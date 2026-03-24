import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
import json

MODEL_ID   = "./qwen3b-base"
OUTPUT_DIR = "./qwen3b-akilli-ayna"
DATA_PATH  = "./dataset.json"

print("=" * 60)
print("  Akıllı Ayna - QLoRA Fine-Tuning (Qwen2.5-3B)")
print(f"  GPU: {torch.cuda.get_device_name(0)}")
print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
print("=" * 60)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

print("\n[1/5] Model yükleniyor...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, quantization_config=bnb_config, device_map="auto", trust_remote_code=True,
)
model.config.use_cache = False
model.enable_input_require_grads()

print("[2/5] Tokenizer yükleniyor...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

print("[3/5] LoRA hazırlanıyor...")
model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
lora_config = LoraConfig(
    r=8, lora_alpha=16,
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
    lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("[4/5] Dataset yükleniyor...")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

def format_sample(example):
    instruction = example.get("instruction", "")
    context     = example.get("input", "")
    output      = example.get("output", "")
    user_msg    = f"{instruction}\n\nBağlam: {context}" if context and context != "{}" else instruction
    return {"text": (
        "<|im_start|>system\nSen Türkçe konuşan, kişiselleştirilmiş bir akıllı ayna asistanısın. "
        "Kullanıcının günlük planlarına, görevlerine ve hatırlatmalarına yardımcı olursun. "
        "SADECE verilen bağlamdaki bilgileri kullan, asla hayal etme!<|im_end|>\n"
        f"<|im_start|>user\n{user_msg}<|im_end|>\n"
        f"<|im_start|>assistant\n{output}<|im_end|>"
    )}

dataset = Dataset.from_list([format_sample(d) for d in raw_data])
print(f"   Toplam örnek: {len(dataset)}")

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    fp16=True,
    gradient_checkpointing=True,
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
    warmup_steps=10,
    lr_scheduler_type="cosine",
    optim="paged_adamw_8bit",
    report_to="none",
)

print("[5/5] Eğitim başlıyor...\n")
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args,
    max_seq_length=512,
    dataset_text_field="text",
)
trainer.train()

print("\nEğitim tamamlandı!")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Model kaydedildi: {OUTPUT_DIR}")
