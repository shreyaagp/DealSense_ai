"""
Synthetic enterprise sales knowledge base.
All data is fictional and for simulation/training purposes only.
"""

DEAL_TRANSCRIPTS = [
    {
        "id": "transcript_001",
        "title": "Won Deal - CFO SaaS Negotiation - Financial Services",
        "content": """
DEAL TRANSCRIPT: Meridian Capital - CRM Platform Sale
Outcome: WON | Deal Size: $2.4M | Industry: Financial Services

[STAGE: Discovery]
CFO (Sarah Chen): "Your pricing is 40% above what we paid for our last vendor. Walk me through why I should even continue this conversation."
REP: "That's exactly the right question, Sarah. Our clients in financial services typically see 18-month ROI. But more importantly, what's the cost of your current system's downtime? Last quarter's outage at three of your competitors cost them an average of $8M each."
CFO: "We had two outages. Combined cost was around $3.2M."
REP: "So over 5 years, that's potentially $16M in risk. Our uptime SLA is 99.99% with financial penalties if we miss it. Would it help to model that against our contract cost?"

[STAGE: Objection - Budget]
CFO: "Even if I accept your reliability argument, I still need to justify the delta to my board. We have a $1.8M budget ceiling."
REP: "I understand. Let me propose a phased approach. We start with core modules at $1.6M, which fits your budget. Modules two and three activate in years two and three as you demonstrate ROI internally. You never exceed budget and you control the pace."
CFO: "That's more workable. What guarantees do I have on the year two pricing?"
REP: "We'll lock year two and three pricing today with a 3% annual cap. That's in writing."

[STAGE: Closing]
CFO: "If security passes CTO review and legal approves the SLA language, we're ready to move."
TURNING POINT: Rep reframed cost as risk mitigation, not expense. Phased pricing removed budget ceiling objection.
""",
        "metadata": {
            "industry": "financial_services",
            "deal_size": "enterprise",
            "persona": "CFO",
            "objection_type": "budget",
            "outcome": "won",
            "stage": "closing",
            "difficulty": "hard",
            "document_type": "transcript"
        }
    },
    {
        "id": "transcript_002",
        "title": "Lost Deal - CTO Technical Objection - Healthcare",
        "content": """
DEAL TRANSCRIPT: Northgate Health Systems - Data Platform Sale
Outcome: LOST | Deal Size: $890K | Industry: Healthcare

[STAGE: Technical Review]
CTO (Marcus Webb): "Your architecture uses a shared database model. We process PHI. That's a non-starter under HIPAA."
REP: "We're fully HIPAA compliant, Marcus."
CTO: "Being compliant doesn't mean your architecture is right for us. I need tenant isolation. Does your system provide dedicated database instances per client?"
REP: "Our security team can walk you through our compliance documentation."
CTO: "That's not what I asked. Dedicated instances. Yes or no?"
REP: "I'd need to check with our technical team."

[STAGE: Objection - Architecture]
CTO: "While you're checking - your API latency documentation shows 200ms P99. Our clinical workflows need under 50ms. How do you address that?"
REP: "We can optimize for your use case."
CTO: "You don't know if you have dedicated instances and you can't commit to latency. I'm not comfortable moving forward."

FAILURE ANALYSIS: Rep couldn't answer technical questions in real-time. CTO interpreted hesitation as product gaps. Lost to competitor who had CTO-facing technical architect in meeting.
LESSON: Bring technical co-seller to CTO meetings. Know your architecture cold. Never say "I'll check" to binary technical questions.
""",
        "metadata": {
            "industry": "healthcare",
            "deal_size": "mid_market",
            "persona": "CTO",
            "objection_type": "technical_architecture",
            "outcome": "lost",
            "stage": "technical_review",
            "difficulty": "hard",
            "document_type": "transcript"
        }
    },
    {
        "id": "transcript_003",
        "title": "Won Deal - Procurement Discount Pressure - Manufacturing",
        "content": """
DEAL TRANSCRIPT: Apex Industrial Group - ERP Implementation
Outcome: WON | Deal Size: $3.1M | Industry: Manufacturing

[STAGE: Procurement Negotiation]
PROCUREMENT (David Okafor): "We've gotten quotes from three vendors. You're the most expensive by 22%. Match the lowest bid or we go elsewhere."
REP: "David, I appreciate the directness. Can I ask - what was the lowest bid from?"
PROCUREMENT: "TechForce. $2.4M."
REP: "TechForce's implementation timeline for a company your size is typically 18-24 months. Ours is 9-12. At $180K per month in operational efficiency gains you've modeled, that's a 9-month difference worth $1.62M. The math actually favors us."
PROCUREMENT: "That's your implementation estimate, not theirs."
REP: "Fair. Let's use the average of both. Even at 6 months difference, that's over $1M in value that doesn't appear in the contract price comparison."

[STAGE: Discount Defense]
PROCUREMENT: "I still need something to show my VP. Give me 10%."
REP: "I can't do 10% without losing the project team that makes our timeline possible. Here's what I can do: prepay discount of 4% if you wire by quarter end, extended warranty year four at no cost, and dedicated customer success manager for year one. Total value add: $340K."
PROCUREMENT: "Let me take that to my VP."
OUTCOME: Won at full price with value-adds. Maintained margin.
TURNING POINT: Reframed price comparison to include implementation timeline value. Substituted value-adds for discount.
""",
        "metadata": {
            "industry": "manufacturing",
            "deal_size": "enterprise",
            "persona": "procurement",
            "objection_type": "price_discount",
            "outcome": "won",
            "stage": "negotiation",
            "difficulty": "medium",
            "document_type": "transcript"
        }
    },
    {
        "id": "transcript_004",
        "title": "Won Deal - Vendor Lock-in Objection - Technology",
        "content": """
DEAL TRANSCRIPT: Stratus Cloud Technologies - API Platform Sale
Outcome: WON | Deal Size: $1.7M | Industry: Technology

[STAGE: Legal/Procurement Review]
CTO (Priya Nair): "Your proprietary data format creates lock-in. If we want to switch in three years, we're held hostage."
REP: "That's a legitimate concern and one I respect you raising. Let me address it directly."
CTO: "Please do."
REP: "First, all your data exports in open formats - JSON, CSV, Parquet. We support standard REST APIs. Migration packages exist for all major competitors. But more importantly, let me show you our customer retention data - 94% of customers renew because they choose to, not because they can't leave."
CTO: "Why do they stay if leaving is easy?"
REP: "Because the switching cost is time, not technical. Our workflow automation would take 6 months to rebuild anywhere. That's a value moat, not a technical one."

[STAGE: Contractual Protection]
CTO: "I want data portability rights in the contract."
REP: "Done. We'll add a data portability clause with 30-day guaranteed export window and we'll provide migration documentation for three named competitors. That's something I can commit to right now."
TURNING POINT: Acknowledged lock-in concern, reframed as value retention vs. technical trap. Offered contractual portability to neutralize the objection.
""",
        "metadata": {
            "industry": "technology",
            "deal_size": "mid_market",
            "persona": "CTO",
            "objection_type": "vendor_lock_in",
            "outcome": "won",
            "stage": "legal_review",
            "difficulty": "medium",
            "document_type": "transcript"
        }
    },
    {
        "id": "transcript_005",
        "title": "Lost Deal - Implementation Risk - Retail",
        "content": """
DEAL TRANSCRIPT: Cascade Retail Group - Inventory Management Platform
Outcome: LOST | Deal Size: $670K | Industry: Retail

[STAGE: Risk Assessment]
CFO (Linda Park): "Your last three retail implementations - what were the actual go-live dates vs. projected?"
REP: "I don't have those specific numbers with me but our implementation record is strong."
CFO: "I pulled public case studies. Two were 6 months late, one was on time. That's a 67% late rate."
REP: "Every implementation is unique. We've learned a lot."
CFO: "We're going into holiday season. A 6-month delay means we miss peak. Can you guarantee on-time delivery with financial penalties?"
REP: "We'd need to discuss penalty structures with our contracts team."
CFO: "You can't answer on implementation history and won't commit to penalties. We're done."

FAILURE ANALYSIS: Rep was unprepared for historical performance questions. Inability to defend implementation record or offer financial accountability was fatal.
LESSON: Know your case studies. Prepare implementation success metrics. Have penalty clause authority or bring someone who does.
""",
        "metadata": {
            "industry": "retail",
            "deal_size": "mid_market",
            "persona": "CFO",
            "objection_type": "implementation_risk",
            "outcome": "lost",
            "stage": "risk_assessment",
            "difficulty": "hard",
            "document_type": "transcript"
        }
    },
    {
        "id": "transcript_006",
        "title": "Won Deal - Security Deep Dive - Government",
        "content": """
DEAL TRANSCRIPT: Regional Government Agency - Workflow Platform
Outcome: WON | Deal Size: $4.2M | Industry: Government

[STAGE: Security Review]
CTO (James Okonkwo): "FedRAMP authorization - what level and when was it granted?"
REP: "FedRAMP Moderate, authorized in 2022, renewed 2024. The full package is available under NDA. We also hold StateRAMP High."
CTO: "Data residency. Where does citizen data physically reside?"
REP: "US-only data centers, GovCloud partitioned. Dedicated single-tenant option available for your agency. No data ever leaves US jurisdiction."
CTO: "Zero-trust architecture?"
REP: "Yes. We implement NIST 800-207 compliant zero-trust. Identity verification on every API call. Microsegmentation at the workload level. I can provide our architecture diagram for your review."
CTO: "Most vendors stumble on zero-trust details. You clearly know your product."

[STAGE: Procurement]
PROCUREMENT: "Four other vendors quoted 30-35% lower."
REP: "None of them have FedRAMP Moderate. Getting authorization post-award costs $800K to $1.2M and takes 18 months. Our compliance is baked in."
PROCUREMENT: "We hadn't factored that."
TURNING POINT: Technical depth on security impressed CTO. Compliance cost analysis neutralized price objection.
""",
        "metadata": {
            "industry": "government",
            "deal_size": "enterprise",
            "persona": "CTO",
            "objection_type": "security",
            "outcome": "won",
            "stage": "technical_review",
            "difficulty": "hard",
            "document_type": "transcript"
        }
    },
]

COMPETITOR_INTEL = [
    {
        "id": "comp_001",
        "title": "Competitor Analysis: TechForce Platform",
        "content": """
COMPETITOR: TechForce Platform
Strengths: Lower initial price point (avg 20-25% below market), strong marketing, fast sales cycle
Weaknesses: 
- Implementation timelines routinely 50-100% over estimate (documented in customer reviews)
- No FedRAMP authorization (disqualifies from government deals)
- Shared multi-tenant database only - no dedicated instances
- Limited API rate: 100 req/min vs our 10,000 req/min
- No native data export - requires paid migration service
- Customer support: business hours only, no 24/7 SLA

Battle card talking points:
- When prospect mentions TechForce pricing: "TechForce's implementation cost overruns average 35% above contract. When you factor that in, their TCO exceeds ours."
- When prospect mentions TechForce references: "Ask them specifically about go-live dates vs. projected. Their NPS for implementation is 22, ours is 71."
- Win rate vs TechForce: 67% when we engage technical decision makers early

Ideal counter-positioning: Lead with implementation risk, uptime SLA comparison, and compliance gaps.
""",
        "metadata": {
            "industry": "all",
            "deal_size": "all",
            "persona": "all",
            "objection_type": "competitive",
            "outcome": "reference",
            "stage": "all",
            "difficulty": "medium",
            "document_type": "competitor_intel"
        }
    },
    {
        "id": "comp_002",
        "title": "Competitor Analysis: Nexus Enterprise Suite",
        "content": """
COMPETITOR: Nexus Enterprise Suite
Strengths: Strong brand recognition, large customer base, robust feature set, good enterprise references
Weaknesses:
- Significant implementation complexity: avg 18-24 months for enterprise
- High professional services dependency: avg customer spends 60% of license cost on PS annually
- Legacy architecture: monolithic, not cloud-native, struggles with modern integrations
- No usage-based pricing: all contracts are seat-based, expensive for variable-use cases
- Support model: tiered with premium support costing additional 22% annually

Battle card talking points:
- When prospect uses Nexus as benchmark: "Nexus's professional services lock-in means your total cost in year 3 is typically 2.8x the initial contract. We have fixed-price implementation."
- When prospect mentions Nexus references: "Ask how many of their references are on the latest version. Upgrade paths from legacy Nexus are notoriously painful."
- Win rate vs Nexus: 45% overall, 72% when deal size under $2M and CTO is primary buyer

Ideal counter-positioning: Modern architecture, faster implementation, predictable total cost of ownership.
""",
        "metadata": {
            "industry": "all",
            "deal_size": "enterprise",
            "persona": "CTO",
            "objection_type": "competitive",
            "outcome": "reference",
            "stage": "all",
            "difficulty": "hard",
            "document_type": "competitor_intel"
        }
    },
]

OBJECTION_PLAYBOOKS = [
    {
        "id": "playbook_001",
        "title": "Budget Objection Playbook",
        "content": """
OBJECTION: "Your price is too high" / "We don't have budget" / "The competition is cheaper"

CATEGORY: Budget / Pricing

WINNING RESPONSE FRAMEWORKS:

Framework 1 - ROI Reframe:
"I hear you on price. Let's separate cost from value for a moment. What does your current problem cost you annually? [Wait for answer]. Our solution typically reduces that by 40-60%. At what point does the investment become justified by the savings?"

Framework 2 - TCO Comparison:
"The purchase price is one line item. Implementation, ongoing support, upgrade costs, and productivity loss during transitions are others. When we model full 5-year TCO including all those factors, how do we compare to alternatives?"

Framework 3 - Phased Approach:
"What if we started with the highest-ROI modules and phased in the rest as you demonstrate value internally? We can structure a deal that fits your current budget ceiling and grows as you see results."

Framework 4 - Risk Quantification:
"I want to understand the cost of inaction. If you don't solve [specific problem] in the next 12 months, what is the financial impact? [Calculate]. Our contract cost may be less than the risk of delay."

NEVER SAY:
- "I can give you a discount" (before understanding their true position)
- "Let me check what I can do" (signals weakness and lack of authority)
- "We're flexible on pricing" (devalues your product)

ESCALATION: If budget is genuinely fixed, explore: value-adds vs. discount, phased contracts, annual vs. multi-year tradeoffs, pilot programs.
""",
        "metadata": {
            "industry": "all",
            "deal_size": "all",
            "persona": "CFO",
            "objection_type": "budget",
            "outcome": "reference",
            "stage": "negotiation",
            "difficulty": "medium",
            "document_type": "playbook"
        }
    },
    {
        "id": "playbook_002",
        "title": "Security Objection Playbook",
        "content": """
OBJECTION: "We have security concerns" / "How do you handle data privacy?" / "Our security team won't approve this"

CATEGORY: Security / Compliance

WINNING RESPONSE FRAMEWORKS:

Framework 1 - Specificity First:
"Security is critical and I want to address your specific concerns directly. Can you tell me exactly what your security team's requirements are? I want to answer the actual questions, not generic ones."

Framework 2 - Credentials Lead:
"Let me share our security posture upfront: [List relevant certifications - SOC2 Type II, ISO 27001, FedRAMP, HIPAA, PCI-DSS as applicable]. We also have a dedicated trust page and will provide our security documentation under NDA."

Framework 3 - Architecture Transparency:
"I can walk you through our architecture at whatever level of detail your team needs - from high-level overview to specific API security controls. We have nothing to hide and everything to demonstrate."

Framework 4 - Shared Responsibility:
"Security is a shared model. Let me show you where we take responsibility and where we empower your team to apply your own controls. You maintain data sovereignty throughout."

CTO-SPECIFIC RESPONSES:
- Zero-trust questions: Know NIST 800-207, be able to describe your implementation specifically
- Encryption: Specify at-rest (AES-256) and in-transit (TLS 1.3) standards
- Penetration testing: Have results or remediation timeline available
- Data residency: Know exactly where data is stored and why

RED FLAGS TO AVOID:
- Vague compliance claims without specifics
- "We'll connect you with our security team" as deflection
- Not knowing your own architecture

ESCALATION: Offer security assessment call with your CISO/security architect. Provide third-party penetration test results.
""",
        "metadata": {
            "industry": "all",
            "deal_size": "all",
            "persona": "CTO",
            "objection_type": "security",
            "outcome": "reference",
            "stage": "technical_review",
            "difficulty": "hard",
            "document_type": "playbook"
        }
    },
    {
        "id": "playbook_003",
        "title": "Vendor Lock-in Objection Playbook",
        "content": """
OBJECTION: "We're worried about vendor lock-in" / "What if we want to switch later?" / "Your proprietary format traps us"

CATEGORY: Vendor Lock-in / Flexibility

WINNING RESPONSE FRAMEWORKS:

Framework 1 - Acknowledge and Reframe:
"That's a smart concern and one I respect you raising. Let me separate two types of lock-in: technical lock-in (can't extract your data) vs. value lock-in (choosing to stay because it works). We have zero technical lock-in. The value lock-in - yes, we hope you'll find it hard to leave because we're delivering results."

Framework 2 - Portability Demonstration:
"Let me show you our data export capabilities. [Demonstrate open format exports]. Every piece of your data, in standard formats, available on demand. We can also provide a migration package for any named competitor."

Framework 3 - Contractual Guarantees:
"We'll put data portability in the contract. Thirty-day guaranteed export window, documented API access, and migration assistance. Your data is your data. Period."

Framework 4 - Ecosystem vs. Trap:
"Our integrations with [list their current tools] mean you're gaining capabilities without replacing infrastructure. You're adding a layer, not locking into a replacement ecosystem."

SUPPORTING DATA:
- 94% renewal rate (customers choose to stay)
- Open API standards: REST, GraphQL, webhooks
- Standard data formats: JSON, CSV, Parquet, XML
- Named competitor migration documentation available

NEVER CONCEDE:
- That your product creates "real" lock-in
- That switching would be technically difficult (if it isn't)

ESCALATION: Add explicit data portability clause to contract. Offer to escrow API documentation.
""",
        "metadata": {
            "industry": "all",
            "deal_size": "all",
            "persona": "CTO",
            "objection_type": "vendor_lock_in",
            "outcome": "reference",
            "stage": "legal_review",
            "difficulty": "medium",
            "document_type": "playbook"
        }
    },
    {
        "id": "playbook_004",
        "title": "Implementation Risk Objection Playbook",
        "content": """
OBJECTION: "We're worried about implementation risk" / "What's your track record?" / "We've been burned before"

CATEGORY: Implementation Risk

WINNING RESPONSE FRAMEWORKS:

Framework 1 - Track Record Specificity:
"Let me give you specific numbers rather than general claims. Our average time-to-value for [their industry] is [X] weeks. Our on-time implementation rate is 89%. The 11% late cases averaged 3 weeks over - not months. I can share specific references from your industry."

Framework 2 - Risk Mitigation Structure:
"We've learned from every implementation. Here's what we put in place: dedicated project manager, weekly executive sponsor check-ins, clear milestone definitions with go/no-go criteria, and a guaranteed rollback capability at any phase."

Framework 3 - Financial Accountability:
"We're willing to put performance in the contract. If we miss agreed milestones, you receive service credits. If we miss go-live by more than [X] weeks, you have termination rights. We put our revenue at risk because we're confident in delivery."

Framework 4 - Phased Risk Reduction:
"Rather than a big-bang implementation, we recommend a phased approach. Phase 1 is a 6-week pilot with defined success criteria. If it works, we proceed. If it doesn't, you've spent [minimal cost] and learned something. Your risk is bounded."

SUPPORTING DATA TO KNOW:
- Industry-specific implementation success rates
- Reference customers willing to discuss timeline
- Average time-to-go-live by company size
- Post-implementation customer satisfaction scores

NEVER SAY:
- "Every implementation is different" (sounds like excuse)
- "We'll figure it out" (no confidence)
- "Our team is great" (unsubstantiated)

ESCALATION: Offer implementation guarantee with financial penalties. Provide client references for direct conversations.
""",
        "metadata": {
            "industry": "all",
            "deal_size": "all",
            "persona": "CFO",
            "objection_type": "implementation_risk",
            "outcome": "reference",
            "stage": "risk_assessment",
            "difficulty": "hard",
            "document_type": "playbook"
        }
    },
]

BUYER_PERSONAS = [
    {
        "id": "persona_001",
        "title": "CFO Buyer Persona Profile",
        "content": """
PERSONA: Chief Financial Officer (CFO)

CORE MOTIVATIONS:
- Protect and grow shareholder value
- Minimize financial risk
- Demonstrate fiscal responsibility to board
- Hit quarterly/annual cost targets
- Ensure predictable, budgetable spend

PRIMARY OBJECTION PATTERNS:
1. Price anchoring: Always references cheaper alternatives first
2. ROI demand: Wants specific numbers, not vague value claims
3. Budget ceiling: Has hard limits and won't easily exceed them
4. Risk aversion: Will surface implementation cost overruns, hidden fees
5. Payback period fixation: Wants to know when they break even

COMMUNICATION STYLE:
- Numbers-focused: Respond with data, not narrative
- Skeptical by default: Don't expect enthusiasm for your claims
- Time-efficient: Get to the point; don't over-explain
- Formal: Professional tone, not casual

PRESSURE TACTICS:
- "We have three other vendors who are cheaper"
- "My board approved X, not X+40%"
- "If you can't make this work within budget, we have options"
- "Your competitor gave me a 15% discount immediately"
- "I need this to pay for itself in 18 months, not 3 years"

WHAT WINS CFOs:
- Specific ROI numbers from comparable companies
- Risk quantification (cost of inaction)
- Flexible payment structures that fit their model
- Implementation guarantees with financial accountability
- References from peer CFOs

WHAT LOSES CFOs:
- Vague value claims without numbers
- Inability to defend pricing with data
- No flexibility on structure (only discount)
- Ignoring their specific budget constraints
- Not knowing their industry's financial benchmarks

NEGOTIATION STYLE: Will use competitive pressure, delay tactics, and budget ceiling claims. Often has more flexibility than they initially reveal. Responds to structured value-adds over straight discounts.
""",
        "metadata": {
            "industry": "all",
            "deal_size": "all",
            "persona": "CFO",
            "objection_type": "all",
            "outcome": "reference",
            "stage": "all",
            "difficulty": "hard",
            "document_type": "persona_profile"
        }
    },
    {
        "id": "persona_002",
        "title": "CTO Buyer Persona Profile",
        "content": """
PERSONA: Chief Technology Officer (CTO)

CORE MOTIVATIONS:
- Technical excellence and architecture integrity
- Team productivity and developer experience
- Security and compliance (protecting the company)
- Scalability for future growth
- Avoid being accountable for a failed tech decision

PRIMARY OBJECTION PATTERNS:
1. Architecture interrogation: Asks deep technical questions to expose knowledge gaps
2. Security probing: Will find the weakest point in your security claims
3. Scalability stress-testing: "What happens at 10x our current load?"
4. Lock-in concerns: Proprietary formats, API compatibility, data portability
5. Integration complexity: "How does this work with our existing stack?"

COMMUNICATION STYLE:
- Technical precision: Respond with specifics, not marketing language
- Respect earned: Won't respect you unless you know your product cold
- Direct: Will call out evasive or vague answers immediately
- Skeptical of vendor claims: Wants evidence, not assertions

PRESSURE TACTICS:
- "Your competitor uses open-source components and doesn't create lock-in"
- "I need dedicated infrastructure, not shared multi-tenant"
- "Walk me through your architecture for handling X at scale"
- "What's your P99 latency under our expected load?"
- "Your documentation says X but I've seen reports that contradict that"

WHAT WINS CTOs:
- Deep product knowledge (know your architecture cold)
- Technical credibility established early
- Honest answers including limitations
- Security documentation and compliance specifics
- Peer CTO references in their industry

WHAT LOSES CTOs:
- Saying "I'll check" to basic technical questions
- Marketing language for technical questions
- Not knowing your uptime, latency, or architecture
- Bringing sales-only team to technical meeting
- Overpromising technical capabilities

NEGOTIATION STYLE: Not primarily price-focused but will align with CFO concerns. More interested in technical fit and risk reduction. Will block a deal if technical requirements aren't met, regardless of price.
""",
        "metadata": {
            "industry": "all",
            "deal_size": "all",
            "persona": "CTO",
            "objection_type": "all",
            "outcome": "reference",
            "stage": "all",
            "difficulty": "hard",
            "document_type": "persona_profile"
        }
    },
    {
        "id": "persona_003",
        "title": "Procurement Buyer Persona Profile",
        "content": """
PERSONA: Procurement Officer / VP of Procurement

CORE MOTIVATIONS:
- Get the lowest possible price (measured on savings)
- Demonstrate negotiating value to internal stakeholders
- Manage vendor relationships and contracts
- Reduce organizational vendor risk
- Create competitive pressure regardless of vendor preference

PRIMARY OBJECTION PATTERNS:
1. Discount demand: Will ask for significant discount as opening position
2. Competitive leverage: Will use real or implied competitive bids as pressure
3. Delay tactics: "We need more time to evaluate" often means "give us more discount"
4. Unbundling: Will try to remove features/services to reduce price
5. Contract term pressure: Shorter terms for more flexibility (leverage to renegotiate)

COMMUNICATION STYLE:
- Transactional: This is business, not personal
- Strategic pressure: Every statement is a negotiating move
- Non-committal: Won't show enthusiasm even if stakeholders are excited
- Process-focused: Will cite procurement policy to justify positions

PRESSURE TACTICS:
- "We have a policy to get at least three competitive bids"
- "Your competitor came in at [X]% lower - you need to match"
- "I need at least 15% off to get internal approval"
- "We're not in a rush - we can extend our evaluation another quarter"
- "Our legal team has issues with your standard contract terms"

WHAT WINS PROCUREMENT:
- Understanding they're measured on savings (give them something to show)
- Value-adds instead of straight discounts (protects your price point)
- Fast close incentives (quarter-end urgency works)
- Structured payment terms that help their budget model
- Flexibility on contract terms that don't affect your margin

WHAT LOSES PROCUREMENT:
- Refusing to engage on price at all
- Giving immediate large discounts (signals you had room all along)
- Matching lowest bid without defending value (race to the bottom)
- Showing desperation for the deal
- Ignoring their process and going around them

NEGOTIATION STYLE: Professional negotiator. Uses competitive pressure, delay, and authority constraints. Usually has more flexibility than stated. Respects structured counter-proposals more than emotional arguments.
""",
        "metadata": {
            "industry": "all",
            "deal_size": "all",
            "persona": "procurement",
            "objection_type": "price_discount",
            "outcome": "reference",
            "stage": "negotiation",
            "difficulty": "medium",
            "document_type": "persona_profile"
        }
    },
]

# Combine all knowledge base documents
ALL_DOCUMENTS = DEAL_TRANSCRIPTS + COMPETITOR_INTEL + OBJECTION_PLAYBOOKS + BUYER_PERSONAS
