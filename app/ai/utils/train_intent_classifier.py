from datasets import load_dataset
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
import torch

model_name = "distilbert-base-uncased"

model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=4)

dataset = load_dataset("json", data_files="app/ai/datasets/fine_tuning_datasets.json")
dataset = dataset["train"].train_test_split(test_size = 0.2, seed=42)
tokenizer = DistilBertTokenizerFast.from_pretrained(model_name)

def preprocess_data(data):
    return tokenizer(data["text"], padding="max_length", truncation=True, max_length=64)

encoded_token = dataset.map(preprocess_data, batched=True)

training_args = TrainingArguments(
    output_dir="./model/results",
    # evaluation_strategy="epoch",
    save_strategy="no",
    learning_rate=5e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=4,
    weight_decay=0.01,
    logging_dir="./model/logs",
    logging_steps=10
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_token['train'],
    eval_dataset=encoded_token['test']
)

trainer.train()

model.save_pretrained("./model/grex-distilbert")
tokenizer.save_pretrained("./model/grex-distilbert")