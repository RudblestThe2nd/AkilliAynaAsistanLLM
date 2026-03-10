import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Akıllı Ayna AI Backend")

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
print("✅ Model hazır!")


class HistoryMessage(BaseModel):
    role: str   # "user" veya "assistant"
    content: str


class InferRequest(BaseModel):
    prompt: str
    context: str = ""
    history: List[HistoryMessage] = []


class VoiceRequest(BaseModel):
    transcript: str
    user_id: str = "default"
    context: str = ""
    history: List[HistoryMessage] = []


def generate(instruction: str, context: str = "", history: List[HistoryMessage] = []) -> str:
    system = (
        "Sen Türkçe konuşan, kişiselleştirilmiş bir akıllı ayna asistanısın. "
        "Kullanıcının günlük planlarına, görevlerine ve hatırlatmalarına yardımcı olursun. "
        "SADECE verilen bağlamdaki bilgileri kullan, asla hayal etme veya uydurma! "
        "Eğer bağlamda bilgi yoksa 'Bu konuda bilgim yok' de."
    )

    prompt = f"<|im_start|>system\n{system}<|im_end|>\n"

    # Konuşma geçmişini ekle (en fazla son 5 tur)
    for msg in history[-10:]:  # 5 tur = 10 mesaj
        role = "user" if msg.role == "user" else "assistant"
        prompt += f"<|im_start|>{role}\n{msg.content}<|im_end|>\n"

    # Mevcut kullanıcı mesajı
    if context:
        user_msg = f"{instruction}\n\n[Kullanıcının Gerçek Verileri]\n{context}"
    else:
        user_msg = instruction

    prompt += f"<|im_start|>user\n{user_msg}<|im_end|>\n<|im_start|>assistant\n"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.3,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1,
        )
    return tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    ).strip()


@app.get("/api/v1/ai/status")
def status():
    return {"status": "ok", "model": "Qwen2.5-1.5B-Instruct (fine-tuned)"}


@app.post("/api/v1/ai/infer")
def infer(req: InferRequest):
    response = generate(req.prompt, req.context, req.history)
    return {"response": response}


@app.post("/api/v1/voice/process")
def voice_process(req: VoiceRequest):
    response = generate(req.transcript, req.context, req.history)
    return {"response": response, "user_id": req.user_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
