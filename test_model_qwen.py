import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
FINETUNED  = "./qwen-akilli-ayna"

print("Model yükleniyor...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)
model = PeftModel.from_pretrained(model, FINETUNED)
model.eval()
print("✅ Model hazır!\n")

def chat(instruction, context=""):
    user_msg = f"{instruction}\n\nBağlam: {context}" if context else instruction
    prompt = (
        "<|im_start|>system\n"
        "Sen Türkçe konuşan, kişiselleştirilmiş bir akıllı ayna asistanısın. "
        "Kullanıcının günlük planlarına, görevlerine ve hatırlatmalarına yardımcı olursun."
        "<|im_end|>\n"
        f"<|im_start|>user\n{user_msg}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return response.strip()

# Test soruları
tests = [
    ("Bugün ne yapmalıyım?", "Görevler: Saat 10'da toplantı, öğlen spor, akşam rapor teslimi"),
    ("Hatırlatıcılarım neler?", "Berkay: İlaç 09:00, market alışverişi 18:00"),
    ("Bana motive edici bir şey söyle", ""),
]

for instruction, context in tests:
    print(f"Soru : {instruction}")
    if context:
        print(f"Bağlam: {context}")
    print(f"Yanıt : {chat(instruction, context)}")
    print("-" * 50)
