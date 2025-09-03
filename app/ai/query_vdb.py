from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3-mini-4k-instruct")
tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-4k-instruct")

inputs = tokenizer("Hello you are an assistant.", return_tensors="pt")
output = model.generate(**inputs, max_new_tokens=200)

print(output.decode(outputs[0], skip_special_tokens=True))