## Docs:

### Google Gemini

You can use Google’s Gemini models for both LLM and embeddings. Set the following environment variables in your .env file:

For LLM:

LLM_PROVIDER="gemini"
LLM_API_KEY="your_api_key"
LLM_MODEL="gemini/gemini-2.5-flash-lite-preview-06-17"

For embeddings:

EMBEDDING_PROVIDER="gemini"
EMBEDDING_API_KEY="your_api_key"
EMBEDDING_MODEL="gemini/text-embedding-004"
EMBEDDING_DIMENSIONS=768
EMBEDDING_MAX_TOKENS=8076