from transformers import pipeline
from pathlib import Path

# model_name = "app/ai_assistant/model/grex-distilbert"
model_path = Path(__file__).parent / "model/grex-distilbert"
classifier = pipeline("text-classification", model_path, tokenizer=model_path)

def query_classifier(query: str):
    result = classifier(query)
    predicted_class = result[0]["label"]
    return int(predicted_class.split("_")[1])

# query = "@GrexAI "
# print(f"Choice: {query_classifier(query)}")

