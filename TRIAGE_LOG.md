
## Fill in `TRIAGE_LOG.md`

```markdown
# Triage Log

This log documents problems encountered while building AI Data Assistant and how they were resolved. It's kept up to date as new issues come up during development.

| # | Problem | Impact | Resolution | Status |
|---|---------|--------|------------|--------|

| 1 | Initial LLM integration used the Google Generative AI SDK directly, then briefly moved to OpenRouter for multi-model flexibility. | Coupling to a single provider/SDK made switching models harder each time. | Settled on Google's OpenAI-compatible endpoint (`generativelanguage.googleapis.com`) via the `openai` client — keeps the flexible client interface while using Google's models directly. | Resolved. |

| 2 | `pydantic` version resolved differently by pip for FastAPI vs. Streamlit when installed in the same environment. | Could resolve to an incompatible version depending on install order. | Pinned `pydantic>=2.0.0` in `frontend/requirements.txt`; backend and frontend use separate virtual environments. | Resolved. |

| 3 | Frontend hardcoded `http://127.0.0.1:8000`, which broke once deployed. | Worked locally, failed against any deployed backend. | Backend URL now read from a `BACKEND_URL` env var. | Resolved. |

| 4 | CORS was configured with `allow_origins=["*"]`. | Any website could call `/analyze` once the API was public. | Origins now read from an `ALLOWED_ORIGINS` env var. | Resolved. |

| 7 | An OpenRouter API key was accidentally committed in a stray text file, caught by GitHub's push protection before it reached the remote. | Push was blocked; key had to be treated as compromised. | Rotated the key, squashed the offending commit out of local history with `git reset --soft`, recommitted clean. | Resolved. |


