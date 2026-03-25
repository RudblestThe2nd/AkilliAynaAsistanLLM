import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import List
import uvicorn
import time

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge

app = FastAPI(title="Akilli Ayna AI Backend")

# Prometheus metrikleri
voice_requests_total = Counter(
    "voice_requests_total",
    "Toplam sesli komut istegi sayisi",
    ["status"]
)
ai_response_time = Histogram(
    "ai_response_seconds",
    "AI yanit suresi (saniye)",
    buckets=[0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]
)
hallucination_blocked = Counter(
    "hallucination_blocked_total",
    "Hallusinasyon engellenen istek sayisi"
)
model_ready = Gauge("model_ready", "Model hazir durumu")
voice_task_added = Counter("voice_task_added_total", "Sesle eklenen gorev sayisi")

# Model
BASE_MODEL = "./qwen3b-base"
FINETUNED  = "./qwen3b-akilli-ayna"

model_ready.set(0)
print("Model yukleniyor...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True,
)
model = PeftModel.from_pretrained(model, FINETUNED)
model.eval()
model_ready.set(1)
print("Model hazir!")

# Prometheus endpoint: /metrics
Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
).instrument(app).expose(app)

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
    return not context or any(k in context for k in [
        "icin gorev yok", "gorev yok", "plan yok", "etkinlik yok"
    ])

def generate(instruction: str, context: str = "", history: List[HistoryMessage] = []):
    start = time.time()
    if has_no_tasks(context):
        hallucination_blocked.inc()
        return "Belirtilen gun icin herhangi bir planin bulunmuyor.", time.time() - start

    system = (
        "Sen Turkce konusan akilli ayna asistanisin. "
        "Asagidaki GOREV LISTESINDE yazan bilgileri kullanarak cevap ver. "
        "Gorev listesinde olmayan hicbir seyi soyleme, uydurma, tahmin etme."
    )
    prompt = f"<|im_start|>system\n{system}<|im_end|>\n"
    for msg in history[-6:]:
        role = "user" if msg.role == "user" else "assistant"
        prompt += f"<|im_start|>{role}\n{msg.content}<|im_end|>\n"
    user_msg = f"{instruction}\n\nGOREV LISTESI:\n{context}"
    prompt += f"<|im_start|>user\n{user_msg}<|im_end|>\n<|im_start|>assistant\n"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=150, temperature=0.1, do_sample=True,
            pad_token_id=tokenizer.eos_token_id, repetition_penalty=1.2,
        )
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
    return response, time.time() - start

@app.get("/api/v1/ai/status")
def status():
    return {"status": "ok", "model": "Qwen2.5-3B-Instruct (fine-tuned)", "model_ready": True}

@app.post("/api/v1/ai/infer")
def infer(req: InferRequest):
    response, elapsed = generate(req.prompt, req.context, req.history)
    ai_response_time.observe(elapsed)
    return {"response": response, "response_time_ms": round(elapsed * 1000)}

@app.post("/api/v1/voice/process")
def voice_process(req: VoiceRequest):
    try:
        response, elapsed = generate(req.transcript, req.context, req.history)
        ai_response_time.observe(elapsed)
        status = "no_task" if "planin bulunmuyor" in response else "success"
        voice_requests_total.labels(status=status).inc()
        return {"response": response, "user_id": req.user_id, "response_time_ms": round(elapsed * 1000)}
    except Exception as e:
        voice_requests_total.labels(status="error").inc()
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
