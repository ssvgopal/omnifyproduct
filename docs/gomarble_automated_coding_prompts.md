# GoMarble AI Replication - Automated Coding Prompts & Implementation Logic

## Executive Summary

This document provides detailed automated coding prompts and implementation logic for replicating GoMarble AI's campaign intelligence capabilities within Omnify Cloud Connect. Each prompt is designed for emergent.sh or similar AI coding tools to implement specific features.

## Phase 1: Core Analytics Engine Implementation

### Prompt 1: Campaign Brief Analysis Module

```
IMPLEMENTATION REQUEST: Campaign Brief Analysis Module

CONTEXT:
I need to implement a comprehensive campaign brief analysis module that replicates GoMarble AI's campaign brief intelligence capabilities within our existing Omnify Cloud Connect architecture.

REQUIREMENTS:
1. Campaign Brief Ingestion System
   - Parse campaign briefs from multiple sources (PDF, Word, text, API)
   - Extract key information: platform, budget, goals, target audience, creative format
   - Structure data into unified schema compatible with our brain logic
   - Support multiple brief formats and languages

2. Automated Brief Analysis Engine
   - Gap analysis: Identify missing elements and potential risks
   - Trend analysis: Surface patterns across multiple briefs
   - Risk assessment: Flag potential issues before campaign launch
   - Optimization suggestions: Recommend improvements based on best practices
   - Vertical-specific analysis: Adapt analysis for different markets (ecommerce, saas, healthcare, finance, education)

3. Brief Intelligence Features
   - Brief completeness scoring (0-100)
   - Risk level assessment (low/medium/high/critical)
   - Missing element identification
   - Best practice recommendations
   - Competitive benchmarking suggestions
   - Budget optimization recommendations

4. Integration with Existing Architecture
   - Extend Creative Intelligence module with brief analysis
   - Integrate with Market Intelligence for competitive insights
   - Connect to Client Intelligence for success prediction
   - Use existing brain logic framework for customization

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with existing Omnify architecture
- AI Integration: OpenAI GPT-4 for brief parsing and analysis
- Database: MongoDB with existing schema
- Frontend: React components for brief upload and analysis display
- API: RESTful endpoints for brief management and analysis

CUSTOMIZATION REQUIREMENTS:
- Market-specific brief templates and analysis criteria
- Vertical-specific risk assessment models
- Customizable analysis parameters per client
- Brand-specific brief requirements and compliance

DELIVERABLES:
1. Campaign brief ingestion API endpoints
2. Automated brief analysis engine
3. Brief intelligence scoring system
4. Risk assessment and recommendation engine
5. Frontend components for brief management
6. Integration with existing brain logic modules
7. Comprehensive testing suite
8. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble replication strategy
- Existing Omnify architecture
- Brain logic framework documentation

IMPLEMENTATION PRIORITY: CRITICAL (Week 1-2)
```

### Prompt 2: Creative Asset Analysis Engine

```
IMPLEMENTATION REQUEST: Creative Asset Analysis Engine

CONTEXT:
Building on the campaign brief analysis, I need to implement a sophisticated creative asset analysis engine that replicates GoMarble AI's creative intelligence capabilities.

REQUIREMENTS:
1. Creative Asset Processing System
   - Support multiple creative formats: images, videos, carousels, UGC content
   - Extract creative elements: hooks, messaging, visuals, CTAs
   - Analyze creative performance metrics: ROAS, CTR, CPC, engagement rates
   - Track creative lifecycle and fatigue patterns

2. AIDA Framework Analysis
   - Attention: Hook effectiveness and visual impact analysis
   - Interest: Content relevance and audience engagement
   - Desire: Persuasion elements and value proposition clarity
   - Action: CTA effectiveness and conversion optimization
   - Overall AIDA score calculation and optimization suggestions

3. Creative Performance Intelligence
   - Creative fatigue detection algorithms
   - Top performer identification and analysis
   - Persona-specific creative effectiveness tracking
   - Format optimization recommendations
   - Hook analysis and messaging effectiveness
   - Creative refresh cycle recommendations

4. Advanced Creative Analytics
   - Creative A/B testing recommendations
   - Performance prediction models
   - Creative scaling suggestions
   - Underperformer identification and optimization
   - Creative trend analysis and forecasting

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with computer vision capabilities
- AI Integration: OpenAI GPT-4 + DALL-E for creative analysis
- Computer Vision: OpenCV, PIL for image/video processing
- Database: MongoDB with creative asset schema
- Frontend: React components for creative upload and analysis
- API: RESTful endpoints for creative management and analysis

CUSTOMIZATION REQUIREMENTS:
- Brand-specific creative guidelines and compliance
- Vertical-specific creative performance benchmarks
- Customizable AIDA scoring criteria
- Client-specific creative preferences and requirements

DELIVERABLES:
1. Creative asset processing pipeline
2. AIDA framework analysis engine
3. Creative performance intelligence system
4. Fatigue detection and optimization algorithms
5. Creative analytics dashboard components
6. Integration with existing creative intelligence module
7. Comprehensive testing suite
8. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble creative analysis capabilities
- Existing creative intelligence module
- AIDA framework specifications

IMPLEMENTATION PRIORITY: CRITICAL (Week 2-3)
```

### Prompt 3: Multi-Platform Campaign Analytics

```
IMPLEMENTATION REQUEST: Multi-Platform Campaign Analytics Engine

CONTEXT:
I need to implement a comprehensive multi-platform campaign analytics engine that unifies data from Google Ads, Meta Ads, LinkedIn Ads, Shopify, and Google Analytics.

REQUIREMENTS:
1. Multi-Platform Data Integration
   - Google Ads API integration for campaign metrics
   - Meta Ads API integration for Facebook/Instagram data
   - LinkedIn Ads API integration for B2B metrics
   - Shopify API integration for e-commerce data
   - Google Analytics API integration for website metrics
   - Unified data schema across all platforms

2. Cross-Channel Analytics Engine
   - Unified metrics dashboard: ROAS, CPC, CPM, revenue, conversions
   - Attribution modeling: Multi-touch attribution analysis
   - Budget optimization: Spend allocation recommendations
   - Performance comparison: Channel-wise performance analysis
   - Scaling recommendations: High-ROAS opportunity identification

3. Advanced Analytics Features
   - Cohort analysis for customer lifecycle tracking
   - Conversion funnel analysis across platforms
   - Customer lifetime value calculation
   - Return on ad spend optimization
   - Cross-platform customer journey mapping

4. Real-Time Analytics Dashboard
   - Live performance monitoring
   - Real-time alert system for performance issues
   - Customizable dashboard widgets
   - Export capabilities (PDF, Excel, CSV)
   - Scheduled report generation

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with async processing
- APIs: Google Ads, Meta Ads, LinkedIn Ads, Shopify, Google Analytics
- Database: MongoDB with time-series data optimization
- Frontend: React with real-time data visualization
- Caching: Redis for performance optimization
- Queue: Celery for background data processing

CUSTOMIZATION REQUIREMENTS:
- Client-specific metric definitions and KPIs
- Vertical-specific performance benchmarks
- Customizable dashboard layouts and widgets
- Brand-specific reporting templates

DELIVERABLES:
1. Multi-platform API integration system
2. Unified analytics data pipeline
3. Cross-channel analytics engine
4. Real-time dashboard components
5. Attribution modeling system
6. Export and reporting capabilities
7. Comprehensive testing suite
8. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble multi-platform analytics
- Existing analytics engine architecture
- Platform API documentation

IMPLEMENTATION PRIORITY: HIGH (Week 3-4)
```

## Phase 2: Advanced Intelligence Features

### Prompt 4: Root-Cause Diagnostics Engine

```
IMPLEMENTATION REQUEST: Root-Cause Diagnostics Engine

CONTEXT:
I need to implement a sophisticated root-cause diagnostics engine that identifies performance issues and classifies them as technical or creative problems.

REQUIREMENTS:
1. Performance Issue Detection
   - Anomaly detection algorithms for performance drops
   - Threshold-based alerting system
   - Pattern recognition for recurring issues
   - Real-time monitoring and alerting
   - Historical trend analysis for issue prediction

2. Issue Classification System
   - Technical vs creative issue attribution
   - Severity level classification (low/medium/high/critical)
   - Impact assessment on campaign performance
   - Root cause identification and explanation
   - Remediation suggestion generation

3. Automated Diagnostics Features
   - Performance drop analysis with context
   - Attribution pattern analysis
   - Budget misallocation detection
   - Creative fatigue identification
   - Technical issue flagging (API errors, tracking issues)

4. Escalation and Workflow System
   - Automated escalation triggers
   - Workflow automation for issue resolution
   - Human intervention requirements
   - Notification system for stakeholders
   - Issue tracking and resolution monitoring

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with machine learning capabilities
- ML Models: Anomaly detection, classification, prediction
- Database: MongoDB with issue tracking schema
- Frontend: React components for issue management
- Queue: Celery for background processing
- Monitoring: Real-time alerting system

CUSTOMIZATION REQUIREMENTS:
- Client-specific issue thresholds and criteria
- Vertical-specific issue patterns and solutions
- Customizable escalation workflows
- Brand-specific issue resolution protocols

DELIVERABLES:
1. Anomaly detection and classification system
2. Root-cause analysis engine
3. Issue tracking and management system
4. Escalation workflow automation
5. Notification and alerting system
6. Integration with existing monitoring systems
7. Comprehensive testing suite
8. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble root-cause diagnostics
- Existing monitoring and alerting systems
- Machine learning model specifications

IMPLEMENTATION PRIORITY: HIGH (Week 5-6)
```

### Prompt 5: Competitor Intelligence Module

```
IMPLEMENTATION REQUEST: Competitor Intelligence Module

CONTEXT:
I need to implement a comprehensive competitor intelligence module that provides auction insights, benchmarking, and competitive analysis capabilities.

REQUIREMENTS:
1. Competitive Data Collection
   - Auction insights from Google Ads
   - Impression share analysis
   - Bid loss analysis and ranking
   - Competitor ad creative analysis
   - Market share estimation
   - Industry trend identification

2. Competitive Analysis Engine
   - Competitor performance benchmarking
   - Market positioning analysis
   - Competitive gap identification
   - Opportunity detection in competitive landscape
   - Trend analysis and forecasting
   - Competitive threat assessment

3. Advanced Competitive Intelligence
   - Competitor creative analysis and insights
   - Pricing strategy analysis
   - Audience targeting insights
   - Campaign structure analysis
   - Performance prediction vs competitors
   - Market opportunity identification

4. Competitive Reporting and Insights
   - Competitive dashboard with key metrics
   - Competitor comparison reports
   - Market trend analysis and insights
   - Opportunity identification and recommendations
   - Competitive positioning suggestions
   - Strategic recommendations based on competitive analysis

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with data scraping capabilities
- APIs: Google Ads API, Meta Ads API for competitive data
- Database: MongoDB with competitive intelligence schema
- Frontend: React components for competitive analysis
- Data Processing: Pandas, NumPy for analysis
- Caching: Redis for competitive data caching

CUSTOMIZATION REQUIREMENTS:
- Client-specific competitor lists and monitoring
- Vertical-specific competitive benchmarks
- Customizable competitive analysis criteria
- Brand-specific competitive positioning strategies

DELIVERABLES:
1. Competitive data collection system
2. Competitive analysis engine
3. Benchmarking and comparison tools
4. Competitive intelligence dashboard
5. Market opportunity identification system
6. Integration with existing market intelligence module
7. Comprehensive testing suite
8. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble competitor intelligence capabilities
- Existing market intelligence module
- Competitive analysis methodologies

IMPLEMENTATION PRIORITY: MEDIUM (Week 6-7)
```

### Prompt 6: Automated Recommendation Engine

```
IMPLEMENTATION REQUEST: Automated Recommendation Engine

CONTEXT:
I need to implement an intelligent recommendation engine that provides data-driven optimization suggestions for campaigns, creatives, and budgets.

REQUIREMENTS:
1. Campaign Optimization Recommendations
   - Campaign structure optimization suggestions
   - Budget allocation recommendations
   - Audience targeting optimization
   - Bid strategy recommendations
   - Campaign scaling suggestions
   - Underperformer containment strategies

2. Creative Optimization Recommendations
   - Creative refresh cycle recommendations
   - A/B testing suggestions
   - Creative format optimization
   - Hook and messaging improvements
   - Creative scaling recommendations
   - Creative performance optimization

3. Budget and Performance Optimization
   - Budget reallocation suggestions
   - High-ROAS opportunity identification
   - Cost efficiency improvements
   - Performance optimization strategies
   - ROI improvement recommendations
   - Waste reduction suggestions

4. Intelligent Recommendation System
   - Machine learning-based recommendation engine
   - Context-aware suggestions
   - Priority-based recommendation ranking
   - Implementation difficulty assessment
   - Expected impact prediction
   - Success probability estimation

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with machine learning capabilities
- ML Models: Recommendation algorithms, prediction models
- Database: MongoDB with recommendation schema
- Frontend: React components for recommendation display
- AI Integration: OpenAI GPT-4 for recommendation explanations
- Queue: Celery for background recommendation processing

CUSTOMIZATION REQUIREMENTS:
- Client-specific recommendation criteria and priorities
- Vertical-specific optimization strategies
- Customizable recommendation thresholds
- Brand-specific recommendation guidelines

DELIVERABLES:
1. Machine learning recommendation engine
2. Campaign optimization recommendation system
3. Creative optimization suggestion engine
4. Budget and performance optimization tools
5. Recommendation dashboard and interface
6. Integration with existing brain logic modules
7. Comprehensive testing suite
8. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble recommendation capabilities
- Existing brain logic framework
- Machine learning model specifications

IMPLEMENTATION PRIORITY: HIGH (Week 7-8)
```

## Phase 3: Automation & Workflow Engine

### Prompt 7: Automated Campaign Deployment System

```
IMPLEMENTATION REQUEST: Automated Campaign Deployment System

CONTEXT:
I need to implement a comprehensive automated campaign deployment system that can create, manage, and optimize campaigns across multiple platforms.

REQUIREMENTS:
1. Multi-Platform Campaign Creation
   - Automated campaign setup across Google Ads, Meta Ads, LinkedIn Ads
   - Campaign structure optimization based on recommendations
   - Budget allocation and bid strategy automation
   - Audience targeting automation
   - Creative asset deployment and management
   - Campaign launch coordination across platforms

2. Campaign Management Automation
   - Real-time campaign monitoring and adjustment
   - Automated bid optimization
   - Budget reallocation based on performance
   - Audience targeting refinement
   - Creative rotation and optimization
   - Performance-based campaign scaling

3. Workflow Automation Engine
   - Campaign creation workflows
   - Approval and review processes
   - Automated testing and optimization
   - Performance monitoring and alerting
   - Escalation and intervention workflows
   - Human oversight and manual override capabilities

4. Integration with Existing Systems
   - Integration with campaign brief analysis
   - Connection to creative asset analysis
   - Link to recommendation engine
   - Integration with monitoring and alerting
   - Connection to reporting and analytics

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with workflow automation
- APIs: Google Ads, Meta Ads, LinkedIn Ads APIs
- Database: MongoDB with workflow and campaign schema
- Frontend: React components for campaign management
- Queue: Celery for background workflow processing
- Workflow: Apache Airflow for complex workflow orchestration

CUSTOMIZATION REQUIREMENTS:
- Client-specific campaign creation templates
- Vertical-specific campaign strategies
- Customizable workflow automation rules
- Brand-specific campaign guidelines

DELIVERABLES:
1. Multi-platform campaign creation system
2. Campaign management automation engine
3. Workflow automation framework
4. Campaign monitoring and optimization tools
5. Integration with existing platform adapters
6. Comprehensive testing suite
7. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble automation capabilities
- Existing platform adapter architecture
- Workflow automation specifications

IMPLEMENTATION PRIORITY: CRITICAL (Week 9-10)
```

### Prompt 8: Real-Time Monitoring & Escalation System

```
IMPLEMENTATION REQUEST: Real-Time Monitoring & Escalation System

CONTEXT:
I need to implement a comprehensive real-time monitoring and escalation system that continuously tracks campaign performance and automatically escalates issues.

REQUIREMENTS:
1. Real-Time Performance Monitoring
   - Continuous campaign performance tracking
   - Real-time metric collection and analysis
   - Performance threshold monitoring
   - Anomaly detection and alerting
   - Live dashboard updates
   - Historical performance comparison

2. Automated Escalation System
   - Threshold-based alerting system
   - Escalation workflow automation
   - Issue severity classification
   - Automated intervention triggers
   - Human oversight requirements
   - Escalation path management

3. Intervention and Resolution System
   - Automated campaign adjustments
   - Performance issue resolution workflows
   - Emergency intervention capabilities
   - Manual override and control
   - Issue tracking and resolution monitoring
   - Success measurement and validation

4. Notification and Communication System
   - Multi-channel notification system (email, SMS, Slack)
   - Stakeholder communication management
   - Alert prioritization and routing
   - Notification preferences and customization
   - Communication history and tracking
   - Escalation status updates

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with real-time processing
- Database: MongoDB with monitoring and escalation schema
- Frontend: React components for monitoring dashboard
- Queue: Celery for background monitoring processing
- WebSocket: Real-time data streaming
- Notification: Email, SMS, Slack integration

CUSTOMIZATION REQUIREMENTS:
- Client-specific monitoring thresholds and criteria
- Vertical-specific escalation workflows
- Customizable notification preferences
- Brand-specific escalation protocols

DELIVERABLES:
1. Real-time monitoring system
2. Automated escalation engine
3. Intervention and resolution workflows
4. Notification and communication system
5. Monitoring dashboard and interface
6. Integration with existing alerting systems
7. Comprehensive testing suite
8. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble monitoring and escalation capabilities
- Existing monitoring and alerting architecture
- Escalation workflow specifications

IMPLEMENTATION PRIORITY: HIGH (Week 10-11)
```

## Phase 4: Advanced Analytics & Reporting

### Prompt 9: Executive Dashboard System

```
IMPLEMENTATION REQUEST: Executive Dashboard System

CONTEXT:
I need to implement a comprehensive executive dashboard system that provides unified metrics, trend analysis, and high-level insights for campaign performance.

REQUIREMENTS:
1. Unified Metrics Dashboard
   - ROAS, CPC, CPM, revenue, conversions tracking
   - Cross-platform performance comparison
   - Budget utilization and efficiency metrics
   - Campaign performance overview
   - Creative performance summary
   - Customer acquisition and retention metrics

2. Advanced Analytics Features
   - Trend analysis and forecasting
   - Cohort analysis for customer lifecycle
   - Attribution modeling and analysis
   - Performance prediction and modeling
   - Market share and competitive analysis
   - ROI and profitability analysis

3. Customizable Dashboard System
   - Drag-and-drop dashboard builder
   - Customizable widgets and metrics
   - Dashboard templates for different roles
   - Personalization and preferences
   - Dashboard sharing and collaboration
   - Mobile-responsive design

4. Real-Time Data Visualization
   - Live data updates and streaming
   - Interactive charts and graphs
   - Drill-down capabilities
   - Export and sharing options
   - Scheduled dashboard updates
   - Performance optimization for large datasets

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with data aggregation
- Frontend: React with D3.js, Chart.js for visualization
- Database: MongoDB with optimized queries
- Caching: Redis for dashboard performance
- WebSocket: Real-time data streaming
- Export: PDF, Excel, CSV generation

CUSTOMIZATION REQUIREMENTS:
- Role-specific dashboard templates
- Client-specific metric definitions
- Vertical-specific dashboard layouts
- Brand-specific dashboard branding

DELIVERABLES:
1. Unified metrics dashboard system
2. Advanced analytics and visualization engine
3. Customizable dashboard builder
4. Real-time data visualization components
5. Export and sharing capabilities
6. Integration with existing analytics engine
7. Comprehensive testing suite
8. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble executive dashboard capabilities
- Existing analytics dashboard architecture
- Data visualization specifications

IMPLEMENTATION PRIORITY: MEDIUM (Week 12-13)
```

### Prompt 10: Template-Driven Reporting System

```
IMPLEMENTATION REQUEST: Template-Driven Reporting System

CONTEXT:
I need to implement a comprehensive template-driven reporting system that provides automated report generation, scheduling, and customization capabilities.

REQUIREMENTS:
1. Pre-Built Report Templates
   - Multi-Platform Analysis reports
   - Weekly Creative Analysis reports
   - Traffic Quality and Funnel reports
   - Ads Audit and Health Check reports
   - Winning Ads and Performance reports
   - Video Hook Analysis reports
   - BFCM Strategy and Holiday reports

2. Custom Report Builder
   - Drag-and-drop report builder
   - Customizable report sections and metrics
   - Report template creation and management
   - Report sharing and collaboration
   - Report versioning and history
   - Report approval and review workflows

3. Automated Report Generation
   - Scheduled report generation and delivery
   - Real-time report updates
   - Automated report distribution
   - Report performance optimization
   - Report caching and storage
   - Report access control and permissions

4. Report Export and Distribution
   - Multiple export formats (PDF, Excel, CSV, PowerPoint)
   - Email distribution and scheduling
   - Report sharing and collaboration
   - Report archiving and retention
   - Report analytics and usage tracking
   - Report compliance and audit trails

TECHNICAL SPECIFICATIONS:
- Backend: Python/FastAPI with report generation
- Frontend: React components for report builder
- Database: MongoDB with report schema
- Export: PDF, Excel, CSV, PowerPoint generation
- Scheduling: Celery for automated report generation
- Storage: File storage for report archives

CUSTOMIZATION REQUIREMENTS:
- Client-specific report templates and branding
- Vertical-specific report formats and metrics
- Customizable report scheduling and distribution
- Brand-specific report styling and formatting

DELIVERABLES:
1. Pre-built report template system
2. Custom report builder interface
3. Automated report generation engine
4. Report export and distribution system
5. Report management and administration tools
6. Integration with existing reporting systems
7. Comprehensive testing suite
8. Documentation and deployment guides

REFERENCE DOCUMENTS:
- GoMarble reporting capabilities
- Existing reporting system architecture
- Report template specifications

IMPLEMENTATION PRIORITY: MEDIUM (Week 13-14)
```

## Implementation Timeline & Resource Allocation

### Phase 1: Core Analytics Engine (4-6 weeks)
- **Week 1-2**: Campaign Brief Analysis Module
- **Week 2-3**: Creative Asset Analysis Engine
- **Week 3-4**: Multi-Platform Campaign Analytics

### Phase 2: Advanced Intelligence Features (6-8 weeks)
- **Week 5-6**: Root-Cause Diagnostics Engine
- **Week 6-7**: Competitor Intelligence Module
- **Week 7-8**: Automated Recommendation Engine

### Phase 3: Automation & Workflow Engine (4-6 weeks)
- **Week 9-10**: Automated Campaign Deployment System
- **Week 10-11**: Real-Time Monitoring & Escalation System

### Phase 4: Advanced Analytics & Reporting (4-6 weeks)
- **Week 12-13**: Executive Dashboard System
- **Week 13-14**: Template-Driven Reporting System

## Usage Instructions

### How to Use These Prompts

1. **Copy the Complete Prompt**: Copy the entire prompt including context, requirements, technical specifications, and deliverables
2. **Customize for Your Needs**: Modify requirements, technical specifications, or deliverables based on your specific needs
3. **Execute with AI Coding Tool**: Use the prompt with emergent.sh or similar AI coding tools
4. **Iterate and Improve**: Use the results to refine and improve subsequent prompts

### Prompt Customization Guidelines

- **Modify Requirements**: Adjust requirements based on your specific needs
- **Update Technical Stack**: Change technical specifications based on your preferences
- **Customize Deliverables**: Modify deliverables based on your project scope
- **Add Context**: Include additional context specific to your implementation
- **Update Priorities**: Adjust implementation priorities based on your timeline

## Conclusion

These automated coding prompts provide a comprehensive implementation guide for replicating GoMarble AI's campaign intelligence capabilities within Omnify Cloud Connect. Each prompt is designed for AI coding tools to implement specific features, enabling rapid development and deployment of sophisticated campaign intelligence and automation capabilities.

**Estimated Timeline**: 14-18 weeks for full implementation
**Estimated Cost**: $400-600K
**ROI**: Enhanced campaign intelligence capabilities with automated implementation

This approach enables Omnify Cloud Connect to match and exceed GoMarble's capabilities while maintaining our unique advantages in multi-platform deployment, customizable brain logic, and white-label capabilities.
