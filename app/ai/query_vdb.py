from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

# quant_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_use_double_quant=True,
#     bnb_4bit_quant_type="nf4",           # nf4 is usually best for LLMs
#     bnb_4bit_compute_dtype=torch.float16 # keep compute in fp16
#     )
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/phi-1_5",
    dtype=torch.float16,
    # quantization_config=quant_config,
    device_map="auto",
    low_cpu_mem_usage=True
    )
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")


prompt = """
Query: "@GrexAI what is the synonym of good"
"""

inputs = tokenizer(prompt, return_tensors="pt")
output = model.generate(
    **inputs,
    max_new_tokens=30,
    do_sample=False,     # deterministic output
)

print(tokenizer.decode(output[0], skip_special_tokens=True))