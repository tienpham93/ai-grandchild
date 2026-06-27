import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# We initialize the google-genai Client.
# It automatically picks up GEMINI_API_KEY from the environment.
client = genai.Client()

# Centralized configuration
MODEL_NAME = "gemini-2.5-flash"
