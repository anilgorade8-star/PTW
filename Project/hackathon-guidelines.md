# Hackathon Guidelines: What to Do and What Not to Do

## 1. Golden Rules

1. **Do not make assumptions.** If anything is unclear, ask the team, mentor, judge, or user before proceeding.
2. **Understand the problem first.** Do not start coding before understanding the problem statement and expected outcome.
3. **Build for the actual problem.** Do not add features just because they seem interesting.
4. **Verify before claiming.** Never claim a feature works unless it has been tested.
5. **Keep it simple.** A small, working solution is better than a large, broken solution.
6. **Communicate clearly.** Share decisions, blockers, and progress with your teammates.
7. **Follow the rules.** Respect the hackathon's rules, deadlines, and technology requirements.

---

## 2. What TO DO ✅

### A. Understand the Problem
- Read the complete problem statement carefully.
- Identify the target users and their actual needs.
- Identify the expected deliverables and judging criteria.
- List the known requirements and constraints.
- Ask questions whenever requirements are unclear.
- Define what success looks like before implementation.

### B. Avoid Assumptions
- Separate confirmed facts from assumptions.
- Ask for clarification instead of guessing.
- Validate requirements with reliable sources or stakeholders.
- If clarification is unavailable, document the uncertainty and make the smallest, safest, reversible decision.
- Clearly communicate any assumption that must be made.

### C. Plan Before Coding
- Define the minimum viable product (MVP).
- Break the work into small, manageable tasks.
- Assign clear responsibilities to teammates.
- Choose technologies the team can realistically use.
- Identify dependencies, risks, and time constraints.
- Keep time for testing, integration, and the final presentation.

### D. Develop the Solution
- Follow consistent coding and naming conventions.
- Use version control, such as Git.
- Make small, frequent commits.
- Build the core functionality first.
- Integrate team members' work early.
- Handle errors and unexpected inputs.
- Use environment variables for secrets and API keys.
- Keep the implementation understandable and maintainable.

### E. Test and Validate
- Test the main user journey from beginning to end.
- Test invalid, missing, and unexpected inputs.
- Check edge cases and error handling.
- Test API integrations and external dependencies.
- Verify that the application works in the demo environment.
- Test on the actual device or browser you plan to use.
- Maintain a backup demo plan.

### F. Prepare the Final Submission
- Ensure all required deliverables are included.
- Write a clear README with setup instructions.
- Explain the problem, solution, technology stack, and key features.
- Mention known limitations honestly.
- Prepare a short, working demonstration.
- Confirm submission format, deadline, and evaluation requirements.

---

## 3. What NOT TO DO ❌

### A. Do Not Make Unverified Assumptions
- Do not invent user requirements.
- Do not guess what judges expect.
- Do not assume an API, library, or service will work without checking.
- Do not assume sample data represents real-world data.
- Do not assume a feature is complete just because it works once.
- Do not treat an unconfirmed idea as an established fact.

### B. Do Not Waste Time
- Do not build unnecessary features before the MVP works.
- Do not spend most of the hackathon perfecting UI while core functionality is broken.
- Do not rewrite working code without a clear reason.
- Do not change the technology stack repeatedly.
- Do not leave integration and testing until the last minute.

### C. Do Not Compromise Security
- Do not commit API keys, passwords, access tokens, or private credentials.
- Do not expose sensitive user data.
- Do not use real personal data without appropriate authorization.
- Do not blindly trust user input or external API responses.
- Do not disable security checks just to make a demo work.

### D. Do Not Misrepresent Your Work
- Do not claim features that have not been implemented.
- Do not present mock data as live or verified data.
- Do not claim AI output is always correct.
- Do not copy code or assets without respecting licenses and attribution requirements.
- Do not hide important limitations from judges.
- Do not violate the hackathon's AI usage, collaboration, or submission policies.

### E. Do Not Damage Team Collaboration
- Do not make major decisions without informing affected teammates.
- Do not overwrite someone else's work without coordination.
- Do not ignore blockers or wait until the deadline to report them.
- Do not blame teammates; focus on solving the problem.
- Do not let unclear ownership create duplicate work.

---

## 4. The No-Assumptions Protocol

Whenever you encounter an unclear requirement, follow these steps:

1. **STOP:** Do not immediately implement your interpretation.
2. **IDENTIFY:** Write down exactly what is unclear.
3. **ASK:** Seek clarification from the relevant person or source.
4. **VERIFY:** Check the answer against the problem statement and available evidence.
5. **DOCUMENT:** Record the confirmed requirement and any remaining uncertainty.
6. **DECIDE:** If clarification is impossible, choose a minimal, low-risk, reversible approach and explicitly label it as an assumption.
7. **TEST:** Validate that the decision does not break the core requirements.

### Example

**Situation:** The problem statement says, "Build a secure login system."

**Do not assume:**
- Social login is required.
- Email verification is required.
- An administrator dashboard is required.
- A particular authentication provider must be used.

**Instead:**
- Check the stated requirements.
- Ask whether a particular authentication method is mandatory.
- Identify the minimum security requirements.
- Implement only the confirmed scope.
- Document any unresolved decisions.

**Important:** When you cannot confirm something, say "Unknown" or "Not yet verified" instead of presenting a guess as a fact.

---

## 5. Decision-Making Rules

Before implementing a feature or making a major decision, ask:

- [ ] Is this explicitly required?
- [ ] Is there evidence that users need it?
- [ ] Does it support the main problem?
- [ ] Can we complete and test it before the deadline?
- [ ] Does it introduce security, privacy, or reliability risks?
- [ ] Have the relevant teammates agreed?
- [ ] Is the decision reversible if we learn something new?

If a feature is not required, not validated, and not essential to the MVP, postpone it.

---

## 6. Handling AI Tools and External Resources

- Use AI tools to accelerate development, not to replace verification.
- Review generated code before integrating it.
- Test generated code with realistic and edge-case inputs.
- Verify factual claims, calculations, dependencies, and API documentation.
- Never paste confidential credentials or sensitive data into tools without authorization.
- Check licensing and attribution requirements for external code and assets.
- Follow the event's specific AI usage policies.
- Disclose AI assistance if required by the organizers.

---

## 7. Recommended Hackathon Workflow

1. **Understand:** Read and clarify the problem statement.
2. **Define:** Identify users, requirements, constraints, and success criteria.
3. **Prioritize:** Select the smallest useful MVP.
4. **Design:** Plan the architecture and primary user flow.
5. **Build:** Implement the core features.
6. **Integrate:** Connect components and external services early.
7. **Test:** Verify functionality, edge cases, and security.
8. **Polish:** Improve usability and fix critical issues.
9. **Document:** Prepare setup instructions and known limitations.
10. **Present:** Demonstrate the working solution and explain its impact honestly.

---

## 8. Final Checklist Before Submission

- [ ] We understand the actual problem.
- [ ] Requirements are confirmed or explicitly marked as uncertain.
- [ ] We have not presented assumptions as facts.
- [ ] The MVP works end to end.
- [ ] Core features have been tested.
- [ ] API keys and secrets are protected.
- [ ] Setup instructions are complete.
- [ ] Known limitations are documented.
- [ ] The demo has been rehearsed.
- [ ] All required files and links are ready.
- [ ] We comply with the hackathon rules.
- [ ] The submission is ready before the deadline.

---

## Final Principle

**Understand before building. Ask before assuming. Verify before trusting. Test before presenting. Be honest about what works and what does not.**

The goal is not to build the most features. The goal is to solve the right problem with a reliable, understandable, and demonstrable solution.
