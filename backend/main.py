import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import List
import uvicorn

app = FastAPI(title="Akıllı Ayna AI Backend")

BASE_MODEL = "./qwen3b-base"
FINETUNED  = "./qwen3b-akilli-ayna"

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
    role: str
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


def has_no_tasks(context: str) -> bool:
    no_task_keywords = [
        "için görev yok",
        "görev yok",
        "plan yok",
        "etkinlik yok",
    ]
    return not context or any(k in context for k in no_task_keywords)


def generate(instruction: str, context: str = "", history: List[HistoryMessage] = []) -> str:
    if has_no_tasks(context):
        return "Belirtilen gün için herhangi bir planın bulunmuyor."

    system = (
        "Sen Türkçe konuşan akıllı ayna asistanısın. "
        "Aşağıdaki GÖREV LİSTESİNDE yazan bilgileri kullanarak cevap ver. "
        "Görev listesinde olmayan hiçbir şeyi söyleme, uydurma, tahmin etme. "
        "Sadece listede olanları söyle."
    )

    prompt = f"<|im_start|>system\n{system}<|im_end|>\n"

    for msg in history[-6:]:
        role = "user" if msg.role == "user" else "assistant"
        prompt += f"<|im_start|>{role}\n{msg.content}<|im_end|>\n"

    user_msg = f"{instruction}\n\nGÖREV LİSTESİ:\n{context}"
    prompt += f"<|im_start|>user\n{user_msg}<|im_end|>\n<|im_start|>assistant\n"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.2,
        )
    return tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    ).strip()


@app.get("/api/v1/ai/status")
def status():
    return {"status": "ok", "model": "Qwen2.5-3B-Instruct (fine-tuned)"}

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
