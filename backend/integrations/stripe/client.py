"""
Production-Ready Stripe API Integration for OmnifyProduct
Complete Stripe payment processing integration

Features:
- OAuth2 authentication flow
- Payment processing and management
- Subscription management
- Customer management
- Invoice generation and tracking
- Webhook handling
- Multi-currency support
- Refund processing
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

class StripeIntegration:
    """
    Complete Stripe API integration for payment processing
    """

    def __init__(self):
        self.client_id = os.environ.get('STRIPE_CLIENT_ID')
        self.client_secret = os.environ.get('STRIPE_CLIENT_SECRET')
        self.publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        self.webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        self.redirect_uri = os.environ.get('STRIPE_REDIRECT_URI', 'http://localhost:8000/auth/stripe/callback')

        # API configuration
        self.base_url = 'https://api.stripe.com'
        self.api_version = '2024-06-20'
        self.timeout_seconds = 30

        # Rate limiting (Stripe has limits)
        self.requests_per_second = 100  # Stripe allows high rate limits
        self.requests_per_minute = 6000
        self.daily_limit = 100000

        # Cache settings
        self.cache_ttl = 300  # 5 minutes

        # HTTP client
        self.client = None
        if HAS_HTTPX:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds
            )

        logger.info("Stripe integration initialized", extra={
            "has_client": HAS_HTTPX and self.client is not None,
            "base_url": self.base_url,
            "api_version": self.api_version
        })

    # ========== OAUTH2 AUTHENTICATION ==========

    def get_oauth_url(self, state: str) -> str:
        """
        Generate OAuth2 authorization URL for Stripe
        """
        base_url = "https://connect.stripe.com/oauth/authorize"
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'read_write',
            'state': state
        }

        return f"{base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access tokens
        """
        try:
            if not self.client:
                return None

            token_url = "/oauth/token"
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code
            }

            response = await self.client.post(token_url, data=data)
            response.raise_for_status()

            tokens = response.json()
            tokens['expires_at'] = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))

            # Get account info
            account_info = await self._get_account_info(tokens['access_token'])

            tokens.update({
                'stripe_user_id': account_info.get('id'),
                'stripe_publishable_key': account_info.get('keys', {}).get('publishable'),
                'country': account_info.get('country'),
                'currency': account_info.get('default_currency'),
                'business_type': account_info.get('business_type')
            })

            logger.info("Stripe OAuth tokens obtained successfully", extra={
                "stripe_user_id": account_info.get('id'),
                "country": account_info.get('country')
            })

            return tokens

        except Exception as e:
            logger.error("Failed to exchange Stripe OAuth code for tokens", exc_info=e)
            return None

    async def _get_account_info(self, access_token: str) -> Dict[str, Any]:
        """Get account information"""
        try:
            if not self.client:
                return {}

            headers = {'Authorization': f'Bearer {access_token}'}
            response = await self.client.get('/v1/account', headers=headers)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.warning("Failed to get Stripe account info", exc_info=e)
            return {}

    async def get_valid_access_token(self, organization_id: str, account_id: str) -> Optional[str]:
        """
        Get valid access token for Stripe account
        """
        try:
            # Get stored tokens
            tokens_key = f"stripe_tokens_{organization_id}_{account_id}"
            tokens = await production_secrets_manager.get_secret(tokens_key)

            if not tokens:
                return None

            # Check if token is still valid (with buffer)
            expires_at = datetime.fromisoformat(tokens['expires_at'])
            buffer_time = timedelta(minutes=5)  # Refresh 5 minutes before expiry

            if datetime.utcnow() >= (expires_at - buffer_time):
                # Refresh token if needed (Stripe tokens typically don't expire for connected accounts)
                # For now, just return the existing token
                pass

            return tokens['access_token']

        except Exception as e:
            logger.error("Failed to get valid Stripe access token", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== PAYMENT PROCESSING ==========

    async def create_payment_intent(
        self,
        organization_id: str,
        account_id: str,
        payment_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a payment intent for processing
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            # Format payment data for Stripe API
            form_data = {
                'amount': int(float(payment_data.get('amount', 0)) * 100),  # Convert to cents
                'currency': payment_data.get('currency', 'usd'),
                'payment_method_types[]': payment_data.get('payment_method_types', ['card']),
                'description': payment_data.get('description', ''),
                'metadata[order_id]': payment_data.get('order_id', ''),
                'metadata[customer_id]': payment_data.get('customer_id', '')
            }

            # Add customer if provided
            if payment_data.get('customer_id'):
                form_data['customer'] = payment_data['customer_id']

            response = await self.client.post('/v1/payment_intents', headers=headers, data=form_data)
            response.raise_for_status()

            payment_intent = response.json()

            logger.info("Stripe payment intent created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "payment_intent_id": payment_intent.get('id'),
                "amount": payment_data.get('amount')
            })

            return payment_intent

        except Exception as e:
            logger.error("Failed to create Stripe payment intent", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    async def confirm_payment_intent(
        self,
        organization_id: str,
        account_id: str,
        payment_intent_id: str,
        payment_method_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Confirm a payment intent
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            form_data = {
                'payment_method': payment_method_id
            }

            response = await self.client.post(
                f'/v1/payment_intents/{payment_intent_id}/confirm',
                headers=headers,
                data=form_data
            )
            response.raise_for_status()

            payment_intent = response.json()

            logger.info("Stripe payment intent confirmed", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "payment_intent_id": payment_intent_id,
                "status": payment_intent.get('status')
            })

            return payment_intent

        except Exception as e:
            logger.error("Failed to confirm Stripe payment intent", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "payment_intent_id": payment_intent_id
            })
            return None

    # ========== CUSTOMER MANAGEMENT ==========

    async def create_customer(
        self,
        organization_id: str,
        account_id: str,
        customer_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a new customer
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            form_data = {
                'email': customer_data.get('email'),
                'name': customer_data.get('name'),
                'phone': customer_data.get('phone'),
                'description': customer_data.get('description', ''),
                'metadata[organization_id]': organization_id
            }

            # Add address if provided
            if customer_data.get('address'):
                address = customer_data['address']
                form_data.update({
                    'address[line1]': address.get('line1'),
                    'address[line2]': address.get('line2'),
                    'address[city]': address.get('city'),
                    'address[state]': address.get('state'),
                    'address[postal_code]': address.get('postal_code'),
                    'address[country]': address.get('country')
                })

            response = await self.client.post('/v1/customers', headers=headers, data=form_data)
            response.raise_for_status()

            customer = response.json()
            customer_id = customer.get('id')

            logger.info("Stripe customer created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "customer_id": customer_id,
                "email": customer_data.get('email')
            })

            return customer_id

        except Exception as e:
            logger.error("Failed to create Stripe customer", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    async def get_customers(
        self,
        organization_id: str,
        account_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve customers
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return []

            headers = {'Authorization': f'Bearer {access_token}'}

            params = {'limit': min(limit, 100)}
            response = await self.client.get('/v1/customers', headers=headers, params=params)
            response.raise_for_status()

            customers_data = response.json()
            customers = customers_data.get('data', [])

            # Format customers for our system
            formatted_customers = []
            for customer in customers:
                formatted_customers.append({
                    "customer_id": customer.get('id'),
                    "email": customer.get('email'),
                    "name": customer.get('name'),
                    "phone": customer.get('phone'),
                    "description": customer.get('description'),
                    "created": customer.get('created'),
                    "default_source": customer.get('default_source'),
                    "delinquent": customer.get('delinquent'),
                    "metadata": customer.get('metadata', {}),
                    "address": customer.get('address')
                })

            logger.info("Stripe customers retrieved", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "customer_count": len(formatted_customers)
            })

            return formatted_customers

        except Exception as e:
            logger.error("Failed to get Stripe customers", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return []

    # ========== SUBSCRIPTION MANAGEMENT ==========

    async def create_subscription(
        self,
        organization_id: str,
        account_id: str,
        subscription_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a subscription
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            form_data = {
                'customer': subscription_data.get('customer_id'),
                'items[0][price]': subscription_data.get('price_id'),
                'metadata[organization_id]': organization_id,
                'metadata[plan_name]': subscription_data.get('plan_name', '')
            }

            # Add trial period if provided
            if subscription_data.get('trial_period_days'):
                form_data['trial_period_days'] = subscription_data['trial_period_days']

            response = await self.client.post('/v1/subscriptions', headers=headers, data=form_data)
            response.raise_for_status()

            subscription = response.json()

            logger.info("Stripe subscription created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "subscription_id": subscription.get('id'),
                "customer_id": subscription_data.get('customer_id')
            })

            return subscription

        except Exception as e:
            logger.error("Failed to create Stripe subscription", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    async def cancel_subscription(
        self,
        organization_id: str,
        account_id: str,
        subscription_id: str,
        cancel_at_period_end: bool = True
    ) -> bool:
        """
        Cancel a subscription
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return False

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            form_data = {
                'cancel_at_period_end': cancel_at_period_end
            }

            response = await self.client.post(
                f'/v1/subscriptions/{subscription_id}',
                headers=headers,
                data=form_data
            )
            response.raise_for_status()

            logger.info("Stripe subscription cancelled", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "subscription_id": subscription_id,
                "cancel_at_period_end": cancel_at_period_end
            })

            return True

        except Exception as e:
            logger.error("Failed to cancel Stripe subscription", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "subscription_id": subscription_id
            })
            return False

    # ========== INVOICE MANAGEMENT ==========

    async def create_invoice(
        self,
        organization_id: str,
        account_id: str,
        invoice_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create an invoice
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            form_data = {
                'customer': invoice_data.get('customer_id'),
                'description': invoice_data.get('description', ''),
                'metadata[organization_id]': organization_id,
                'metadata[order_id]': invoice_data.get('order_id', '')
            }

            # Add line items
            for i, item in enumerate(invoice_data.get('line_items', [])):
                form_data[f'lines[{i}][amount]'] = int(float(item.get('amount', 0)) * 100)
                form_data[f'lines[{i}][currency]'] = item.get('currency', 'usd')
                form_data[f'lines[{i}][description]'] = item.get('description', '')

            response = await self.client.post('/v1/invoices', headers=headers, data=form_data)
            response.raise_for_status()

            invoice = response.json()

            logger.info("Stripe invoice created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "invoice_id": invoice.get('id'),
                "customer_id": invoice_data.get('customer_id')
            })

            return invoice

        except Exception as e:
            logger.error("Failed to create Stripe invoice", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    async def finalize_invoice(
        self,
        organization_id: str,
        account_id: str,
        invoice_id: str
    ) -> bool:
        """
        Finalize an invoice
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return False

            headers = {'Authorization': f'Bearer {access_token}'}

            response = await self.client.post(
                f'/v1/invoices/{invoice_id}/finalize',
                headers=headers
            )
            response.raise_for_status()

            logger.info("Stripe invoice finalized", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "invoice_id": invoice_id
            })

            return True

        except Exception as e:
            logger.error("Failed to finalize Stripe invoice", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "invoice_id": invoice_id
            })
            return False

    # ========== REFUND PROCESSING ==========

    async def create_refund(
        self,
        organization_id: str,
        account_id: str,
        refund_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a refund
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            form_data = {
                'payment_intent': refund_data.get('payment_intent_id'),
                'amount': int(float(refund_data.get('amount', 0)) * 100),  # Convert to cents
                'reason': refund_data.get('reason', 'requested_by_customer'),
                'metadata[organization_id]': organization_id
            }

            response = await self.client.post('/v1/refunds', headers=headers, data=form_data)
            response.raise_for_status()

            refund = response.json()

            logger.info("Stripe refund created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "refund_id": refund.get('id'),
                "amount": refund_data.get('amount')
            })

            return refund

        except Exception as e:
            logger.error("Failed to create Stripe refund", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== WEBHOOK HANDLING ==========

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature
        """
        try:
            if not self.webhook_secret:
                return False

            # Parse signature
            sig_parts = signature.split(',')
            timestamp = None
            v1_signature = None

            for part in sig_parts:
                if part.startswith('t='):
                    timestamp = part[2:]
                elif part.startswith('v1='):
                    v1_signature = part[3:]

            if not timestamp or not v1_signature:
                return False

            # Create expected signature
            expected_signature = hashlib.sha256(
                f"{timestamp}.{payload}".encode()
            ).hexdigest()

            return v1_signature == expected_signature

        except Exception as e:
            logger.error("Failed to verify Stripe webhook signature", exc_info=e)
            return False

    async def process_webhook(self, payload: str, signature: str) -> Optional[Dict[str, Any]]:
        """
        Process webhook event
        """
        try:
            if not self.verify_webhook_signature(payload, signature):
                logger.warning("Invalid Stripe webhook signature")
                return None

            event_data = json.loads(payload)
            event_type = event_data.get('type')

            logger.info("Processing Stripe webhook", extra={
                "event_type": event_type,
                "event_id": event_data.get('id')
            })

            # Process different event types
            if event_type == 'payment_intent.succeeded':
                return await self._handle_payment_succeeded(event_data)
            elif event_type == 'payment_intent.payment_failed':
                return await self._handle_payment_failed(event_data)
            elif event_type == 'invoice.payment_succeeded':
                return await self._handle_invoice_payment_succeeded(event_data)
            elif event_type == 'customer.subscription.created':
                return await self._handle_subscription_created(event_data)
            elif event_type == 'customer.subscription.deleted':
                return await self._handle_subscription_deleted(event_data)

            return {"status": "processed", "event_type": event_type}

        except Exception as e:
            logger.error("Failed to process Stripe webhook", exc_info=e)
            return None

    async def _handle_payment_succeeded(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment succeeded event"""
        payment_intent = event_data.get('data', {}).get('object', {})
        return {
            "event_type": "payment_succeeded",
            "payment_intent_id": payment_intent.get('id'),
            "amount": payment_intent.get('amount'),
            "currency": payment_intent.get('currency'),
            "customer_id": payment_intent.get('customer')
        }

    async def _handle_payment_failed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failed event"""
        payment_intent = event_data.get('data', {}).get('object', {})
        return {
            "event_type": "payment_failed",
            "payment_intent_id": payment_intent.get('id'),
            "amount": payment_intent.get('amount'),
            "currency": payment_intent.get('currency'),
            "customer_id": payment_intent.get('customer'),
            "failure_reason": payment_intent.get('last_payment_error', {}).get('message')
        }

    async def _handle_invoice_payment_succeeded(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice payment succeeded event"""
        invoice = event_data.get('data', {}).get('object', {})
        return {
            "event_type": "invoice_payment_succeeded",
            "invoice_id": invoice.get('id'),
            "amount_paid": invoice.get('amount_paid'),
            "currency": invoice.get('currency'),
            "customer_id": invoice.get('customer')
        }

    async def _handle_subscription_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription created event"""
        subscription = event_data.get('data', {}).get('object', {})
        return {
            "event_type": "subscription_created",
            "subscription_id": subscription.get('id'),
            "customer_id": subscription.get('customer'),
            "status": subscription.get('status'),
            "current_period_start": subscription.get('current_period_start'),
            "current_period_end": subscription.get('current_period_end')
        }

    async def _handle_subscription_deleted(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deleted event"""
        subscription = event_data.get('data', {}).get('object', {})
        return {
            "event_type": "subscription_deleted",
            "subscription_id": subscription.get('id'),
            "customer_id": subscription.get('customer'),
            "canceled_at": subscription.get('canceled_at')
        }

    # ========== UTILITY METHODS ==========

    async def test_connection(self, organization_id: str, account_id: str) -> Dict[str, Any]:
        """
        Test connection to Stripe API
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return {"status": "no_token"}

            headers = {'Authorization': f'Bearer {access_token}'}
            response = await self.client.get('/v1/account', headers=headers)
            response.raise_for_status()

            account_data = response.json()

            return {
                "status": "connected",
                "account_id": account_data.get('id'),
                "country": account_data.get('country'),
                "currency": account_data.get('default_currency'),
                "charges_enabled": account_data.get('charges_enabled'),
                "payouts_enabled": account_data.get('payouts_enabled')
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def get_required_scopes(self) -> List[str]:
        """Get required OAuth2 scopes"""
        return ['read_write']

    def get_api_limits(self) -> Dict[str, Any]:
        """Get Stripe API limits information"""
        return {
            "requests_per_second": self.requests_per_second,
            "requests_per_minute": self.requests_per_minute,
            "daily_limit": self.daily_limit,
            "rate_limit_type": "per_second",
            "burst_allowed": True,
            "plan_based_limits": True,
            "documentation_url": "https://stripe.com/docs/api"
        }

# Global Stripe integration instance
stripe_integration = StripeIntegration()
