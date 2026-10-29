# AI Customer Support Intelligence

A live Streamlit portfolio demo for structured English/German IT support triage using Google Gemini. Adapted from `AI_Customer_Support_Intelligence_Final.ipynb`; no Colab, Gradio, dataset download, or notebook runtime is required.

## What it does

Enter a fictional ticket or select an English/German example. Explicitly confirm the privacy notice, then click **Analyze ticket**. Examples use the same live API workflow as typed tickets; selecting one alone makes no API call.

The app returns a five-level priority, English explanation, suggested routing, and every applicable review trigger. It does not actually send notifications or contact a support team.

| Condition | Outcome |
| --- | --- |
| Critical priority | Escalate immediately **and require human intervention**, even if Gemini returns `human_review: false` |
| Gemini requests review | Human review, with AI assessment listed as a trigger |
| Independent bilingual data-loss keyword match | Human review, even if Gemini says no review |
| Multiple conditions | All applicable triggers are shown |
| Invalid/blocked/missing JSON or service error | No invented priority; human-review fallback |
| No review trigger | Standard queue; not a guarantee of safety |

The original five priorities and all original data-loss phrases are preserved, with several additional phrases. Critical intervention is enforced after validation rather than relying on the prompt. Independent data-loss checks run before the API and remain visible in failure fallbacks. The original AI flag is preserved separately from the final review decision.

## Files

- `app.py`: complete UI, schema, local validation, independent checks, routing, failure handling, usage limits.
- `requirements.txt`: fixed direct dependency versions for reproducible setup.
- `.gitignore`: excludes secrets and local environment files.
- `test_app.py`: offline regression and UI tests; makes no live API calls.
- `README.md`: this guide.

## Upload to GitHub

1. Download and extract the ZIP on your computer.
2. Open your `ai-customer-support-intelligence` repository on GitHub.
3. Choose **Add file → Upload files**. Upload the extracted files to the repository's top level, so `app.py` and `requirements.txt` are directly visible. Upload files, not the ZIP or its enclosing folder.
4. Replace an existing README if needed. Ensure `.gitignore` is included; some file browsers hide names beginning with a dot. You can instead use **Add file → Create new file**, name it `.gitignore`, and paste its contents.
5. Commit the files. Never upload an API key, `.env`, or `.streamlit/secrets.toml`. Ignoring a file does not remove secrets already committed; revoke any exposed key.

## Deploy on Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub and authorize the repository.
2. Choose **Create app**, select the existing repository, branch (usually `main`), and entrypoint **`app.py`**.
3. In **Advanced settings**, choose **Python 3.12** and paste the following TOML into **Secrets**, replacing the placeholder privately:

```toml
GEMINI_API_KEY = "PASTE_YOUR_PRIVATE_KEY_HERE"
GEMINI_MODEL = "gemini-3.5-flash-lite"
ENABLE_LIVE_DEMO = "true"
```

4. Save the settings and click **Deploy**. Once configured, try a fictional example and confirm the results before sharing your app's URL.
5. To pause API usage, set `ENABLE_LIVE_DEMO = "false"` in the app's Secrets settings. Never paste the secrets block with a real key into GitHub.

The model defaults to the notebook's `gemini-3.5-flash-lite`, which is configurable by the owner through Secrets or an environment variable. Choose a text model supporting structured JSON output and available to your API project. Model access, quotas, availability, and pricing may change. An unavailable model fails safely to human review; the app does not automatically try another model or spend on retries.

See the official [deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [secrets guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management), [Gemini models](https://ai.google.dev/gemini-api/docs/models), and [structured output documentation](https://ai.google.dev/gemini-api/docs/structured-output).

## Privacy and costs

Use **only fictional or anonymized data**. The subject and message are sent to Google's Gemini API after explicit submission and consent. Do not submit passwords, personal information, confidential customer information, or production records. Review the applicable [Gemini API terms and data handling](https://ai.google.dev/gemini-api/terms) before deployment; handling varies with service and plan. The UI warns users before submission. This is not a production privacy or compliance solution.

The app does not intentionally persist ticket history, log tickets, cache responses globally, or display raw service exceptions. The form and latest result live in the current Streamlit session; **Clear ticket and result** removes them from app session state. Provider/platform processing and retention still apply. Clearing data does not reset the session attempt count.

Default safeguards:

- Subject up to 160 characters; message up to 4,000 characters.
- One API call per explicit submission; 1,024 output-token budget and 30-second SDK request timeout.
- SDK retry attempts set to one; failed attempts consume usage allowance.
- 15-second cooldown and 10 attempts per browser session.
- Thread-safe shared limits of 6 attempts/minute and 100 attempts/rolling 24 hours per running process; stored data consists only of timestamps.
- No automatic API call on page load, sample selection, or unrelated rerun; no tools or batch execution.
- Owner-controlled live-demo switch; visitors cannot select a more expensive model.

**These are best-effort controls, not a hard spending cap.** Sessions can be recreated, and process limits reset on restart and are not shared across multiple processes/replicas. Use a dedicated API project, restrict the key to the intended API, and configure available provider-side quotas and monitoring. Billing alerts alone do not stop spending. A public demo may be abused; stronger production protection requires authentication and a persistent shared rate limiter. Hosting and Gemini usage are separate services; verify current pricing and quotas before enabling calls.

## Local run (optional)

Python 3.12 is recommended:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate with `.venv\Scripts\activate`. For local secrets, create `.streamlit/secrets.toml` privately with the TOML above; it is ignored by Git. Environment variables `GEMINI_API_KEY`, `GEMINI_MODEL`, and `ENABLE_LIVE_DEMO` also work. Streamlit Secrets take precedence over environment values. The app starts without a key, but analysis stays disabled.

## Offline verification

```sh
python -m py_compile app.py test_app.py
python -m unittest -v test_app.py
```

Preparation verification: Python syntax checks and all 13 offline tests passed using Python 3.11 with the pinned direct dependencies. Python 3.12 is the recommended cloud runtime; a live cloud deployment was not tested.

Tests inject fake model responses and exercise real Streamlit UI sessions; they never instantiate the Gemini client or make live requests. Coverage includes critical review enforcement, both languages, combined triggers, invalid JSON/schema, empty/oversized input, service failures, limits, secrets precedence, and UI submission/clear behavior. Syntax and offline checks do not establish model accuracy or verify your credentials, model access, billing, or cloud deployment.

## Limitations

This is advisory triage, not autonomous incident response. Schema validation ensures structure, not factual correctness. Keyword checks intentionally err on the side of review: negated phrases can trigger false positives and paraphrases can be missed. Prompt instructions reduce, but do not eliminate, prompt-injection risk. Human review is necessary for consequential decisions. High priority alone retains the notebook's standard-queue behavior unless another review trigger is present.

The notebook's small evaluation is not a production benchmark and is not presented as accuracy for this deployed app. No live API evaluation or publication was performed while preparing these deployment files.
