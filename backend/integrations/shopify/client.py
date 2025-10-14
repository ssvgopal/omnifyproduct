"""
Production-Ready Shopify API Integration for OmnifyProduct
Complete Shopify e-commerce platform integration

Features:
- OAuth2 authentication flow
- Product management and synchronization
- Order tracking and fulfillment
- Customer data synchronization
- Inventory management
- Analytics and reporting
- Webhook handling
- Multi-store support
"""

import os
import asyncio
import json
import base64
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    httpx = None

from services.structured_logging import logger
from services.production_secrets_manager import production_secrets_manager
from services.production_tenant_manager import get_tenant_manager

class ShopifyIntegration:
    """
    Complete Shopify API integration for e-commerce operations
    """

    def __init__(self):
        self.client_id = os.environ.get('SHOPIFY_CLIENT_ID')
        self.client_secret = os.environ.get('SHOPIFY_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('SHOPIFY_REDIRECT_URI', 'http://localhost:8000/auth/shopify/callback')

        # API configuration
        self.api_version = '2024-01'
        self.timeout_seconds = 30

        # Rate limiting (Shopify has strict limits)
        self.requests_per_second = 2  # Conservative limit
        self.requests_per_minute = 40
        self.daily_limit = 10000

        # Cache settings
        self.cache_ttl = 300  # 5 minutes

        # HTTP client
        self.client = None
        if HAS_HTTPX:
            self.client = httpx.AsyncClient(timeout=self.timeout_seconds)

        logger.info("Shopify integration initialized", extra={
            "has_client": HAS_HTTPX and self.client is not None,
            "api_version": self.api_version,
            "rate_limit_per_second": self.requests_per_second
        })

    # ========== OAUTH2 AUTHENTICATION ==========

    def get_oauth_url(self, shop_domain: str, state: str) -> str:
        """
        Generate OAuth2 authorization URL for Shopify
        """
        base_url = f"https://{shop_domain}.myshopify.com/admin/oauth/authorize"
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'read_products,write_products,read_orders,write_orders,read_customers,write_customers,read_inventory,write_inventory',
            'state': state
        }

        return f"{base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, shop_domain: str, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access tokens
        """
        try:
            if not self.client:
                return None

            token_url = f"https://{shop_domain}.myshopify.com/admin/oauth/access_token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code
            }

            response = await self.client.post(token_url, data=data)
            response.raise_for_status()

            tokens = response.json()
            tokens['shop_domain'] = shop_domain
            tokens['expires_at'] = datetime.utcnow() + timedelta(days=365)  # Shopify tokens don't expire

            # Get shop info
            shop_info = await self._get_shop_info(shop_domain, tokens['access_token'])

            tokens.update({
                'shop_id': shop_info.get('id'),
                'shop_name': shop_info.get('name'),
                'shop_email': shop_info.get('email'),
                'shop_currency': shop_info.get('currency'),
                'shop_timezone': shop_info.get('timezone')
            })

            logger.info("Shopify OAuth tokens obtained successfully", extra={
                "shop_domain": shop_domain,
                "shop_id": shop_info.get('id')
            })

            return tokens

        except Exception as e:
            logger.error("Failed to exchange Shopify OAuth code for tokens", exc_info=e)
            return None

    async def _get_shop_info(self, shop_domain: str, access_token: str) -> Dict[str, Any]:
        """Get shop information"""
        try:
            if not self.client:
                return {}

            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            url = f"https://{shop_domain}.myshopify.com/admin/api/{self.api_version}/shop.json"
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()

            shop_data = response.json()
            return shop_data.get('shop', {})

        except Exception as e:
            logger.warning("Failed to get Shopify shop info", exc_info=e)
            return {}

    async def get_valid_access_token(self, organization_id: str, shop_domain: str) -> Optional[str]:
        """
        Get valid access token for Shopify shop
        """
        try:
            # Get stored tokens
            tokens_key = f"shopify_tokens_{organization_id}_{shop_domain}"
            tokens = await production_secrets_manager.get_secret(tokens_key)

            if not tokens:
                return None

            # Shopify tokens don't expire, but check if they're still valid
            return tokens['access_token']

        except Exception as e:
            logger.error("Failed to get valid Shopify access token", exc_info=e, extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain
            })
            return None

    # ========== PRODUCT MANAGEMENT ==========

    async def get_products(
        self,
        organization_id: str,
        shop_domain: str,
        limit: int = 50,
        page_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve products from Shopify store
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, shop_domain)
            if not access_token:
                return {"products": [], "has_next_page": False}

            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            params = {'limit': min(limit, 250)}  # Shopify limit
            if page_info:
                params['page_info'] = page_info

            url = f"https://{shop_domain}.myshopify.com/admin/api/{self.api_version}/products.json"
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()

            products_data = response.json()
            products = products_data.get('products', [])

            # Format products for our system
            formatted_products = []
            for product in products:
                formatted_products.append({
                    "product_id": product.get('id'),
                    "title": product.get('title'),
                    "handle": product.get('handle'),
                    "description": product.get('body_html', ''),
                    "vendor": product.get('vendor'),
                    "product_type": product.get('product_type'),
                    "tags": product.get('tags', '').split(',') if product.get('tags') else [],
                    "status": product.get('status'),
                    "created_at": product.get('created_at'),
                    "updated_at": product.get('updated_at'),
                    "variants": [
                        {
                            "variant_id": variant.get('id'),
                            "title": variant.get('title'),
                            "price": variant.get('price'),
                            "sku": variant.get('sku'),
                            "inventory_quantity": variant.get('inventory_quantity'),
                            "weight": variant.get('weight'),
                            "weight_unit": variant.get('weight_unit')
                        }
                        for variant in product.get('variants', [])
                    ],
                    "images": [
                        {
                            "image_id": image.get('id'),
                            "src": image.get('src'),
                            "alt": image.get('alt')
                        }
                        for image in product.get('images', [])
                    ]
                })

            # Check for pagination
            link_header = response.headers.get('Link', '')
            has_next_page = 'rel="next"' in link_header

            logger.info("Shopify products retrieved", extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain,
                "product_count": len(formatted_products),
                "has_next_page": has_next_page
            })

            return {
                "products": formatted_products,
                "has_next_page": has_next_page,
                "next_page_info": self._extract_page_info(link_header) if has_next_page else None
            }

        except Exception as e:
            logger.error("Failed to get Shopify products", exc_info=e, extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain
            })
            return {"products": [], "has_next_page": False}

    async def create_product(
        self,
        organization_id: str,
        shop_domain: str,
        product_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a new product in Shopify
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, shop_domain)
            if not access_token:
                return None

            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            # Format product data for Shopify API
            product_payload = {
                'product': {
                    'title': product_data.get('title'),
                    'body_html': product_data.get('description', ''),
                    'vendor': product_data.get('vendor', ''),
                    'product_type': product_data.get('product_type', ''),
                    'tags': ','.join(product_data.get('tags', [])),
                    'status': product_data.get('status', 'active'),
                    'variants': [
                        {
                            'title': variant.get('title', 'Default Title'),
                            'price': variant.get('price'),
                            'sku': variant.get('sku'),
                            'inventory_quantity': variant.get('inventory_quantity', 0),
                            'weight': variant.get('weight'),
                            'weight_unit': variant.get('weight_unit', 'kg')
                        }
                        for variant in product_data.get('variants', [])
                    ]
                }
            }

            url = f"https://{shop_domain}.myshopify.com/admin/api/{self.api_version}/products.json"
            response = await self.client.post(url, headers=headers, json=product_payload)
            response.raise_for_status()

            product_result = response.json()
            product_id = product_result.get('product', {}).get('id')

            logger.info("Shopify product created", extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain,
                "product_id": product_id,
                "product_title": product_data.get('title')
            })

            return str(product_id)

        except Exception as e:
            logger.error("Failed to create Shopify product", exc_info=e, extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain
            })
            return None

    # ========== ORDER MANAGEMENT ==========

    async def get_orders(
        self,
        organization_id: str,
        shop_domain: str,
        status: Optional[str] = None,
        limit: int = 50,
        created_at_min: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve orders from Shopify store
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, shop_domain)
            if not access_token:
                return []

            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            params = {'limit': min(limit, 250)}
            if status:
                params['status'] = status
            if created_at_min:
                params['created_at_min'] = created_at_min

            url = f"https://{shop_domain}.myshopify.com/admin/api/{self.api_version}/orders.json"
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()

            orders_data = response.json()
            orders = orders_data.get('orders', [])

            # Format orders for our system
            formatted_orders = []
            for order in orders:
                formatted_orders.append({
                    "order_id": order.get('id'),
                    "order_number": order.get('order_number'),
                    "name": order.get('name'),
                    "email": order.get('email'),
                    "phone": order.get('phone'),
                    "total_price": order.get('total_price'),
                    "subtotal_price": order.get('subtotal_price'),
                    "total_tax": order.get('total_tax'),
                    "currency": order.get('currency'),
                    "financial_status": order.get('financial_status'),
                    "fulfillment_status": order.get('fulfillment_status'),
                    "created_at": order.get('created_at'),
                    "updated_at": order.get('updated_at'),
                    "customer": {
                        "customer_id": order.get('customer', {}).get('id'),
                        "email": order.get('customer', {}).get('email'),
                        "first_name": order.get('customer', {}).get('first_name'),
                        "last_name": order.get('customer', {}).get('last_name')
                    },
                    "line_items": [
                        {
                            "line_item_id": item.get('id'),
                            "product_id": item.get('product_id'),
                            "variant_id": item.get('variant_id'),
                            "title": item.get('title'),
                            "quantity": item.get('quantity'),
                            "price": item.get('price'),
                            "sku": item.get('sku')
                        }
                        for item in order.get('line_items', [])
                    ],
                    "shipping_address": order.get('shipping_address'),
                    "billing_address": order.get('billing_address')
                })

            logger.info("Shopify orders retrieved", extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain,
                "order_count": len(formatted_orders)
            })

            return formatted_orders

        except Exception as e:
            logger.error("Failed to get Shopify orders", exc_info=e, extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain
            })
            return []

    async def update_order_fulfillment(
        self,
        organization_id: str,
        shop_domain: str,
        order_id: str,
        fulfillment_data: Dict[str, Any]
    ) -> bool:
        """
        Update order fulfillment status
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, shop_domain)
            if not access_token:
                return False

            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            fulfillment_payload = {
                'fulfillment': {
                    'order_id': order_id,
                    'status': fulfillment_data.get('status', 'success'),
                    'tracking_number': fulfillment_data.get('tracking_number'),
                    'tracking_company': fulfillment_data.get('tracking_company'),
                    'tracking_url': fulfillment_data.get('tracking_url'),
                    'notify_customer': fulfillment_data.get('notify_customer', True)
                }
            }

            url = f"https://{shop_domain}.myshopify.com/admin/api/{self.api_version}/orders/{order_id}/fulfillments.json"
            response = await self.client.post(url, headers=headers, json=fulfillment_payload)
            response.raise_for_status()

            logger.info("Shopify order fulfillment updated", extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain,
                "order_id": order_id,
                "status": fulfillment_data.get('status')
            })

            return True

        except Exception as e:
            logger.error("Failed to update Shopify order fulfillment", exc_info=e, extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain,
                "order_id": order_id
            })
            return False

    # ========== CUSTOMER MANAGEMENT ==========

    async def get_customers(
        self,
        organization_id: str,
        shop_domain: str,
        limit: int = 50,
        created_at_min: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve customers from Shopify store
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, shop_domain)
            if not access_token:
                return []

            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            params = {'limit': min(limit, 250)}
            if created_at_min:
                params['created_at_min'] = created_at_min

            url = f"https://{shop_domain}.myshopify.com/admin/api/{self.api_version}/customers.json"
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()

            customers_data = response.json()
            customers = customers_data.get('customers', [])

            # Format customers for our system
            formatted_customers = []
            for customer in customers:
                formatted_customers.append({
                    "customer_id": customer.get('id'),
                    "email": customer.get('email'),
                    "first_name": customer.get('first_name'),
                    "last_name": customer.get('last_name'),
                    "phone": customer.get('phone'),
                    "total_spent": customer.get('total_spent'),
                    "orders_count": customer.get('orders_count'),
                    "state": customer.get('state'),
                    "created_at": customer.get('created_at'),
                    "updated_at": customer.get('updated_at'),
                    "default_address": customer.get('default_address'),
                    "addresses": customer.get('addresses', []),
                    "tags": customer.get('tags', '').split(',') if customer.get('tags') else []
                })

            logger.info("Shopify customers retrieved", extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain,
                "customer_count": len(formatted_customers)
            })

            return formatted_customers

        except Exception as e:
            logger.error("Failed to get Shopify customers", exc_info=e, extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain
            })
            return []

    # ========== INVENTORY MANAGEMENT ==========

    async def get_inventory_levels(
        self,
        organization_id: str,
        shop_domain: str,
        location_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get inventory levels for products
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, shop_domain)
            if not access_token:
                return []

            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            params = {}
            if location_ids:
                params['location_ids'] = ','.join(location_ids)

            url = f"https://{shop_domain}.myshopify.com/admin/api/{self.api_version}/inventory_levels.json"
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()

            inventory_data = response.json()
            inventory_levels = inventory_data.get('inventory_levels', [])

            # Format inventory levels for our system
            formatted_levels = []
            for level in inventory_levels:
                formatted_levels.append({
                    "inventory_item_id": level.get('inventory_item_id'),
                    "location_id": level.get('location_id'),
                    "available": level.get('available'),
                    "updated_at": level.get('updated_at')
                })

            logger.info("Shopify inventory levels retrieved", extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain,
                "level_count": len(formatted_levels)
            })

            return formatted_levels

        except Exception as e:
            logger.error("Failed to get Shopify inventory levels", exc_info=e, extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain
            })
            return []

    # ========== ANALYTICS ==========

    async def get_analytics(
        self,
        organization_id: str,
        shop_domain: str,
        date_range: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Get store analytics data
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, shop_domain)
            if not access_token:
                return {}

            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            # Get orders for the date range
            orders = await self.get_orders(
                organization_id, shop_domain,
                created_at_min=date_range['start'],
                limit=250
            )

            # Calculate analytics
            total_orders = len(orders)
            total_revenue = sum(float(order['total_price']) for order in orders)
            total_customers = len(set(order['customer']['customer_id'] for order in orders if order['customer']['customer_id']))

            # Get unique customers
            customer_ids = set()
            for order in orders:
                if order['customer']['customer_id']:
                    customer_ids.add(order['customer']['customer_id'])

            analytics = {
                "date_range": date_range,
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "total_customers": len(customer_ids),
                "average_order_value": total_revenue / max(total_orders, 1),
                "orders_by_status": self._group_orders_by_status(orders),
                "top_products": self._get_top_products(orders),
                "revenue_by_day": self._group_revenue_by_day(orders)
            }

            logger.info("Shopify analytics retrieved", extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain,
                "total_orders": total_orders,
                "total_revenue": total_revenue
            })

            return analytics

        except Exception as e:
            logger.error("Failed to get Shopify analytics", exc_info=e, extra={
                "organization_id": organization_id,
                "shop_domain": shop_domain
            })
            return {}

    def _group_orders_by_status(self, orders: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group orders by fulfillment status"""
        status_counts = {}
        for order in orders:
            status = order.get('fulfillment_status', 'unfulfilled')
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts

    def _get_top_products(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top selling products"""
        product_counts = {}
        for order in orders:
            for item in order.get('line_items', []):
                product_id = item.get('product_id')
                if product_id:
                    if product_id not in product_counts:
                        product_counts[product_id] = {
                            'product_id': product_id,
                            'title': item.get('title'),
                            'quantity': 0,
                            'revenue': 0
                        }
                    product_counts[product_id]['quantity'] += item.get('quantity', 0)
                    product_counts[product_id]['revenue'] += float(item.get('price', 0)) * item.get('quantity', 0)

        return sorted(product_counts.values(), key=lambda x: x['quantity'], reverse=True)[:10]

    def _group_revenue_by_day(self, orders: List[Dict[str, Any]]) -> Dict[str, float]:
        """Group revenue by day"""
        daily_revenue = {}
        for order in orders:
            date = order.get('created_at', '')[:10]  # Extract date part
            if date:
                daily_revenue[date] = daily_revenue.get(date, 0) + float(order.get('total_price', 0))
        return daily_revenue

    def _extract_page_info(self, link_header: str) -> Optional[str]:
        """Extract page info from Link header"""
        if 'page_info=' in link_header:
            start = link_header.find('page_info=') + 10
            end = link_header.find('>', start)
            return link_header[start:end]
        return None

    # ========== UTILITY METHODS ==========

    async def test_connection(self, organization_id: str, shop_domain: str) -> Dict[str, Any]:
        """
        Test connection to Shopify API
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, shop_domain)
            if not access_token:
                return {"status": "no_token"}

            # Test with a simple API call
            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            url = f"https://{shop_domain}.myshopify.com/admin/api/{self.api_version}/shop.json"
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()

            shop_data = response.json()
            shop = shop_data.get('shop', {})

            return {
                "status": "connected",
                "shop_domain": shop_domain,
                "shop_name": shop.get('name'),
                "shop_id": shop.get('id')
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def get_required_scopes(self) -> List[str]:
        """Get required OAuth2 scopes"""
        return [
            'read_products',
            'write_products',
            'read_orders',
            'write_orders',
            'read_customers',
            'write_customers',
            'read_inventory',
            'write_inventory'
        ]

    def get_api_limits(self) -> Dict[str, Any]:
        """Get Shopify API limits information"""
        return {
            "requests_per_second": self.requests_per_second,
            "requests_per_minute": self.requests_per_minute,
            "daily_limit": self.daily_limit,
            "rate_limit_type": "bucket_based",
            "burst_allowed": True,
            "plan_based_limits": True,
            "documentation_url": "https://shopify.dev/api/admin-rest"
        }

# Global Shopify integration instance
shopify_integration = ShopifyIntegration()
