from google import genai
from app.config.settings import settings as st
from google.genai import types


def gemini_setup(prompt: str, query: str):
    client = genai.Client(api_key=st.GEMINI_API_KEY)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=prompt),
        contents=query
    )

    return response.text

