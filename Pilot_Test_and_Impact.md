# Pilot Test Report & Impact Projection

## 1. Pilot Test Outline

**Objective:** To validate the low-bandwidth, multilingual conversational assistant in a real-world setting with 10–15 rural users.

**Target Demographics (Personas):**
1. Farmers (seeking agricultural or PM-KISAN benefits)
2. Gig Workers / Daily Wage Laborers (seeking MGNREGA or PM SVANidhi benefits)
3. Women Head-of-Households (seeking PMUY or SSY benefits)

**Methodology:**
1. **Onboarding:** Briefly introduce the WhatsApp bot to the user and explain its purpose (e.g., "Send 'Hi' to this number to find out what government schemes you can apply for").
2. **Interaction:** Allow users to interact naturally using text or voice notes. Do not guide them heavily unless they are completely stuck.
3. **Observation:** Note the time taken per response (aiming for < 3 seconds on a simulated 2G/3G network) and the number of questions the bot asks to determine eligibility.
4. **Post-Chat Quiz:** Ask the user 3 simple questions about the schemes recommended to them and the documents required.

**Success Metrics to Measure:**
- **Completion Rate:** Percentage of users who complete the eligibility flow and receive a scheme recommendation + document checklist without dropping off (Target: ≥ 80%).
- **Comprehension Score:** Percentage of correct answers on the post-chat quiz regarding scheme details (Target: ≥ 70%).
- **Latency:** Median response time for the chatbot to reply over a 2G/3G connection (Target: < 3 seconds).
- **Code-Mixing Accuracy:** How effectively the bot understood queries that mixed Hindi and English (or used regional dialects).

---

## 2. Impact Projection (2-Page Summary)

### The Problem
Information asymmetry is a critical bottleneck in last-mile welfare delivery in India. Out of 950+ welfare schemes, fewer than 40% of eligible rural beneficiaries are aware of their entitlements. English/Hindi-only portals, smartphone dependency, and low literacy further exacerbate this issue.

### The Solution
By providing a low-bandwidth, multilingual conversational assistant on a familiar platform like WhatsApp, we drastically lower the barrier to discovery. A user simply sends a voice note in their native tongue to learn exactly what they are eligible for and what documents they need to prepare.

### Projected Impact Scenario (District-Level Adoption)
**Assumptions:**
- Target Population: 10,000 eligible beneficiaries in a single district or NGO network.
- Current Awareness/Uptake Rate: 35%.
- Projected Uplift: 20% increase in successful scheme discovery and application initiation due to the chatbot.

**Financial Impact Example (PM-KISAN & Ayushman Bharat):**
1. **PM-KISAN (Income Support):**
   - 20% of 10,000 = 2,000 new successful applications.
   - Entitlement: ₹6,000/year per household.
   - **Economic Impact:** ₹1.2 Crores per year injected directly into rural farming households.

2. **Ayushman Bharat (Health Cover):**
   - 2,000 new successful enrollments.
   - Entitlement: Health cover of ₹5 Lakhs per family.
   - **Economic Impact:** While the immediate cash injection isn't direct, the prevention of medical-debt spirals is immeasurable. Assuming 5% of these households require hospitalization averaging ₹50,000, the scheme saves the community ₹50 Lakhs annually in out-of-pocket medical expenses.

### Scalability and Cost
Deploying this solution scales linearly with API costs. Using the Gemini API and a Twilio Sandbox, the cost per conversation is fractions of a rupee. The ROI on this digital public infrastructure layer is immense, potentially unlocking hundreds of crores in welfare distribution across states with minimal overhead.
