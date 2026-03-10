import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# ─────────────────────────────────────────
# AYARLAR
# ─────────────────────────────────────────
BASE_MODEL  = "meta-llama/Llama-3.2-1B"
FINE_TUNED  = "./llama-akilli-ayna"

print("🪞 Akıllı Ayna - Model Test")
print("=" * 40)

# ─────────────────────────────────────────
# MODEL YÜKLE
# ─────────────────────────────────────────
tokenizer = AutoTokenizer.from_pretrained(FINE_TUNED)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
)
model = PeftModel.from_pretrained(model, FINE_TUNED)
model.eval()

print("✅ Model yüklendi!\n")

# ─────────────────────────────────────────
# SORU SOR
# ─────────────────────────────────────────
def sor(instruction, context=""):
    if context:
        prompt = f"### Görev:\n{instruction}\n\n### Bağlam:\n{context}\n\n### Yanıt:\n"
    else:
        prompt = f"### Görev:\n{instruction}\n\n### Yanıt:\n"

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Sadece yanıt kısmını al
    response = response.split("### Yanıt:\n")[-1].strip()
    return response

# ─────────────────────────────────────────
# TEST SORULARI
# ─────────────────────────────────────────
testler = [
    {
        "instruction": "Bugün programımda ne var?",
        "context": "Kullanıcı: Berkay. Plan: 10:00 ekip toplantısı, 14:00 spor, 19:00 arkadaş buluşması."
    },
    {
        "instruction": "Toplantımdan önce bana hatırlatma yap.",
        "context": "Toplantı: 15:00 müşteri toplantısı."
    },
    {
        "instruction": "Bugün en önemli görevim ne?",
        "context": "Todo: proje teslimi, e-posta gönder."
    },
    {
        "instruction": "Akşam spor yapmayı unutursam hatırlat.",
        "context": "Plan: 19:30 fitness."
    },
]

for i, test in enumerate(testler, 1):
    print(f"[Test {i}]")
    print(f"  Soru   : {test['instruction']}")
    print(f"  Bağlam : {test['context']}")
    yanit = sor(test["instruction"], test["context"])
    print(f"  Yanıt  : {yanit}")
    print()

# ─────────────────────────────────────────
# İNTERAKTİF MOD
# ─────────────────────────────────────────
print("=" * 40)
print("💬 İnteraktif mod (çıkmak için 'quit')")
print("=" * 40)

while True:
    soru = input("\nSoru: ").strip()
    if soru.lower() in ["quit", "exit", "q"]:
        break
    baglam = input("Bağlam (boş bırakabilirsin): ").strip()
    yanit = sor(soru, baglam)
    print(f"Yanıt: {yanit}")
