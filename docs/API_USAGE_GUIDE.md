# OmnifyProduct API Usage Guide

## 📖 **Complete API Reference**

This guide provides comprehensive documentation for using the OmnifyProduct API, including all endpoints, request/response formats, and practical examples.

---

## **Authentication** 🔐

All API endpoints require JWT authentication. Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer your-jwt-token" \
     https://api.omnifyproduct.com/api/agentkit/agents
```

### **Getting Authentication Token**
```bash
# Login endpoint (implement based on your auth system)
curl -X POST https://api.omnifyproduct.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

---

## **1. Agent Management** 🤖

### **Create Agent**
```bash
curl -X POST https://api.omnifyproduct.com/api/agentkit/agents \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Creative Intelligence Agent",
    "agent_type": "creative_intelligence",
    "description": "Analyzes creative assets for AIDA optimization",
    "config": {
      "analysis_types": ["aida", "brand_compliance", "performance_prediction"],
      "platforms": ["google_ads", "meta_ads", "linkedin_ads"],
      "auto_optimize": true
    }
  }'
```

**Response:**
```json
{
  "agent_id": "org_creative_intelligence",
  "status": "created",
  "agentkit_agent_id": "agent_abc123def456",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### **List Agents**
```bash
curl -X GET "https://api.omnifyproduct.com/api/agentkit/agents?organization_id=your-org-id" \
  -H "Authorization: Bearer your-token"
```

**Response:**
```json
[
  {
    "agent_id": "org_creative_intelligence",
    "name": "Creative Intelligence Agent",
    "agent_type": "creative_intelligence",
    "description": "Analyzes creative assets for AIDA optimization",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### **Execute Agent**
```bash
curl -X POST https://api.omnifyproduct.com/api/agentkit/agents/org_creative_intelligence/execute \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "asset_url": "https://example.com/creative.jpg",
      "analysis_type": "aida",
      "target_platforms": ["google_ads", "meta_ads"]
    },
    "context": {
      "user_id": "user_123",
      "session_id": "session_456"
    }
  }'
```

**Response:**
```json
{
  "execution_id": "exec_abc123def456",
  "agent_id": "org_creative_intelligence",
  "status": "completed",
  "output_data": {
    "aida_scores": {
      "attention": 0.75,
      "interest": 0.70,
      "desire": 0.65,
      "action": 0.70
    },
    "recommendations": [
      "Increase visual contrast for better attention capture",
      "Add social proof elements to boost desire"
    ]
  },
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:02Z",
  "duration_seconds": 2.5
}
```

---

## **2. Workflow Management** ⚡

### **Create Workflow**
```bash
curl -X POST https://api.omnifyproduct.com/api/agentkit/workflows \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Campaign Launch Workflow",
    "description": "Complete campaign creation and launch process",
    "steps": [
      {
        "step_id": "creative_analysis",
        "agent_type": "creative_intelligence",
        "input_mapping": {
          "asset_url": "campaign_creative_url",
          "analysis_type": "campaign_launch"
        },
        "output_mapping": {
          "aida_scores": "campaign_aida_scores",
          "recommendations": "creative_recommendations"
        }
      },
      {
        "step_id": "campaign_creation",
        "agent_type": "marketing_automation",
        "depends_on": ["creative_analysis"],
        "input_mapping": {
          "campaign_config": "campaign_config",
          "aida_scores": "campaign_aida_scores"
        },
        "output_mapping": {
          "platform_campaign_ids": "deployment_results"
        }
      },
      {
        "step_id": "performance_setup",
        "agent_type": "analytics",
        "depends_on": ["campaign_creation"],
        "input_mapping": {
          "campaign_ids": "deployment_results"
        },
        "output_mapping": {
          "tracking_setup": "analytics_setup"
        }
      }
    ],
    "config": {
      "execution_mode": "sequential",
      "notification_settings": {
        "email_on_completion": true,
        "email_on_failure": true
      }
    }
  }'
```

### **Execute Workflow**
```bash
curl -X POST https://api.omnifyproduct.com/api/agentkit/workflows/campaign_launch_workflow/execute \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "campaign_creative_url": "https://example.com/campaign-creative.jpg",
      "campaign_config": {
        "name": "Summer Sale Campaign",
        "objective": "conversions",
        "budget_daily": 100.00,
        "platforms": ["google_ads", "meta_ads"]
      }
    }
  }'
```

**Response:**
```json
{
  "execution_id": "workflow_exec_abc123def456",
  "workflow_id": "campaign_launch_workflow",
  "status": "completed",
  "output_data": {
    "campaign_aida_scores": {
      "attention": 0.78,
      "interest": 0.72,
      "desire": 0.68,
      "action": 0.74
    },
    "deployment_results": {
      "google_ads_campaign_id": "gads_1234567890",
      "meta_ads_campaign_id": "meta_0987654321"
    },
    "analytics_setup": {
      "tracking_implemented": true,
      "conversion_pixels": ["google", "meta"]
    }
  },
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:15Z",
  "duration_seconds": 15.2
}
```

---

## **3. Compliance & Audit** 📋

### **Run Compliance Check**
```bash
curl -X POST https://api.omnifyproduct.com/api/agentkit/compliance/check \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "check_type": "soc2",
    "organization_id": "your-org-id"
  }'
```

**Response:**
```json
{
  "check_id": "check_abc123def456",
  "organization_id": "your-org-id",
  "check_type": "soc2",
  "status": "passed",
  "findings": [
    {
      "severity": "info",
      "message": "7-day data retention policy active",
      "category": "data_retention",
      "recommendations": []
    }
  ],
  "recommendations": [],
  "checked_at": "2024-01-15T10:30:00Z",
  "next_check_at": "2024-02-15T10:30:00Z"
}
```

### **Get Audit Logs**
```bash
curl -X GET "https://api.omnifyproduct.com/api/agentkit/audit-logs?organization_id=your-org-id&start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z" \
  -H "Authorization: Bearer your-token"
```

**Response:**
```json
[
  {
    "log_id": "audit_abc123def456",
    "organization_id": "your-org-id",
    "user_id": "user_123",
    "action": "execute_agent",
    "resource_type": "agent",
    "resource_id": "agent_456",
    "timestamp": "2024-01-15T10:30:00Z",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "details": {
      "execution_id": "exec_789",
      "input_data_summary": "Creative analysis request"
    }
  }
]
```

---

## **4. Analytics & Metrics** 📊

### **Get Agent Metrics**
```bash
curl -X GET "https://api.omnifyproduct.com/api/agentkit/metrics?organization_id=your-org-id&start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z" \
  -H "Authorization: Bearer your-token"
```

**Response:**
```json
{
  "metrics": {
    "your-org-id": {
      "total_executions": 150,
      "successful_executions": 147,
      "failed_executions": 3,
      "average_execution_time_seconds": 2.3,
      "total_execution_time_seconds": 345,
      "agents_used": [
        {
          "agent_id": "org_creative_intelligence",
          "execution_count": 89,
          "average_time_seconds": 2.1
        },
        {
          "agent_id": "org_marketing_automation",
          "execution_count": 61,
          "average_time_seconds": 2.6
        }
      ],
      "platform_usage": {
        "google_ads": 45,
        "meta_ads": 38,
        "linkedin_ads": 18
      }
    }
  },
  "period": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z"
  }
}
```

---

## **5. Error Handling Examples** 🚨

### **Validation Error**
```json
{
  "error": "Validation Error",
  "field": "email",
  "message": "Invalid email format",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Authentication Error**
```json
{
  "error": "Authentication Error",
  "message": "Valid JWT token required",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Business Logic Error**
```json
{
  "error": "BUSINESS_LOGIC_ERROR",
  "message": "Campaign budget exceeds organization limit",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Not Found Error**
```json
{
  "error": "Not Found",
  "resource": "agent",
  "identifier": "non_existent_agent",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## **6. Webhook Integration** 🔗

### **Webhook Configuration**
```bash
curl -X POST https://api.omnifyproduct.com/api/webhooks \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Campaign Completion Webhook",
    "url": "https://your-app.com/webhooks/campaign-complete",
    "events": ["workflow.completed", "workflow.failed"],
    "secret": "your-webhook-secret"
  }'
```

### **Webhook Payload Example**
```json
{
  "event": "workflow.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "workflow_id": "campaign_launch_workflow",
    "execution_id": "workflow_exec_abc123def456",
    "organization_id": "your-org-id",
    "status": "completed",
    "output_data": {
      "campaign_aida_scores": {...},
      "deployment_results": {...}
    }
  }
}
```

---

## **7. Batch Operations** 📦

### **Batch Agent Execution**
```bash
curl -X POST https://api.omnifyproduct.com/api/agentkit/agents/batch-execute \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "agent_id": "org_creative_intelligence",
        "input_data": {
          "asset_url": "https://example.com/creative1.jpg",
          "analysis_type": "aida"
        }
      },
      {
        "agent_id": "org_creative_intelligence",
        "input_data": {
          "asset_url": "https://example.com/creative2.jpg",
          "analysis_type": "aida"
        }
      }
    ]
  }'
```

**Response:**
```json
{
  "batch_id": "batch_abc123def456",
  "total_requests": 2,
  "results": [
    {
      "request_index": 0,
      "execution_id": "exec_123",
      "status": "completed",
      "output_data": {...}
    },
    {
      "request_index": 1,
      "execution_id": "exec_456",
      "status": "completed",
      "output_data": {...}
    }
  ]
}
```

---

## **8. Real-time Updates** ⚡

### **Server-Sent Events (SSE)**
```javascript
// Client-side JavaScript for real-time updates
const eventSource = new EventSource('https://api.omnifyproduct.com/api/events?organization_id=your-org-id');

eventSource.addEventListener('workflow_update', (event) => {
  const data = JSON.parse(event.data);
  console.log('Workflow update:', data);
});

eventSource.addEventListener('agent_execution', (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent execution:', data);
});
```

---

## **9. Rate Limiting** 🚦

### **Rate Limit Headers**
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

### **Rate Limit Exceeded**
```json
{
  "error": "Rate Limit Exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after_seconds": 60,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## **10. SDK Examples** 💻

### **Python SDK Usage**
```python
import asyncio
from omnifyproduct import OmnifyProduct

async def main():
    client = OmnifyProduct(api_key="your-api-key")

    # Create agent
    agent = await client.create_agent(
        name="Creative Agent",
        agent_type="creative_intelligence",
        config={"platforms": ["google_ads"]}
    )

    # Execute workflow
    result = await client.execute_workflow(
        workflow_id="campaign_launch",
        input_data={
            "campaign_creative_url": "https://example.com/creative.jpg",
            "campaign_config": {"name": "Test Campaign"}
        }
    )

    print(f"Workflow completed: {result['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### **JavaScript/Node.js SDK Usage**
```javascript
const { OmnifyProduct } = require('omnifyproduct-sdk');

const client = new OmnifyProduct({
  apiKey: 'your-api-key',
  baseURL: 'https://api.omnifyproduct.com'
});

// Create and execute agent
async function runAgent() {
  try {
    const result = await client.executeAgent('agent-id', {
      asset_url: 'https://example.com/creative.jpg',
      analysis_type: 'aida'
    });

    console.log('Agent result:', result.output_data);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

runAgent();
```

---

## **11. Troubleshooting** 🔧

### **Common Issues**

#### **401 Unauthorized**
- Check JWT token validity
- Verify token expiration
- Ensure correct Authorization header format

#### **422 Validation Error**
- Verify request body format matches API specification
- Check required fields are present
- Validate data types and constraints

#### **429 Rate Limit Exceeded**
- Implement exponential backoff retry logic
- Check current rate limit status in response headers
- Consider upgrading plan for higher limits

#### **500 Internal Server Error**
- Check application logs for detailed error information
- Verify all required services are running
- Contact support if issue persists

### **Debug Mode**
Enable debug logging by setting environment variable:
```bash
export LOG_LEVEL=DEBUG
```

---

## **12. Best Practices** ✅

### **API Design**
- Use descriptive agent and workflow names
- Implement proper error handling in client applications
- Cache frequently accessed data (agents, workflows)
- Use pagination for large result sets

### **Performance**
- Batch similar operations when possible
- Implement retry logic with exponential backoff
- Monitor API usage and performance metrics
- Use appropriate timeouts for long-running operations

### **Security**
- Store API keys securely (environment variables, secret management)
- Implement proper authentication in client applications
- Validate all data before sending to API
- Use HTTPS for all API communication

### **Monitoring**
- Track API usage and performance metrics
- Set up alerts for failed operations
- Monitor rate limit usage
- Log important operations for audit trails

---

## **13. Migration from v1.x** 🔄

### **Breaking Changes in v2.0.0**

1. **Agent Execution API**
   - `POST /execute` → `POST /agents/{agent_id}/execute`
   - Response format includes execution metadata

2. **Workflow API**
   - Enhanced workflow definition format with dependency management
   - New execution modes (sequential, parallel, conditional)

3. **Error Response Format**
   - Standardized error response structure
   - More detailed error information

### **Migration Steps**
1. Update API client to use new endpoint paths
2. Handle new response formats
3. Update error handling for new error structure
4. Test all integrations thoroughly

---

*This API documentation covers all features implemented in OmnifyProduct v2.0.0. For additional support, visit our documentation portal or contact our technical support team.*
