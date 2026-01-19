# GESTURE — SENIOR SOFTWARE ENGINEERING - REAL WORLD ASSESSMENT

Time Expectation: 3 Hours or less (total for both part 1 and part 2) 

Allowed Stack: JavaScript / TypeScript, Node.js, React (optional), Python
(Diagrams, pseudocode, and written explanation are encouraged.)

Purpose
Gesture builds emotionally intelligent, data-driven systems that connect brands and consumers through tangible experiences. At the core of this is our own propriatary AI technology, which powers personalization, experimentation, and measurement across both consumer and our enterprise products.

This assessment is designed to understand how you think about systems, not to test framework knowledge, and is intentionally designed to reflect the kinds of architectural and product-driven challenges we work on at Gesture. It’s not a test of syntax or speed — it’s a way for us to understand how you reason about systems, tradeoffs, and applied intelligence.

### The assessment has two parts:

Part 1 focuses on system design, experimentation thinking, and decision logic.

Part 2 is a small, targeted prototype to demonstrate how your ideas translate into structure.

We expect this should take you no more than approximately 3 hours or less to complete, and we’re happy for you to time-box it in a way that works for you.

Please let us know if you have any questions. We’re looking forward to reviewing your approach.

#
## 🟦 PART 1 — SYSTEMS THINKING & DESIGN (Primary Signal)

#### Prompt

Design a conversational or interactive system that:
- Educates users about a product or service
- Identifies high-intent users and captures actionable signals
- Improves over time based on usage and feedback
- Can integrate with external systems (e.g. CRM, analytics, internal tools)

#### Your Task
Provide a short written design covering:
Architecture
- High-level system architecture
- Core components (frontend, backend, logic/AI layer, data storage)
- How interactions are logged and reused
- How external integrations would work
  
#### Experimentation & Measurement
- How system behavior would be tested and improved over time
- What metrics matter and why
- How to avoid misleading or noisy experiments

#### Decision Logic
- How free-form user input maps to structured decisions
- Rules vs models: where each is appropriate
- How the system evolves safely over time
  
#### Tradeoffs & Risks
- Key technical risks
- Product or data risks
- What you would explicitly not build in v1

#### Part 1 Deliverable:
2–4 pages of written explanation (bullets are fine). Diagrams optional.

#
## 🟧 PART 2 — TARGETED IMPLEMENTATION (Supporting Signal)

Choose one option:

#### Option A — Decision Engine Prototype
#### Build a small service that: Accepts free-text input + light context

Outputs:

- vertical

- recommended campaign

- confidence score

- reasoning

- next questions to ask

- Focus on structure and extensibility, not ML accuracy.

OR

#### Option B — Experimentation Framework Skeleton
#### Implement a minimal framework showing: 

- How results are logged

- How winning variants are selected

- Simulation or fake data is fine.

OR

#### Option C — Scoring / Ranking Slice
#### Build a simplified scoring model that:

- Outputs a score + explanation

- Takes synthetic interaction data

- Is explainable and evolvable

#### Part 2 Deliverable (applies to any of the chosen options above):
1. Code
2. Short README explaining what you built, why you chose it, and what comes next

