from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.dialogue_engine import DialogueEngine
from modules.empathy_module import EMPATHY_MODULE

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = DialogueEngine(EMPATHY_MODULE)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"status": "Buddy running 🚀"}


@app.get("/start")
def start():
    return {"reply": engine.start()}


@app.post("/chat")
def chat(req: ChatRequest):

    user_text = req.message
    response = engine.respond(user_text)

    return {
        "reply": response,
        "stage": engine.stage,
        "warmth": engine.personality["warmth"]
    }