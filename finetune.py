import json
import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# ─────────────────────────────────────────
# 1. AYARLAR
# ─────────────────────────────────────────
MODEL_ID   = "meta-llama/Llama-3.2-1B"
DATA_PATH  = "dataset.json"
OUTPUT_DIR = "./llama-akilli-ayna"
MAX_SEQ_LEN = 512

print("=" * 50)
print("🪞 Akıllı Ayna - LLaMA Fine-Tuning")
print("=" * 50)

# ─────────────────────────────────────────
# 2. GPU KONTROL
# ─────────────────────────────────────────
if not torch.cuda.is_available():
    raise RuntimeError("❌ CUDA bulunamadı! GPU bağlantısını kontrol et.")

print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
print(f"✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

# ─────────────────────────────────────────
# 3. DATASET YÜKLE
# ─────────────────────────────────────────
print("\n📂 Dataset yükleniyor...")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Alpaca formatını tek string'e çevir
def format_prompt(example):
    if example["input"]:
        text = (
            f"### Görev:\n{example['instruction']}\n\n"
            f"### Bağlam:\n{example['input']}\n\n"
            f"### Yanıt:\n{example['output']}"
        )
    else:
        text = (
            f"### Görev:\n{example['instruction']}\n\n"
            f"### Yanıt:\n{example['output']}"
        )
    return {"text": text}

dataset = Dataset.from_list(raw_data)
dataset = dataset.map(format_prompt)

# %90 train, %10 validation
split = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = split["train"]
eval_dataset  = split["test"]

print(f"✅ Eğitim örnekleri : {len(train_dataset)}")
print(f"✅ Doğrulama örnekleri: {len(eval_dataset)}")

# ─────────────────────────────────────────
# 4. QLoRA AYARLARI (8GB VRAM için)
# ─────────────────────────────────────────
print("\n⚙️  Model yükleniyor (4-bit QLoRA)...")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# ─────────────────────────────────────────
# 5. MODEL & TOKENIZER
# ─────────────────────────────────────────
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16,
)

model = prepare_model_for_kbit_training(model)

# ─────────────────────────────────────────
# 6. LoRA AYARLARI
# ─────────────────────────────────────────
lora_config = LoraConfig(
    r=16,                    # LoRA rank
    lora_alpha=32,           # Scaling
    target_modules=[         # Hangi katmanlar eğitilecek
        "q_proj",
        "v_proj",
        "k_proj",
        "o_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ─────────────────────────────────────────
# 7. EĞİTİM AYARLARI
# ─────────────────────────────────────────
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    report_to="none",
    optim="paged_adamw_8bit",
)

# ─────────────────────────────────────────
# 8. TRAINER
# ─────────────────────────────────────────
trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    dataset_text_field="text",
    tokenizer=tokenizer,
    args=training_args,
    max_seq_length=MAX_SEQ_LEN,
    packing=False,
)

# ─────────────────────────────────────────
# 9. EĞİTİMİ BAŞLAT
# ─────────────────────────────────────────
print("\n🚀 Eğitim başlıyor...")
print(f"   Epochs     : {training_args.num_train_epochs}")
print(f"   Batch size : {training_args.per_device_train_batch_size}")
print(f"   Learning rate: {training_args.learning_rate}")
print()

trainer.train()

# ─────────────────────────────────────────
# 10. MODELİ KAYDET
# ─────────────────────────────────────────
print("\n💾 Model kaydediliyor...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"✅ Model kaydedildi: {OUTPUT_DIR}")
print("\n🎉 Fine-tuning tamamlandı!")
