In this project, you are going to make a chatbot to scrape LLM Inference Serving websites to research costs of serving various LLMs. You will do this by writing an MCP Server that hooks up to Firecrawl's API and saving the data in a SQLite Database. You should use the following websites to scrape:

- "cloudrift": "https://www.cloudrift.ai/inference"
- "deepinfra": "https://deepinfra.com/pricing"
- "fireworks": "https://fireworks.ai/pricing#serverless-pricing"
- "groq": "https://groq.com/pricing"

1. Make a venv with uv
2. Sync venv with pyproject.toml (`uv sync`)
3. Make an API Key on Anthropic and Firecrawl
4. Complete the 2 tool calls in `starter_server.py`
5. Change the `server_config.json` to point to your server file
6. Complete any section in `starter_client.py` that has "#complete".
7. Test using any methods taught in the course
8. Use the following prompts in your chatbot but play around with all the LLM providers in the list above: 
    - "How much does cloudrift ai (https://www.cloudrift.ai/inference) charge for deepseek v3?"
    - "How much does deepinfra (https://deepinfra.com/pricing) charge for deepseek v3"
    - "Compare cloudrift ai and deepinfra's costs for deepseek v3"
