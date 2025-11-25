"""
Stripe API Integration
Production-ready payment processing platform integration
"""

import os
import asyncio
import json
import base64
import hashlib
import hmac
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
import httpx
from dataclasses import dataclass

from services.structured_logging import logger
from services.production_secrets_manager import production_secrets_manager
from services.production_tenant_manager import get_tenant_manager

@dataclass
class StripeCustomer:
    """Stripe customer data structure"""
    customer_id: str
    email: str
    name: str
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime
    balance: float
    currency: str
    status: str

@dataclass
class StripePayment:
    """Stripe payment data structure"""
    payment_id: str
    customer_id: str
    amount: float
    currency: str
    status: str
    payment_method: str
    created_at: datetime
    description: str

@dataclass
class StripeSubscription:
    """Stripe subscription data structure"""
    subscription_id: str
    customer_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    amount: float
    currency: str
    created_at: datetime

class StripeClient:
    """Stripe API client with production-ready implementation"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.api_key = credentials.get("api_key")
        self.webhook_secret = credentials.get("webhook_secret")
        self.api_version = "2023-10-16"
        self.base_url = "https://api.stripe.com/v1"
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Stripe-Version": self.api_version,
                "User-Agent": "OmnifyProduct/2.0.0"
            }
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with Stripe API"""
        try:
            response = await self.client.get("/account")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Stripe authentication error: {e}")
            return False
    
    async def get_customers(self, limit: int = 100) -> List[StripeCustomer]:
        """Get Stripe customers"""
        try:
            url = "/customers"
            params = {
                "limit": limit
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            customers = []
            
            for customer_data in data.get("data", []):
                customer = StripeCustomer(
                    customer_id=customer_data.get("id"),
                    email=customer_data.get("email"),
                    name=customer_data.get("name"),
                    phone=customer_data.get("phone"),
                    created_at=datetime.fromtimestamp(customer_data.get("created", 0)),
                    updated_at=datetime.fromtimestamp(customer_data.get("created", 0)),  # Stripe doesn't have updated_at
                    balance=customer_data.get("balance", 0) / 100,  # Convert from cents
                    currency=customer_data.get("currency", "usd"),
                    status="active" if not customer_data.get("deleted") else "deleted"
                )
                customers.append(customer)
            
            logger.info(f"Retrieved {len(customers)} Stripe customers", extra={
                "customer_count": len(customers)
            })
            
            return customers
            
        except Exception as e:
            logger.error(f"Error getting Stripe customers: {e}")
            return []
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Optional[str]:
        """Create Stripe customer"""
        try:
            url = "/customers"
            
            # Prepare customer payload
            payload = {
                "email": customer_data["email"],
                "name": customer_data.get("name"),
                "phone": customer_data.get("phone"),
                "description": customer_data.get("description"),
                "metadata": customer_data.get("metadata", {})
            }
            
            response = await self.client.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            customer_id = result.get("id")
            
            logger.info(f"Created Stripe customer {customer_id}", extra={
                "customer_id": customer_id,
                "email": customer_data["email"]
            })
            
            return customer_id
            
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            return None
    
    async def get_payments(self, customer_id: Optional[str] = None, limit: int = 100) -> List[StripePayment]:
        """Get Stripe payments"""
        try:
            url = "/payment_intents"
            params = {
                "limit": limit
            }
            
            if customer_id:
                params["customer"] = customer_id
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            payments = []
            
            for payment_data in data.get("data", []):
                payment = StripePayment(
                    payment_id=payment_data.get("id"),
                    customer_id=payment_data.get("customer"),
                    amount=payment_data.get("amount", 0) / 100,  # Convert from cents
                    currency=payment_data.get("currency", "usd"),
                    status=payment_data.get("status"),
                    payment_method=payment_data.get("payment_method"),
                    created_at=datetime.fromtimestamp(payment_data.get("created", 0)),
                    description=payment_data.get("description", "")
                )
                payments.append(payment)
            
            logger.info(f"Retrieved {len(payments)} Stripe payments", extra={
                "customer_id": customer_id,
                "payment_count": len(payments)
            })
            
            return payments
            
        except Exception as e:
            logger.error(f"Error getting Stripe payments: {e}")
            return []
    
    async def create_payment(self, payment_data: Dict[str, Any]) -> Optional[str]:
        """Create Stripe payment intent"""
        try:
            url = "/payment_intents"
            
            # Prepare payment payload
            payload = {
                "amount": int(payment_data["amount"] * 100),  # Convert to cents
                "currency": payment_data.get("currency", "usd"),
                "customer": payment_data.get("customer_id"),
                "description": payment_data.get("description"),
                "payment_method": payment_data.get("payment_method"),
                "confirmation_method": payment_data.get("confirmation_method", "automatic"),
                "confirm": payment_data.get("confirm", True),
                "metadata": payment_data.get("metadata", {})
            }
            
            response = await self.client.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            payment_id = result.get("id")
            
            logger.info(f"Created Stripe payment {payment_id}", extra={
                "payment_id": payment_id,
                "amount": payment_data["amount"],
                "currency": payment_data.get("currency", "usd")
            })
            
            return payment_id
            
        except Exception as e:
            logger.error(f"Error creating Stripe payment: {e}")
            return None
    
    async def get_subscriptions(self, customer_id: Optional[str] = None, limit: int = 100) -> List[StripeSubscription]:
        """Get Stripe subscriptions"""
        try:
            url = "/subscriptions"
            params = {
                "limit": limit
            }
            
            if customer_id:
                params["customer"] = customer_id
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            subscriptions = []
            
            for sub_data in data.get("data", []):
                subscription = StripeSubscription(
                    subscription_id=sub_data.get("id"),
                    customer_id=sub_data.get("customer"),
                    status=sub_data.get("status"),
                    current_period_start=datetime.fromtimestamp(sub_data.get("current_period_start", 0)),
                    current_period_end=datetime.fromtimestamp(sub_data.get("current_period_end", 0)),
                    amount=sub_data.get("items", {}).get("data", [{}])[0].get("price", {}).get("unit_amount", 0) / 100,
                    currency=sub_data.get("currency", "usd"),
                    created_at=datetime.fromtimestamp(sub_data.get("created", 0))
                )
                subscriptions.append(subscription)
            
            logger.info(f"Retrieved {len(subscriptions)} Stripe subscriptions", extra={
                "customer_id": customer_id,
                "subscription_count": len(subscriptions)
            })
            
            return subscriptions
            
        except Exception as e:
            logger.error(f"Error getting Stripe subscriptions: {e}")
            return []
    
    async def create_subscription(self, subscription_data: Dict[str, Any]) -> Optional[str]:
        """Create Stripe subscription"""
        try:
            url = "/subscriptions"
            
            # Prepare subscription payload
            payload = {
                "customer": subscription_data["customer_id"],
                "items": [{
                    "price": subscription_data["price_id"],
                    "quantity": subscription_data.get("quantity", 1)
                }],
                "payment_behavior": subscription_data.get("payment_behavior", "default_incomplete"),
                "payment_settings": {
                    "save_default_payment_method": subscription_data.get("save_default_payment_method", True)
                },
                "expand": ["latest_invoice.payment_intent"]
            }
            
            response = await self.client.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            subscription_id = result.get("id")
            
            logger.info(f"Created Stripe subscription {subscription_id}", extra={
                "subscription_id": subscription_id,
                "customer_id": subscription_data["customer_id"]
            })
            
            return subscription_id
            
        except Exception as e:
            logger.error(f"Error creating Stripe subscription: {e}")
            return None
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Optional[str]:
        """Create Stripe invoice"""
        try:
            url = "/invoices"
            
            # Prepare invoice payload
            payload = {
                "customer": invoice_data["customer_id"],
                "description": invoice_data.get("description"),
                "metadata": invoice_data.get("metadata", {}),
                "auto_advance": invoice_data.get("auto_advance", True)
            }
            
            response = await self.client.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            invoice_id = result.get("id")
            
            logger.info(f"Created Stripe invoice {invoice_id}", extra={
                "invoice_id": invoice_id,
                "customer_id": invoice_data["customer_id"]
            })
            
            return invoice_id
            
        except Exception as e:
            logger.error(f"Error creating Stripe invoice: {e}")
            return None
    
    async def add_invoice_item(self, invoice_item_data: Dict[str, Any]) -> Optional[str]:
        """Add item to Stripe invoice"""
        try:
            url = "/invoiceitems"
            
            # Prepare invoice item payload
            payload = {
                "customer": invoice_item_data["customer_id"],
                "amount": int(invoice_item_data["amount"] * 100),  # Convert to cents
                "currency": invoice_item_data.get("currency", "usd"),
                "description": invoice_item_data.get("description"),
                "invoice": invoice_item_data.get("invoice_id")
            }
            
            response = await self.client.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            item_id = result.get("id")
            
            logger.info(f"Added Stripe invoice item {item_id}", extra={
                "item_id": item_id,
                "customer_id": invoice_item_data["customer_id"]
            })
            
            return item_id
            
        except Exception as e:
            logger.error(f"Error adding Stripe invoice item: {e}")
            return None
    
    async def finalize_invoice(self, invoice_id: str) -> bool:
        """Finalize Stripe invoice"""
        try:
            url = f"/invoices/{invoice_id}/finalize"
            
            response = await self.client.post(url)
            response.raise_for_status()
            
            logger.info(f"Finalized Stripe invoice {invoice_id}", extra={
                "invoice_id": invoice_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error finalizing Stripe invoice: {e}")
            return False
    
    async def pay_invoice(self, invoice_id: str) -> bool:
        """Pay Stripe invoice"""
        try:
            url = f"/invoices/{invoice_id}/pay"
            
            response = await self.client.post(url)
            response.raise_for_status()
            
            logger.info(f"Paid Stripe invoice {invoice_id}", extra={
                "invoice_id": invoice_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error paying Stripe invoice: {e}")
            return False
    
    async def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> Optional[str]:
        """Refund Stripe payment"""
        try:
            url = "/refunds"
            
            payload = {
                "payment_intent": payment_id
            }
            
            if amount:
                payload["amount"] = int(amount * 100)  # Convert to cents
            
            response = await self.client.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            refund_id = result.get("id")
            
            logger.info(f"Created Stripe refund {refund_id}", extra={
                "refund_id": refund_id,
                "payment_id": payment_id,
                "amount": amount
            })
            
            return refund_id
            
        except Exception as e:
            logger.error(f"Error creating Stripe refund: {e}")
            return None
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get Stripe account information"""
        try:
            url = "/account"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            account_info = {
                "account_id": data.get("id"),
                "name": data.get("business_profile", {}).get("name"),
                "email": data.get("email"),
                "country": data.get("country"),
                "currency": data.get("default_currency"),
                "charges_enabled": data.get("charges_enabled"),
                "payouts_enabled": data.get("payouts_enabled"),
                "created_at": datetime.fromtimestamp(data.get("created", 0))
            }
            
            logger.info(f"Retrieved Stripe account info", extra={
                "account_id": account_info["account_id"],
                "name": account_info["name"]
            })
            
            return account_info
            
        except Exception as e:
            logger.error(f"Error getting Stripe account info: {e}")
            return {}
    
    async def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            import hmac
            import hashlib
            
            expected_sig = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(f"sha256={expected_sig}", signature)
            
        except Exception as e:
            logger.error(f"Error verifying Stripe webhook: {e}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

class StripeAdapter:
    """Stripe adapter for platform integrations manager"""
    
    def __init__(self):
        self.client = None
        self.credentials = None
    
    async def initialize(self, credentials: Dict[str, Any]):
        """Initialize Stripe client"""
        self.credentials = credentials
        self.client = StripeClient(credentials)
        
        # Test authentication
        is_authenticated = await self.client.authenticate()
        if not is_authenticated:
            raise ValueError("Stripe authentication failed")
        
        logger.info("Stripe adapter initialized successfully")
    
    async def get_customers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get customers"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        customers = await self.client.get_customers(limit)
        return [customer.__dict__ for customer in customers]
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Optional[str]:
        """Create customer"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.create_customer(customer_data)
    
    async def get_payments(self, customer_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get payments"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        payments = await self.client.get_payments(customer_id, limit)
        return [payment.__dict__ for payment in payments]
    
    async def create_payment(self, payment_data: Dict[str, Any]) -> Optional[str]:
        """Create payment"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.create_payment(payment_data)
    
    async def get_subscriptions(self, customer_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get subscriptions"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        subscriptions = await self.client.get_subscriptions(customer_id, limit)
        return [subscription.__dict__ for subscription in subscriptions]
    
    async def create_subscription(self, subscription_data: Dict[str, Any]) -> Optional[str]:
        """Create subscription"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.create_subscription(subscription_data)
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Optional[str]:
        """Create invoice"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.create_invoice(invoice_data)
    
    async def add_invoice_item(self, invoice_item_data: Dict[str, Any]) -> Optional[str]:
        """Add invoice item"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.add_invoice_item(invoice_item_data)
    
    async def finalize_invoice(self, invoice_id: str) -> bool:
        """Finalize invoice"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.finalize_invoice(invoice_id)
    
    async def pay_invoice(self, invoice_id: str) -> bool:
        """Pay invoice"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.pay_invoice(invoice_id)
    
    async def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> Optional[str]:
        """Refund payment"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.refund_payment(payment_id, amount)
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.get_account_info()
    
    async def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        if not self.client:
            raise ValueError("Stripe client not initialized")
        
        return await self.client.verify_webhook(payload, signature)
    
    async def close(self):
        """Close client"""
        if self.client:
            await self.client.close()