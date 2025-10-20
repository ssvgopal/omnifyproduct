"""
Open Policy Agent (OPA) Integration
Enterprise-grade policy engine for RBAC/ABAC authorization
"""

import os
import httpx
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException, status, Depends
from pydantic import BaseModel

from services.oidc_auth import TokenValidationResult, get_current_user

logger = logging.getLogger(__name__)

class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"

class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class PolicyContext:
    """Context for policy evaluation"""
    user_id: str
    organization_id: str
    email: str
    roles: List[str]
    permissions: List[str]
    resource: str
    action: str
    resource_attributes: Dict[str, Any]
    environment: Dict[str, Any]

class PolicyRule(BaseModel):
    """Policy rule definition"""
    name: str
    effect: PolicyEffect
    conditions: List[Dict[str, Any]]
    description: Optional[str] = None

class PolicyEvaluationResult(BaseModel):
    """Policy evaluation result"""
    decision: PolicyDecision
    reason: str
    policies_applied: List[str]
    context: Dict[str, Any]
    timestamp: datetime

class OPAClient:
    """
    Open Policy Agent (OPA) client for policy evaluation
    """

    def __init__(self):
        self.enable_opa = os.getenv("ENABLE_OPA", "false").lower() == "true"
        self.opa_url = os.getenv("OPA_URL", "http://opa:8181")
        self.policy_package = os.getenv("OPA_POLICY_PACKAGE", "omnify.authz")
        self.timeout = int(os.getenv("OPA_TIMEOUT", "5"))
        
        # HTTP client for OPA
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            base_url=self.opa_url
        )

        # Fallback policies (when OPA is disabled)
        self.fallback_policies = self._load_fallback_policies()

        logger.info(f"OPA Client initialized", extra={
            "enabled": self.enable_opa,
            "opa_url": self.opa_url,
            "policy_package": self.policy_package
        })

    def _load_fallback_policies(self) -> Dict[str, PolicyRule]:
        """Load fallback policies when OPA is disabled"""
        return {
            "admin_full_access": PolicyRule(
                name="admin_full_access",
                effect=PolicyEffect.ALLOW,
                conditions=[
                    {"role": "admin"}
                ],
                description="Admin users have full access to all resources"
            ),
            "manager_org_access": PolicyRule(
                name="manager_org_access",
                effect=PolicyEffect.ALLOW,
                conditions=[
                    {"role": "manager"},
                    {"resource_scope": "organization"}
                ],
                description="Managers can access organization-scoped resources"
            ),
            "user_campaign_access": PolicyRule(
                name="user_campaign_access",
                effect=PolicyEffect.ALLOW,
                conditions=[
                    {"role": "user"},
                    {"resource": "campaigns"},
                    {"action": ["read", "write"]}
                ],
                description="Users can read and write campaigns"
            ),
            "viewer_read_only": PolicyRule(
                name="viewer_read_only",
                effect=PolicyEffect.ALLOW,
                conditions=[
                    {"role": "viewer"},
                    {"action": "read"}
                ],
                description="Viewers have read-only access"
            ),
            "deny_delete_unless_admin": PolicyRule(
                name="deny_delete_unless_admin",
                effect=PolicyEffect.DENY,
                conditions=[
                    {"action": "delete"},
                    {"role": {"not": "admin"}}
                ],
                description="Only admins can delete resources"
            )
        }

    async def evaluate_policy(
        self,
        context: PolicyContext,
        policy_name: Optional[str] = None
    ) -> PolicyEvaluationResult:
        """
        Evaluate policy using OPA or fallback rules
        """
        try:
            if self.enable_opa:
                return await self._evaluate_with_opa(context, policy_name)
            else:
                return await self._evaluate_fallback(context, policy_name)

        except Exception as e:
            logger.error(f"Policy evaluation failed: {str(e)}")
            # Fail secure - deny access on error
            return PolicyEvaluationResult(
                decision=PolicyDecision.DENY,
                reason=f"Policy evaluation error: {str(e)}",
                policies_applied=[],
                context=context.__dict__,
                timestamp=datetime.utcnow()
            )

    async def _evaluate_with_opa(
        self,
        context: PolicyContext,
        policy_name: Optional[str] = None
    ) -> PolicyEvaluationResult:
        """Evaluate policy using OPA server"""
        try:
            # Prepare input for OPA
            input_data = {
                "user": {
                    "id": context.user_id,
                    "organization_id": context.organization_id,
                    "email": context.email,
                    "roles": context.roles,
                    "permissions": context.permissions
                },
                "resource": {
                    "name": context.resource,
                    "action": context.action,
                    "attributes": context.resource_attributes
                },
                "environment": context.environment
            }

            # Determine policy path
            if policy_name:
                policy_path = f"/v1/data/{self.policy_package}/{policy_name}"
            else:
                policy_path = f"/v1/data/{self.policy_package}/allow"

            # Make request to OPA
            response = await self.http_client.post(
                policy_path,
                json={"input": input_data}
            )

            if response.status_code == 200:
                result = response.json()
                decision = PolicyDecision.ALLOW if result.get("result", False) else PolicyDecision.DENY
                
                return PolicyEvaluationResult(
                    decision=decision,
                    reason=f"OPA policy evaluation: {policy_name or 'default'}",
                    policies_applied=[policy_name or "default"],
                    context=context.__dict__,
                    timestamp=datetime.utcnow()
                )
            else:
                logger.error(f"OPA request failed: {response.status_code} - {response.text}")
                return PolicyEvaluationResult(
                    decision=PolicyDecision.DENY,
                    reason=f"OPA request failed: {response.status_code}",
                    policies_applied=[],
                    context=context.__dict__,
                    timestamp=datetime.utcnow()
                )

        except httpx.TimeoutException:
            logger.error("OPA request timeout")
            return PolicyEvaluationResult(
                decision=PolicyDecision.DENY,
                reason="OPA request timeout",
                policies_applied=[],
                context=context.__dict__,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"OPA evaluation error: {str(e)}")
            return PolicyEvaluationResult(
                decision=PolicyDecision.DENY,
                reason=f"OPA error: {str(e)}",
                policies_applied=[],
                context=context.__dict__,
                timestamp=datetime.utcnow()
            )

    async def _evaluate_fallback(
        self,
        context: PolicyContext,
        policy_name: Optional[str] = None
    ) -> PolicyEvaluationResult:
        """Evaluate policy using fallback rules"""
        applied_policies = []
        
        # Check each fallback policy
        for rule_name, rule in self.fallback_policies.items():
            if self._evaluate_rule(rule, context):
                applied_policies.append(rule_name)
                
                # If it's a DENY rule and it matches, deny access
                if rule.effect == PolicyEffect.DENY:
                    return PolicyEvaluationResult(
                        decision=PolicyDecision.DENY,
                        reason=f"Fallback policy denied: {rule_name}",
                        policies_applied=applied_policies,
                        context=context.__dict__,
                        timestamp=datetime.utcnow()
                    )

        # If any ALLOW rule matched, allow access
        if applied_policies:
            return PolicyEvaluationResult(
                decision=PolicyDecision.ALLOW,
                reason=f"Fallback policies allowed: {', '.join(applied_policies)}",
                policies_applied=applied_policies,
                context=context.__dict__,
                timestamp=datetime.utcnow()
            )

        # Default deny
        return PolicyEvaluationResult(
            decision=PolicyDecision.DENY,
            reason="No matching policies found",
            policies_applied=[],
            context=context.__dict__,
            timestamp=datetime.utcnow()
        )

    def _evaluate_rule(self, rule: PolicyRule, context: PolicyContext) -> bool:
        """Evaluate a single policy rule"""
        for condition in rule.conditions:
            if not self._evaluate_condition(condition, context):
                return False
        return True

    def _evaluate_condition(self, condition: Dict[str, Any], context: PolicyContext) -> bool:
        """Evaluate a single condition"""
        for key, expected_value in condition.items():
            if key == "role":
                if isinstance(expected_value, str):
                    if expected_value not in context.roles:
                        return False
                elif isinstance(expected_value, dict) and "not" in expected_value:
                    if expected_value["not"] in context.roles:
                        return False
                else:
                    if not any(role in context.roles for role in expected_value):
                        return False

            elif key == "permission":
                if expected_value not in context.permissions:
                    return False

            elif key == "resource":
                if isinstance(expected_value, str):
                    if context.resource != expected_value:
                        return False
                elif isinstance(expected_value, list):
                    if context.resource not in expected_value:
                        return False

            elif key == "action":
                if isinstance(expected_value, str):
                    if context.action != expected_value:
                        return False
                elif isinstance(expected_value, list):
                    if context.action not in expected_value:
                        return False

            elif key == "resource_scope":
                if expected_value not in context.resource_attributes.get("scope", []):
                    return False

            elif key == "organization_id":
                if context.organization_id != expected_value:
                    return False

        return True

    async def health_check(self) -> Dict[str, Any]:
        """Health check for OPA service"""
        try:
            if self.enable_opa:
                # Test OPA connectivity
                response = await self.http_client.get("/health")
                opa_status = "healthy" if response.status_code == 200 else "unhealthy"
            else:
                opa_status = "disabled"

            return {
                "status": "healthy",
                "opa_enabled": self.enable_opa,
                "opa_status": opa_status,
                "fallback_policies": len(self.fallback_policies),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"OPA health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()

# Global instance
opa_client = OPAClient()

# Policy evaluation dependency
async def evaluate_access_policy(
    resource: str,
    action: str,
    resource_attributes: Dict[str, Any] = None,
    environment: Dict[str, Any] = None,
    policy_name: Optional[str] = None,
    current_user: TokenValidationResult = Depends(get_current_user)
) -> PolicyEvaluationResult:
    """
    FastAPI dependency to evaluate access policy
    """
    context = PolicyContext(
        user_id=current_user.user_id,
        organization_id=current_user.organization_id,
        email=current_user.email,
        roles=current_user.roles,
        permissions=current_user.permissions,
        resource=resource,
        action=action,
        resource_attributes=resource_attributes or {},
        environment=environment or {}
    )

    result = await opa_client.evaluate_policy(context, policy_name)
    
    if result.decision == PolicyDecision.DENY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: {result.reason}"
        )

    return result

# Convenience decorators for common policies
def require_resource_access(resource: str, action: str):
    """Decorator to require access to a specific resource and action"""
    async def access_checker(current_user: TokenValidationResult = Depends(get_current_user)):
        await evaluate_access_policy(resource, action, current_user=current_user)
        return current_user
    return access_checker

def require_organization_access():
    """Decorator to require organization-level access"""
    async def org_checker(current_user: TokenValidationResult = Depends(get_current_user)):
        await evaluate_access_policy("organization", "read", current_user=current_user)
        return current_user
    return org_checker

def require_admin_access():
    """Decorator to require admin access"""
    async def admin_checker(current_user: TokenValidationResult = Depends(get_current_user)):
        await evaluate_access_policy("admin", "full_access", current_user=current_user)
        return current_user
    return admin_checker
