# Subagent Prompting Guide

## Critical Context Principle
Subagents start with ZERO context about the current project, problem, or conversation. They cannot ask clarifying questions - they work with what you provide. The quality of their output directly correlates with the completeness of your prompt.

**Golden Rule**: Include everything a new team member would need to understand and solve the problem independently.

---

## 🔍 Research Specialist (@research-specialist)

### Purpose
Gathers information, identifies risks, finds documentation, analyzes competitors, researches best practices.

### Essential Context to Include

**For Technical Research:**
```
@research-specialist: Research [specific technology/approach]

Context:
- What we're building: [system description and purpose]
- Current stack: [languages, frameworks, infrastructure]
- Specific challenge: [what problem needs solving]
- Scale requirements: [users, data volume, performance needs]
- Constraints: [budget, timeline, team expertise]

Research needed:
- [Specific question 1]
- [Specific question 2]
- Find potential pitfalls with [approach]
- Compare [option A] vs [option B]

Success criteria: [what constitutes useful findings]
Timeline: [when findings are needed]
```

**For Competitive Analysis:**
```
@research-specialist: Analyze competitors in [market segment]

Context:
- Our product: [what we offer]
- Target market: [who we serve]
- Current pricing: [our model]
- Key differentiators: [what makes us unique]

Research needed:
- Competitor pricing models (normalized)
- Feature comparisons
- Market positioning strategies
- Customer complaints/pain points
- Hidden costs or limitations

Focus on: [specific aspects most important to decision]
```

**For Security/Risk Research:**
```
@research-specialist: Research security implications of [technology/approach]

Context:
- System type: [web app, API, mobile, etc.]
- Sensitive data: [PII, financial, health, etc.]
- Compliance needs: [GDPR, HIPAA, SOC2, etc.]
- Current security measures: [what's in place]
- Risk tolerance: [startup vs enterprise]

Research needed:
- Known vulnerabilities
- Best practices for [specific scenario]
- Compliance requirements
- Incident examples and recovery times
```

### Key Phrases That Improve Results
- "Find potential pitfalls and gotchas"
- "Look for recovery procedures and time estimates"
- "Compare normalized costs including hidden fees"
- "Find real-world implementation examples"
- "Identify what could go catastrophically wrong"

---

## 🎯 Strategic Executive (@strategic-executive)

### Purpose
Provides strategic guidance, analyzes trade-offs, recommends directions, assesses market opportunities.

### Essential Context to Include

**For Technical Strategy:**
```
@strategic-executive: Need strategic guidance on [decision]

Current situation:
- Business context: [revenue, users, market position]
- Technical state: [current architecture, tech debt]
- Team: [size, skills, capacity]
- Resources: [budget, timeline constraints]

Strategic decision needed:
- Option A: [description, cost, timeline]
- Option B: [description, cost, timeline]
- Key trade-offs: [what we're optimizing for]

Success metrics: [how we measure success]
Risk tolerance: [startup scrappy vs enterprise stable]
Time horizon: [when decision impacts felt]
```

**For Market/Business Strategy:**
```
@strategic-executive: Evaluate market opportunity for [initiative]

Business context:
- Current position: [market share, revenue, growth]
- Core competency: [what we do well]
- Target market: [who we serve]
- Competition: [key players and dynamics]

Opportunity details:
- Market segment: [description]
- Investment required: [time, money, people]
- Expected return: [revenue, users, strategic value]
- Risks: [execution, market, competitive]

Strategic priorities: [growth vs profit vs market share]
Decision timeline: [when we need to commit]
```

### Key Context Elements
- Always include current state (business + technical)
- Specify constraints (time, money, people)
- Define success criteria explicitly
- State risk tolerance clearly
- Provide decision timeline

---

## 🏗️ Principal Engineering Advisor (@principal-engineering-advisor)

### Purpose
Provides deep technical guidance, architectural recommendations, performance strategies, best practices.

### Essential Context to Include

**For Architecture Design:**
```
@principal-engineering-advisor: Design architecture for [system type]

Technical context:
- Current architecture: [monolith/microservices, tech stack]
- Scale requirements: [current vs projected load]
- Performance needs: [latency, throughput targets]
- Team: [size, experience level, strengths]
- Infrastructure: [cloud provider, tooling]

Specific challenge:
- Problem: [detailed description]
- Current approach: [what we've tried]
- Constraints: [technical, time, expertise]
- Integration needs: [existing systems]

Non-functional requirements:
- Availability: [uptime needs]
- Security: [requirements]
- Compliance: [standards]
- Budget: [infrastructure costs]
```

**For Performance Optimization:**
```
@principal-engineering-advisor: Optimize [system component] performance

Current state:
- Architecture: [relevant components]
- Performance metrics: [current latency, throughput]
- Bottlenecks: [identified issues]
- Load patterns: [traffic shape, peak times]
- Infrastructure: [servers, database, cache]

Performance targets:
- Required: [specific metrics]
- Current gap: [where we fall short]
- User impact: [why this matters]

Constraints:
- Cannot change: [fixed elements]
- Budget: [for new infrastructure]
- Timeline: [when improvements needed]
```

**For Technical Debt/Refactoring:**
```
@principal-engineering-advisor: Refactoring strategy for [system/component]

Legacy context:
- Current state: [architecture, tech stack, age]
- Pain points: [specific problems]
- Technical debt: [known issues]
- Business impact: [why refactoring matters]

Team context:
- Available developers: [number and skills]
- Domain knowledge: [who knows what]
- Other priorities: [competing work]

Constraints:
- Must maintain: [what can't break]
- Rollback needs: [recovery requirements]
- Timeline: [delivery expectations]
```

### Key Technical Details
- Always include current architecture
- Specify scale and performance needs
- State team capabilities honestly
- List integration requirements
- Define "cannot change" constraints

---

## 🚨 Common Prompting Mistakes to Avoid

### ❌ Too Vague
```
@research-specialist: Research WebSocket best practices
```

### ✅ Properly Contextualized
```
@research-specialist: Research WebSocket best practices for real-time chat

Context:
- Building: Real-time chat for customer support
- Scale: 10k concurrent connections expected
- Stack: Node.js backend, React frontend
- Constraints: Single server initially, AWS hosting

Research needed:
- Scaling strategies for 10k+ connections
- Security best practices for WebSocket
- Reconnection and error handling patterns
- Performance optimization techniques
```

### ❌ Missing Current State
```
@strategic-executive: Should we use microservices?
```

### ✅ Complete Context
```
@strategic-executive: Evaluate microservices migration

Current situation:
- Monolithic Django app, 5 years old
- 50k daily active users, growing 20% monthly
- Team: 6 developers, strong Python, no DevOps
- Pain points: Deploy time (2 hours), scaling specific features

Investment required:
- 6-month migration estimate
- Need to hire 2 DevOps engineers
- $30k/month additional infrastructure

Success criteria: Reduce deploy time, independent scaling
Risk tolerance: Medium - need to maintain uptime
```

---

## 📋 Pre-Flight Checklist

Before invoking any subagent, verify you've included:

- [ ] **What** we're building/solving
- [ ] **Why** this matters (business impact)
- [ ] **Current** state (technical and business)
- [ ] **Constraints** (time, money, technical)
- [ ] **Success** criteria (how we measure)
- [ ] **Specific** questions to answer
- [ ] **Timeline** for findings/decision

---

## 🎯 Quick Reference

**Research Specialist** needs:
- Current technical context
- Specific research questions
- Risk areas to investigate
- Success criteria for findings

**Strategic Executive** needs:
- Business and technical context
- Options with trade-offs
- Resource constraints
- Success metrics
- Risk tolerance

**Principal Engineer** needs:
- Detailed technical context
- Scale and performance requirements
- Team capabilities
- Integration constraints
- Non-functional requirements

Remember: Subagents cannot ask for clarification. Front-load your prompts with context to get expert-level outputs on the first pass.
