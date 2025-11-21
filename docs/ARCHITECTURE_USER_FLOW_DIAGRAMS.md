# 🏗️ OmniFy Cloud Connect - Architecture & User Flow Diagrams

## 📋 System Architecture Overview

### **High-Level Architecture**

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Dashboard]
        EYES[EYES Module UI]
        BRAIN[Brain Logic Panel]
        ANALYTICS[Analytics Dashboard]
    end
    
    subgraph "API Gateway Layer"
        GATEWAY[FastAPI Gateway]
        AUTH[JWT Authentication]
        RATE[Rate Limiting]
        CORS[CORS Middleware]
    end
    
    subgraph "Business Logic Layer"
        AGENTS[AgentKit Agents]
        BRAIN_LOGIC[Brain Logic Modules]
        PLATFORM_MGR[Platform Manager]
        WORKFLOWS[Workflow Orchestrator]
    end
    
    subgraph "Integration Layer"
        TW[TripleWhale API - Primary]
        HS[HubSpot API - Secondary]
        KL[Klaviyo API - Tertiary]
        GHL[GoHighLevel API - Low Priority]
        LINKEDIN[LinkedIn Ads API]
        SHOPIFY[Shopify API]
        STRIPE[Stripe API]
        OPENAI[OpenAI AgentKit]
    end
    
    subgraph "Data Layer"
        MONGODB[(MongoDB)]
        REDIS[(Redis Cache)]
        RABBITMQ[(RabbitMQ)]
    end
    
    subgraph "Infrastructure Layer"
        DOCKER[Docker Containers]
        MONITORING[Grafana/Prometheus]
        LOGGING[Loki/Structured Logs]
    end
    
    UI --> GATEWAY
    EYES --> GATEWAY
    BRAIN --> GATEWAY
    ANALYTICS --> GATEWAY
    
    GATEWAY --> AUTH
    GATEWAY --> RATE
    GATEWAY --> CORS
    
    GATEWAY --> AGENTS
    GATEWAY --> BRAIN_LOGIC
    GATEWAY --> PLATFORM_MGR
    GATEWAY --> WORKFLOWS
    
    AGENTS --> OPENAI
    PLATFORM_MGR --> TW
    PLATFORM_MGR --> HS
    PLATFORM_MGR --> KL
    PLATFORM_MGR --> GHL
    PLATFORM_MGR --> LINKEDIN
    PLATFORM_MGR --> SHOPIFY
    PLATFORM_MGR --> STRIPE
    
    AGENTS --> MONGODB
    BRAIN_LOGIC --> MONGODB
    PLATFORM_MGR --> REDIS
    WORKFLOWS --> RABBITMQ
    
    DOCKER --> MONITORING
    DOCKER --> LOGGING
```

---

## 🔄 User Flow Diagrams

### **1. Client Onboarding Flow**

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend
    participant API as FastAPI Gateway
    participant AUTH as Auth Service
    participant ORG as Organization Service
    participant PLAT as Platform Manager
    participant GHL as GoHighLevel API
    
    U->>UI: Visit OmniFy Dashboard
    UI->>API: GET /health
    API-->>UI: System Status
    
    U->>UI: Click "Sign Up"
    UI->>API: POST /api/auth/register
    API->>AUTH: Create User Account
    AUTH->>ORG: Create Organization
    ORG-->>AUTH: Organization ID
    AUTH-->>API: JWT Token + Org ID
    API-->>UI: Authentication Success
    
    U->>UI: Connect GoHighLevel
    UI->>API: POST /api/platforms/gohighlevel/connect
    API->>PLAT: Initialize GoHighLevel Integration
    PLAT->>GHL: Test API Connection
    GHL-->>PLAT: Connection Success
    PLAT-->>API: Integration Ready
    API-->>UI: GoHighLevel Connected
    
    U->>UI: Access EYES Module
    UI->>API: GET /api/eyes/segments/30d
    API->>PLAT: Get Customer Data
    PLAT->>GHL: Fetch Contacts
    GHL-->>PLAT: Contact Data
    PLAT-->>API: Segmented Data
    API-->>UI: Customer Segments Display
```

### **2. EYES Module - Customer Segmentation Flow**

```mermaid
flowchart TD
    START([User Accesses EYES Module]) --> LOAD[Load Customer Data]
    LOAD --> VALIDATE{Validate Consent Fields}
    
    VALIDATE -->|Missing| ADD_CONSENT[Add Default Consent Values]
    VALIDATE -->|Valid| FEATURE_ENG[Feature Engineering]
    ADD_CONSENT --> FEATURE_ENG
    
    FEATURE_ENG --> CLUSTER[Perform Clustering Analysis]
    CLUSTER --> KMEANS[K-Means Clustering]
    CLUSTER --> DBSCAN[DBSCAN Clustering]
    CLUSTER --> AGGLOM[Agglomerative Clustering]
    
    KMEANS --> EVAL[Evaluate Clustering Quality]
    DBSCAN --> EVAL
    AGGLOM --> EVAL
    
    EVAL --> SILHOUETTE{Silhouette Score >= 0.45?}
    SILHOUETTE -->|Yes| SELECT_BEST[Select Best Algorithm]
    SILHOUETTE -->|No| ADJUST[Adjust Parameters]
    ADJUST --> CLUSTER
    
    SELECT_BEST --> CHURN[Churn Prediction Analysis]
    CHURN --> MODEL_30[30-Day Churn Model]
    CHURN --> MODEL_60[60-Day Churn Model]
    CHURN --> MODEL_90[90-Day Churn Model]
    
    MODEL_30 --> AUC_CHECK{AUC >= 0.70?}
    MODEL_60 --> AUC_CHECK
    MODEL_90 --> AUC_CHECK
    
    AUC_CHECK -->|Yes| GENERATE[Generate Segment Analysis]
    AUC_CHECK -->|No| RETRAIN[Retrain Models]
    RETRAIN --> CHURN
    
    GENERATE --> CROSS_PLAT[Cross-Platform Analysis]
    CROSS_PLAT --> LEARNING[Learning Insights]
    LEARNING --> STORE[Store Results]
    STORE --> DISPLAY[Display Dashboard]
    DISPLAY --> END([User Views Segments])
```

### **3. Platform Integration Flow**

```mermaid
graph LR
    subgraph "OmniFy Platform Manager"
        PM[Platform Manager]
        CB[Circuit Breaker]
        RL[Rate Limiter]
        CACHE[Cache Manager]
    end
    
    subgraph "External APIs"
        GHL[GoHighLevel API]
        LI[LinkedIn Ads API]
        SH[Shopify API]
        ST[Stripe API]
        OA[OpenAI AgentKit]
    end
    
    subgraph "Data Processing"
        VALIDATE[Input Validation]
        TRANSFORM[Data Transformation]
        ENRICH[Data Enrichment]
        STORE[Data Storage]
    end
    
    PM --> VALIDATE
    VALIDATE --> CB
    CB --> RL
    RL --> CACHE
    
    CACHE -->|Cache Miss| GHL
    CACHE -->|Cache Miss| LI
    CACHE -->|Cache Miss| SH
    CACHE -->|Cache Miss| ST
    CACHE -->|Cache Miss| OA
    
    GHL --> TRANSFORM
    LI --> TRANSFORM
    SH --> TRANSFORM
    ST --> TRANSFORM
    OA --> TRANSFORM
    
    TRANSFORM --> ENRICH
    ENRICH --> STORE
    STORE --> CACHE
    CACHE --> PM
```

### **4. Brain Logic Modules Architecture**

```mermaid
graph TB
    subgraph "Brain Logic Modules"
        CREATIVE[Creative Intelligence]
        MARKET[Market Intelligence]
        CLIENT[Client Intelligence]
        EYES[EYES - At-Risk Segments]
        CUSTOM[Customization Engine]
    end
    
    subgraph "Data Sources"
        GHL_DATA[GoHighLevel Data]
        PLATFORM_DATA[Platform Data]
        USER_DATA[User Behavior Data]
        MARKET_DATA[Market Data]
    end
    
    subgraph "AI Processing"
        GPT[GPT-4o-mini]
        ML_MODELS[ML Models]
        CLUSTERING[Clustering Algorithms]
        PREDICTION[Prediction Models]
    end
    
    subgraph "Output Actions"
        RECOMMENDATIONS[Recommendations]
        AUTOMATION[Automated Actions]
        ALERTS[Alerts & Notifications]
        REPORTS[Reports & Analytics]
    end
    
    GHL_DATA --> CREATIVE
    PLATFORM_DATA --> MARKET
    USER_DATA --> CLIENT
    USER_DATA --> EYES
    MARKET_DATA --> MARKET
    
    CREATIVE --> GPT
    MARKET --> ML_MODELS
    CLIENT --> ML_MODELS
    EYES --> CLUSTERING
    EYES --> PREDICTION
    CUSTOM --> GPT
    
    GPT --> RECOMMENDATIONS
    ML_MODELS --> AUTOMATION
    CLUSTERING --> ALERTS
    PREDICTION --> REPORTS
```

### **5. AgentKit Integration Flow**

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant API as FastAPI
    participant AGENT as AgentKit Service
    participant SDK as OpenAI Agents SDK
    participant OPENAI as OpenAI API
    participant GHL as GoHighLevel
    
    UI->>API: Execute Agent Workflow
    API->>AGENT: Process Workflow Request
    AGENT->>SDK: Check AgentKit Availability
    
    alt AgentKit SDK Available
        SDK->>OPENAI: Execute Agent
        OPENAI-->>SDK: Agent Response
        SDK-->>AGENT: Structured Response
    else AgentKit SDK Not Available
        AGENT->>OPENAI: Fallback to OpenAI API
        OPENAI-->>AGENT: API Response
        AGENT->>AGENT: Format as Agent Response
    end
    
    AGENT->>GHL: Trigger Platform Actions
    GHL-->>AGENT: Action Results
    AGENT-->>API: Workflow Results
    API-->>UI: Display Results
```

### **6. Data Flow Architecture**

```mermaid
graph TB
    subgraph "Data Ingestion"
        API_CALLS[API Calls]
        WEBHOOKS[Webhooks]
        FILE_UPLOAD[File Uploads]
        USER_INPUT[User Input]
    end
    
    subgraph "Data Processing"
        VALIDATION[Data Validation]
        TRANSFORMATION[Data Transformation]
        ENRICHMENT[Data Enrichment]
        AGGREGATION[Data Aggregation]
    end
    
    subgraph "Storage Layer"
        MONGODB[(MongoDB<br/>Primary Data)]
        REDIS[(Redis<br/>Cache & Sessions)]
        FILES[(File Storage<br/>Assets & Documents)]
    end
    
    subgraph "Analytics & ML"
        EYES_MODULE[EYES Module]
        PREDICTIVE[Predictive Models]
        ANALYTICS[Analytics Engine]
        LEARNING[Learning System]
    end
    
    subgraph "Output & Actions"
        DASHBOARD[Dashboard Display]
        AUTOMATION[Automated Actions]
        NOTIFICATIONS[Notifications]
        REPORTS[Generated Reports]
    end
    
    API_CALLS --> VALIDATION
    WEBHOOKS --> VALIDATION
    FILE_UPLOAD --> VALIDATION
    USER_INPUT --> VALIDATION
    
    VALIDATION --> TRANSFORMATION
    TRANSFORMATION --> ENRICHMENT
    ENRICHMENT --> AGGREGATION
    
    AGGREGATION --> MONGODB
    AGGREGATION --> REDIS
    AGGREGATION --> FILES
    
    MONGODB --> EYES_MODULE
    MONGODB --> PREDICTIVE
    MONGODB --> ANALYTICS
    MONGODB --> LEARNING
    
    EYES_MODULE --> DASHBOARD
    PREDICTIVE --> AUTOMATION
    ANALYTICS --> REPORTS
    LEARNING --> NOTIFICATIONS
```

### **7. Security & Compliance Architecture**

```mermaid
graph TB
    subgraph "Security Layers"
        JWT[JWT Authentication]
        RBAC[Role-Based Access Control]
        RATE_LIMIT[Rate Limiting]
        CORS[CORS Protection]
    end
    
    subgraph "Data Protection"
        ENCRYPTION[Data Encryption]
        SECRETS[Secrets Management]
        AUDIT[Audit Logging]
        CONSENT[Consent Management]
    end
    
    subgraph "Compliance"
        GDPR[GDPR Compliance]
        SOC2[SOC 2 Compliance]
        ISO27001[ISO 27001]
        DATA_RETENTION[Data Retention]
    end
    
    subgraph "Monitoring"
        LOGGING[Structured Logging]
        METRICS[Performance Metrics]
        ALERTS[Security Alerts]
        TRACING[Request Tracing]
    end
    
    JWT --> RBAC
    RBAC --> RATE_LIMIT
    RATE_LIMIT --> CORS
    
    CORS --> ENCRYPTION
    ENCRYPTION --> SECRETS
    SECRETS --> AUDIT
    AUDIT --> CONSENT
    
    CONSENT --> GDPR
    GDPR --> SOC2
    SOC2 --> ISO27001
    ISO27001 --> DATA_RETENTION
    
    DATA_RETENTION --> LOGGING
    LOGGING --> METRICS
    METRICS --> ALERTS
    ALERTS --> TRACING
```

### **8. Deployment Architecture**

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_LOCAL[Local Development]
        DEV_DOCKER[Docker Compose]
        DEV_TEST[Test Environment]
    end
    
    subgraph "Staging Environment"
        STAGING_K8S[Kubernetes Staging]
        STAGING_MONITOR[Staging Monitoring]
        STAGING_TEST[Integration Tests]
    end
    
    subgraph "Production Environment"
        PROD_K8S[Kubernetes Production]
        PROD_LB[Load Balancer]
        PROD_CDN[CDN]
        PROD_MONITOR[Production Monitoring]
    end
    
    subgraph "Infrastructure Services"
        MONGODB_ATLAS[MongoDB Atlas]
        REDIS_CLOUD[Redis Cloud]
        MONITORING[Grafana/Prometheus]
        LOGGING[Loki/Structured Logs]
    end
    
    DEV_LOCAL --> DEV_DOCKER
    DEV_DOCKER --> DEV_TEST
    DEV_TEST --> STAGING_K8S
    
    STAGING_K8S --> STAGING_MONITOR
    STAGING_MONITOR --> STAGING_TEST
    STAGING_TEST --> PROD_K8S
    
    PROD_K8S --> PROD_LB
    PROD_LB --> PROD_CDN
    PROD_CDN --> PROD_MONITOR
    
    PROD_K8S --> MONGODB_ATLAS
    PROD_K8S --> REDIS_CLOUD
    PROD_MONITOR --> MONITORING
    PROD_MONITOR --> LOGGING
```

---

## 🎯 Key Architecture Principles

### **1. Microservices Architecture**
- **Modular Design**: Each brain module is independent
- **API-First**: All modules communicate via REST APIs
- **Scalable**: Individual modules can be scaled independently

### **2. AgentKit-First Approach**
- **Visual Development**: Drag-and-drop agent creation
- **Enterprise Compliance**: Built-in SOC 2 & ISO 27001
- **Cost Efficiency**: 70-80% cost reduction vs custom development

### **3. Multi-Tenant Architecture**
- **Organization Isolation**: Complete data separation
- **Role-Based Access**: Granular permission system
- **Resource Sharing**: Efficient resource utilization

### **4. Event-Driven Architecture**
- **Asynchronous Processing**: Non-blocking operations
- **Real-Time Updates**: Live data synchronization
- **Workflow Orchestration**: Complex automation workflows

### **5. Security-First Design**
- **Zero Trust**: All requests authenticated and authorized
- **Data Encryption**: End-to-end encryption
- **Audit Trail**: Complete activity logging

---

## 🚀 User Journey Summary

### **Phase 1: Onboarding (10 minutes)**
1. **User Registration** → Organization Setup
2. **Platform Integration** → Connect GoHighLevel
3. **Feature Access** → EYES Module Activation
4. **Automated Setup** → Complete Onboarding Workflow

### **Phase 2: Daily Operations**
1. **Dashboard Access** → View Analytics
2. **Brain Logic** → AI-Powered Insights
3. **EYES Module** → Customer Segmentation
4. **Platform Actions** → Automated Workflows

### **Phase 3: Advanced Features**
1. **Predictive Intelligence** → ORACLE Module
2. **Content Repurposing** → VOICE Module
3. **Budget Optimization** → CURIOSITY Module
4. **Performance Analytics** → MEMORY Module

This architecture provides a scalable, secure, and efficient platform for autonomous marketing intelligence with the revolutionary AgentKit-first approach.
