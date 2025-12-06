# User Journeys - OmniFy Cloud Connect

## 📖 Overview

This document outlines key user journeys through the OmniFy Cloud Connect platform, from initial setup to daily usage.

---

## 🎯 User Persona: Marketing Manager (Sarah)

**Background:**
- Manages $50K/month ad budget across Meta, Google, TikTok
- Needs daily performance monitoring
- Makes budget allocation decisions weekly
- Reports to CMO monthly

---

## Journey 1: Initial Setup & Configuration

### Goal: Get the platform operational with API keys configured

**Duration**: 15-30 minutes  
**Frequency**: One-time

### Steps:

#### 1. Account Creation & Login (5 min)
```
1. Navigate to https://omnify.ai
2. Click "Get Started"
3. Enter email: sarah@company.com
4. Set password
5. Verify email
6. Log in to platform
```

**User sees:**
- Welcome screen
- Empty dashboard with setup prompts
- "Configure Integrations" button prominently displayed

---

#### 2. Configure OpenAI (5 min)
```
1. Click "Settings" or "Configure Integrations"
2. Navigate to API Keys page
3. Find "OpenAI" card under "AI / LLM Services"
4. Click "View Documentation" link (opens in new tab)
5. Follow guide to get OpenAI key
6. Copy key: sk-proj-abc123...
7. Return to OmniFy
8. Paste key in "API Key" field
9. Click "Save"
10. Wait for success message
11. Click "Test Connection"
12. See green success banner
```

**User thinks:**
- "This is straightforward"
- "Test connection gives me confidence"
- "Documentation link is helpful"

**Pain points:**
- If key is invalid, clear error message needed
- If OpenAI account has no credits, needs guidance

---

#### 3. Configure Meta Ads (10 min)
```
1. Switch to "Marketing Platforms" tab
2. Find "Meta Ads" card
3. Click "View Documentation" link
4. Navigate to Facebook Business Manager
5. Go to Ad Accounts section
6. Copy Ad Account ID: act_123456789
7. Go to Graph API Explorer
8. Generate Access Token with required permissions
9. Copy access token: EAAabc123...
10. Return to OmniFy
11. Paste both values
12. Click "Save"
13. Click "Test Connection"
14. See "Meta Ads connection successful"
```

**User thinks:**
- "Meta setup is more complex"
- "Good that test connection validates immediately"
- "Clear which permissions I need"

**Pain points:**
- Meta token expiration not clear
- Account ID format (with act_) may confuse

---

#### 4. First Data Sync (5 min)
```
1. Click "Back to Dashboard"
2. See "No data available" message
3. Click "Sync Data" button
4. See loading spinner
5. Wait 10-15 seconds
6. See success message: "Synced 7 days of data"
7. Dashboard updates with real metrics
8. Memory card shows: $12,450 spend, $49,800 revenue, 4.0x ROAS
```

**User thinks:**
- "Wow, my data is here!"
- "This ROAS looks good"
- "Easy to see overall performance"

**Success criteria:**
- ✅ All API keys configured
- ✅ Connections tested successfully
- ✅ Initial data synced
- ✅ Dashboard showing real metrics

---

## Journey 2: Daily Performance Check

### Goal: Quick morning check of campaign performance

**Duration**: 2-3 minutes  
**Frequency**: Daily (workdays)

### Steps:

#### 1. Login & Dashboard View (1 min)
```
1. Navigate to https://omnify.ai
2. Log in (if not already)
3. Land on dashboard automatically
4. Scan three brain modules
```

**What Sarah sees:**

**Memory Card:**
- Total Spend: $1,850 (yesterday)
- Total Revenue: $7,400
- ROAS: 4.0x ✅ (green, good)
- Trend: +5% vs last week

**Oracle Card:**
- Risk Score: 15% (Low) ✅
- Performance looks stable
- No alerts

**Curiosity Card:**
- 2 new recommendations
- "Increase Meta budget by 10%" (High Impact, Low Effort)
- "Refresh creative on Campaign XYZ" (Medium Impact, Medium Effort)

**User thinks:**
- "Everything looks good"
- "That Meta budget recommendation makes sense"
- "No urgent issues today"

**Time saved:** 15 minutes vs. logging into each platform separately

---

#### 2. Quick Campaign Check (1 min)
```
1. Click "Campaigns" quick action
2. See list of all campaigns
3. Sort by "Spend" (highest first)
4. Scan top 5 campaigns
5. Check status column (all active ✅)
```

**User thinks:**
- "No paused campaigns"
- "Top campaign still performing well"
- "Everything running as expected"

**Decision:** No action needed today

---

## Journey 3: Weekly Budget Optimization

### Goal: Reallocate budget based on performance

**Duration**: 15-20 minutes  
**Frequency**: Weekly (Monday mornings)

### Steps:

#### 1. Review Last Week Performance (5 min)
```
1. Open dashboard
2. Look at Memory card
3. Note: 
   - Last 7 days: $12,450 spend, $49,800 revenue
   - ROAS: 4.0x
   - Meta Ads: 3.8x ROAS
   - Google Ads: 4.2x ROAS
```

**Insight:** Google Ads performing better than Meta

---

#### 2. Read AI Recommendations (3 min)
```
1. Scroll to Curiosity card
2. Read 3 recommendations:
   a. "Shift 15% budget from Meta to Google" (High Impact)
   b. "Scale Google Search campaigns by 20%" (High Impact)
   c. "Test new audience on Meta" (Medium Impact)
3. Click on recommendation for details (future feature)
```

**User thinks:**
- "AI recommendation aligns with my analysis"
- "High impact suggestions are actionable"
- "Will implement #1 and #2 today"

---

#### 3. Navigate to Campaigns (2 min)
```
1. Click "Campaigns"
2. Filter by "Google Ads"
3. Sort by ROAS (highest first)
4. Identify top 3 campaigns to scale
5. Note campaign IDs
```

---

#### 4. Take Action in Platform (10 min)
```
[Outside OmniFy]
1. Log into Google Ads
2. Find Campaign ID from OmniFy
3. Increase budget by 20%
4. Repeat for top 3 campaigns

5. Log into Meta Ads
6. Reduce budget by 15% on lower ROAS campaigns
```

**Future enhancement:** One-click budget adjustments from OmniFy

---

#### 5. Document Decision (2 min)
```
1. Take screenshot of OmniFy recommendations
2. Save to weekly report folder
3. Note action taken
```

**Success criteria:**
- ✅ Identified optimization opportunity
- ✅ AI validated decision
- ✅ Action taken in platforms
- ✅ Expected impact: 10-15% ROAS increase

---

## Journey 4: Monthly Reporting to CMO

### Goal: Create executive summary of marketing performance

**Duration**: 30 minutes  
**Frequency**: Monthly

### Steps:

#### 1. Gather Data (10 min)
```
1. Open OmniFy dashboard
2. Click "Analytics" (future feature)
3. Select date range: Last 30 days
4. Export summary metrics:
   - Total Spend: $50,000
   - Total Revenue: $200,000
   - Blended ROAS: 4.0x
   - Platform breakdown
5. Screenshot Memory card
6. Screenshot platform breakdown chart
```

---

#### 2. Highlight Wins (5 min)
```
1. Review Oracle risk scores over month
2. Note: Risk decreased from 45% to 15%
3. Review Curiosity recommendations
4. Count: 12 recommendations implemented
5. Calculate: $15,000 additional revenue from optimizations
```

---

#### 3. Create Presentation (15 min)
```
1. Open PowerPoint
2. Slide 1: Overall Performance
   - Use OmniFy Memory card screenshot
   - Add trend arrows
3. Slide 2: Platform Breakdown
   - Use platform comparison data
   - Highlight Google Ads growth
4. Slide 3: AI-Driven Optimizations
   - List top 5 recommendations implemented
   - Show impact ($$ saved/gained)
5. Slide 4: Next Month Focus
   - Based on current Curiosity recommendations
```

**User thinks:**
- "OmniFy made this report 3x faster"
- "Visual data from dashboard is presentation-ready"
- "AI recommendations tell a good story"

**Time saved:** 60 minutes vs. manual data gathering

---

## Journey 5: Creative Performance Analysis

### Goal: Identify underperforming creatives and refresh

**Duration**: 20 minutes  
**Frequency**: Bi-weekly

### Steps:

#### 1. Navigate to Creative Analysis (5 min)
```
1. Click "Analytics" > "Creatives" (future feature)
2. See list of all ad creatives
3. Sort by "Impressions" (highest first)
4. Look for:
   - High impressions + Low CTR = Creative fatigue
   - Declining ROAS over time
```

---

#### 2. AI Creative Analysis (10 min)
```
1. Select creative with fatigue warning
2. Click "Analyze Creative"
3. Review AIDA scores:
   - Attention: 65 (Low)
   - Interest: 70
   - Desire: 75
   - Action: 80
   - Overall: 72.5
4. Read AI recommendations:
   - "Add stronger hook in first 3 seconds"
   - "Include product benefit in headline"
   - "Use more specific CTA"
5. Screenshot for design team
```

---

#### 3. Create Creative Brief (5 min)
```
1. Open Google Doc
2. Title: "Creative Refresh - Campaign XYZ"
3. Include:
   - Current performance data from OmniFy
   - AIDA analysis screenshot
   - AI recommendations
   - Target metrics: CTR 3%+, ROAS 4.5x+
4. Share with design team
```

**Success criteria:**
- ✅ Identified 3 creatives needing refresh
- ✅ AI analysis provides actionable feedback
- ✅ Brief created for design team
- ✅ Expected: 20% CTR improvement

---

## Journey 6: Crisis Response (Campaign Underperforming)

### Goal: Quickly identify and fix underperforming campaign

**Duration**: 10 minutes  
**Frequency**: As needed (alerts)

### Steps:

#### 1. Alert Detection (1 min)
```
1. Log into OmniFy
2. See Oracle card: Risk Score 65% (High) 🔴
3. See alert: "Campaign ABC ROAS dropped to 1.2x"
4. Click alert for details
```

**User thinks:**
- "This needs immediate attention"
- "Good that OmniFy caught this"

---

#### 2. Investigate Issue (4 min)
```
1. Click "Campaigns"
2. Filter to "Campaign ABC"
3. Review metrics:
   - Spend: $500/day (normal)
   - ROAS: 1.2x (was 4.0x last week) 🔴
   - CTR: 0.8% (was 2.5%) 🔴
   - CPC: $2.50 (was $0.50) 🔴
4. Check Oracle analysis:
   - "Creative fatigue detected"
   - "CPC increased 5x in 3 days"
   - "Audience saturation likely"
```

**Root cause identified:** Creative fatigue + audience saturation

---

#### 3. Review AI Recommendations (2 min)
```
1. Curiosity card shows:
   - "URGENT: Pause Campaign ABC immediately" (High Impact)
   - "Refresh creative" (High Impact)
   - "Expand to lookalike audience" (Medium Impact)
```

---

#### 4. Take Action (3 min)
```
1. Log into Meta Ads
2. Pause Campaign ABC
3. Create task: "Rush creative refresh for Campaign ABC"
4. Assign to design team
5. Set reminder: Check back in 2 days
```

**User thinks:**
- "Caught this before wasting more budget"
- "Could have cost $3,500 if not detected"
- "OmniFy paid for itself today"

**Success criteria:**
- ✅ Issue detected early (within 24 hours)
- ✅ Root cause identified quickly
- ✅ Action taken to stop losses
- ✅ Estimated savings: $3,500

---

## 🎯 Journey Success Metrics

| Journey | Time Saved | Key Benefit | User Satisfaction |
|---------|------------|-------------|------------------|
| Initial Setup | 30 min saved | Easy onboarding | 😊 4/5 |
| Daily Check | 15 min saved | Quick insights | 😊 5/5 |
| Weekly Optimization | 20 min saved | Data-driven decisions | 😊 5/5 |
| Monthly Reporting | 60 min saved | Auto reporting | 😊 5/5 |
| Creative Analysis | 30 min saved | AI feedback | 😊 4/5 |
| Crisis Response | Prevents losses | Early detection | 😊 5/5 |

**Total time saved per month**: ~15 hours  
**Value created**: $10,000+ in optimizations + crisis prevention

---

## 🚧 Pain Points & Solutions

### Pain Point 1: API Key Setup Complexity
**Severity**: Medium  
**Frequency**: One-time (setup)

**User quote:** "Getting Meta Ads token was confusing"

**Solutions implemented:**
- ✅ Step-by-step documentation links
- ✅ Test connection button for immediate validation
- ✅ Clear error messages

**Future improvements:**
- OAuth flow integration (no manual token copy)
- Video tutorials for each platform

---

### Pain Point 2: No One-Click Actions
**Severity**: Medium  
**Frequency**: Weekly

**User quote:** "I still need to log into each platform to make changes"

**Current state:** Recommendations provided, but action taken externally

**Future improvements:**
- One-click budget adjustments
- Campaign pause/resume from OmniFy
- Automated rules engine

---

### Pain Point 3: Limited Historical Data View
**Severity**: Low  
**Frequency**: Monthly

**User quote:** "I want to see trends over 90 days"

**Current state:** Default 30-day view

**Future improvements:**
- Custom date range selector
- Comparison modes (vs. last period, vs. last year)
- Historical trend charts

---

## 📱 Mobile User Journey (Future)

### Goal: Quick performance check on mobile

**Duration**: 1 minute  
**Frequency**: Daily (on-the-go)

```
1. Open OmniFy mobile app
2. See dashboard summary card
3. Swipe for platform breakdown
4. Tap alert for details
5. Mark as "will review later"
```

**Benefit:** Monitor performance anywhere, anytime

---

## 🎓 Learning Curve

### New User Proficiency Timeline

**Day 1:** Setup & first sync (30 min)
- Configure 1-2 platforms
- Understand dashboard layout
- First data sync

**Week 1:** Daily checks (2-3 min/day)
- Comfortable with dashboard navigation
- Reading metrics correctly
- Understanding recommendations

**Week 2:** Taking actions (20 min/week)
- Implementing AI recommendations
- Making budget decisions
- Using campaigns page

**Month 1:** Power user (10 min/day)
- Creating reports
- Advanced filtering
- Proactive optimization

**Proficiency achieved:** 80% of users become proficient within 2 weeks

---

**Last Updated**: January 2025
