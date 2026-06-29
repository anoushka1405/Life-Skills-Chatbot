from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from session_manager import get_engine, clear_session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartRequest(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/")
def home():
    return {"status": "Buddy running 🚀"}


@app.post("/start")
def start(req: StartRequest):

    engine = get_engine(req.session_id)

    return {
        "reply": engine.start()
    }


@app.post("/chat")
def chat(req: ChatRequest):

    engine = get_engine(req.session_id)

    response = engine.respond(req.message)

    finished = engine.session_finished()

    result = {
        "reply": response,
        "stage": engine.stage,
        "warmth": engine.personality["warmth"],
        "finished": finished
    }

    # attach summary if lesson finished
    if finished:
        result["summary"] = engine.end_session()
        clear_session(req.session_id)

    return result