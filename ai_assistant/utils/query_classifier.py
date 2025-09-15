from transformers import pipeline

model_name = "ai_assistant/model/grex-distilbert"
classifier = pipeline("text-classification", model=model_name, tokenizer=model_name)

def query_classifier(query):
    result = classifier(query)
    predicted_class = result[0]["label"]
    return int(predicted_class.split("_")[1])

query = "@GrexAI do you think this is the right solution for these tasks?"
print(f"Choice: {query_classifier(query)}")
