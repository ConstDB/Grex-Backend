from transformers import pipeline

model_name = "app/ai_assistant/model/grex-distilbert"
classifier = pipeline("text-classification", model=model_name, tokenizer=model_name)

def query_classifier(query: str):
    result = classifier(query)
    predicted_class = result[0]["label"]
    return int(predicted_class.split("_")[1])

# query = "@GrexAI "
# print(f"Choice: {query_classifier(query)}")

