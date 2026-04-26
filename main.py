# This file is the backend of our web app, built with FastAPI.
# The backend is the "server" side — it receives requests from
# the browser, talks to the AI, and sends responses back.
# ============================================================
from dotenv import load_dotenv  # reads .env and makes its values available via os.getenv()
import os                       # used to read environment variables like the API key
from fastapi import FastAPI     # the web framework that handles incoming HTTP requests
from pydantic import BaseModel  # validates the shape of incoming request data automatically
from openai import OpenAI
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


# --- Chat endpoint -------------------------------------------
# Receives the user's message, sends it to the AI, returns the reply.
@app.post("/chat")
def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model="google/gemma-4-31b-it:free",
        messages=[
            {"role": "system", "content": "You are an assistant that gives silly answers."}, # "system" message sets the AI's behavior.
            {"role": "user", "content": request.message}, # "user" message is what the user typed.
        ],
    )
    # Extract the AI's reply from the response and send it back to the browser as JSON: {"reply": "..."}
    return {"reply": response.choices[0].message.content} 
