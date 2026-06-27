# AI Grandchild

A Kaggle Capstone Project (Concierge Track) designed to protect Vietnamese seniors from high-pressure vacation contract and timeshare scams.

## Architecture

This project simulates a webhook receiver for Zalo messages, processing them through a multi-agent system powered by Google Gemini:

1.  **Anonymizer Skill:** Scrubs PII (phone numbers, ID cards, bank accounts) before it hits the LLM.
2.  **Companion Agent:** Acts as an empathetic digital grandchild, interacting warmly with the senior.
3.  **Investigator Agent:** Analyzes the context for known scam patterns (e.g., the 2.7T VND timeshare ring).
4.  **Bridge Agent:** Formats and escalates alerts to family members if a scam is suspected.

## Setup

1. Ensure you have Python 3.11+ and `uv` installed.
2. Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`.
3. Run `make init` to install dependencies.
4. Run `make run` to execute the mock pipeline.
