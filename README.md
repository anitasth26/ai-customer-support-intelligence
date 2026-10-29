# AI Customer Support Intelligence

**Bilingual English–German support-ticket classification and triage powered by Google Gemini.**

[Try the live demo](https://ai-customer-support-intelligence-2ust48ggmsgawaerqbgyhp.streamlit.app/)

## Overview

This application analyzes IT support tickets in English and German, recommends a priority, and explains whether human intervention is needed.

It combines structured AI classification with independent data-loss checks, response validation, and safe fallback handling.

## Features

- **Bilingual input:** Analyze English and German tickets, with explanations in English.
- **Five priority levels:** Critical, high, medium, low, and very low.
- **Clear explanations:** Understand the reasoning behind each classification.
- **Independent safety checks:** Detect possible data loss using English and German keyword rules.
- **Critical escalation:** Critical incidents always require immediate human intervention.
- **Visible review triggers:** See why a ticket needs human review.
- **Safe fallbacks:** Invalid responses and service failures require manual review without assigning an unreliable priority.
- **Usage safeguards:** Input limits, request cooldowns, and session and shared request limits.

## Try the demo

1. Open the [live application](https://ai-customer-support-intelligence-2ust48ggmsgawaerqbgyhp.streamlit.app/).
2. Choose a fictional sample or enter an anonymized support ticket.
3. Confirm the privacy notice and click **Analyze ticket**.
4. Review the priority, explanation, routing recommendation, and review triggers.

**Use fictional or anonymized information only.** Submitted tickets are sent to Google Gemini. Do not enter passwords, personal information, or confidential customer data.

## How it works

1. Validate the ticket input.
2. Check independently for possible data loss.
3. Request a structured JSON classification from Gemini.
4. Validate the AI response.
5. Apply escalation and human-review rules.
6. Display the recommendation and its explanation.

| Condition | Recommended action |
| --- | --- |
| Critical incident | Escalate immediately; human intervention required |
| AI review flag or independent data-loss match | Send for human review |
| Valid classification without review triggers | Standard support queue |
| Invalid response or processing failure | Human review; no assigned priority |

Routing is advisory. The demo does not create incidents or notify a support team.

## Technology

Python · Streamlit · Google Gemini API · Google Gen AI SDK · JSON Schema · unittest

API credentials are configured privately on the server. The model is configurable by the application owner.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Application interface, AI integration, validation, safety rules, and routing |
| `requirements.txt` | Application dependencies |
| `test_app.py` | Offline safety, routing, usage-limit, and interface tests |
| `.gitignore` | Excludes local secrets and development files |

## Validation

The deployment package passed Python syntax checks and **13 offline tests**, including critical escalation, bilingual data-loss checks, combined review triggers, invalid responses, service failures, privacy consent, and usage limits.

The tests used simulated model responses. They do not establish real-world classification accuracy.

## Limitations

This is a portfolio demonstration. AI can misclassify tickets, and keyword checks can miss paraphrases or flag negated statements. Human verification is necessary for consequential decisions.

Usage safeguards reduce API consumption but do not guarantee a spending cap.
