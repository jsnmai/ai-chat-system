# This file is the backend of our web app, built with FastAPI.
# The backend is the "server" side — it receives requests from
# the browser, talks to the AI, and sends responses back.
# ============================================================
from dotenv import load_dotenv  # reads .env and makes its values available via os.getenv()
import os                       # used to read environment variables like the API key
from fastapi import FastAPI, HTTPException  # HTTPException lets us return error responses with a status code
from pydantic import BaseModel             # validates the shape of incoming request data automatically
from openai import OpenAI, RateLimitError  # RateLimitError is raised when the API is temporarily rate-limited
from fastapi.staticfiles import StaticFiles  # serves files from a folder (HTML, CSS, JS)
from fastapi.responses import FileResponse   # returns a specific file as an HTTP response


# --- Setup ---------------------------------------------------
load_dotenv()  # must run before os.getenv() so the .env values are loaded first

app = FastAPI() # Create the FastAPI app. This is the core object that registers all our routes and handles incoming HTTP requests.

# Mount the frontend folder so FastAPI serves its files.
# Serve everything inside frontend/ at the /frontend URL path.
# Any file inside frontend/ is accessible at /frontend/filename ie frontend/style.css is accessible at /frontend/style.css
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

client = OpenAI( # Create the AI client. 
    api_key=os.getenv("AI_API_KEY"), # api_key is read from .env file.
    base_url="https://openrouter.ai/api/v1", # Instead of connecting to OpenAI directly, point it at OpenRouter 
)


# --- Routes --------------------------------------------------
# A "route" maps a URL path + HTTP method to a Python function.
# When a request comes in, FastAPI calls the matching function and returns its result as a JSON response.

# Root route — serves the HTML page when you visit the root URL.
@app.get("/")
def root():
    return FileResponse("frontend/index.html")


# Health route — used by deployment platforms like Render to check if the server is alive. 
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Request model -------------------------------------------
# This defines the expected shape of the JSON body when the browser calls POST /chat. 
# Pydantic rejects request automatically if "message" is missing or not a string.
class ChatRequest(BaseModel):
    message: str
    role: str = "answers questions"  # default if the frontend sends nothing


# Models to try in order — if one is rate-limited, the next is used as a fallback.
MODELS = [
    "google/gemma-4-31b-it:free",
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "google/gemma-3-27b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "google/gemma-3-12b-it:free",
    "openai/gpt-oss-20b:free",
    "qwen/qwen3-coder:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-3-4b-it:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
]


# --- Chat endpoint -------------------------------------------
# Receives the user's message and role, sends them to the AI, returns the reply.
@app.post("/chat")
def chat(request: ChatRequest):
    system_prompt = f"You are an assistant that {request.role}."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.message},
    ]

    # Try each model in order, falling back to the next if rate-limited.
    for model in MODELS:
        try:
            response = client.chat.completions.create(model=model, messages=messages)
            return {"reply": response.choices[0].message.content}
        except RateLimitError:
            continue

    # All models are rate-limited — let the frontend know.
    raise HTTPException(status_code=429, detail="All models are currently rate-limited. Please try again in a moment.")
