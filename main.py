# This file is the backend of our web app, built with FastAPI.
# The backend is the "server" side — it receives requests from
# the browser, talks to the AI, and sends responses back.
#
# In the original notebook, all the logic ran in a terminal loop.
# Here, we replace that loop with HTTP routes (called "endpoints")
# that the browser can call over the internet.
# ============================================================
from dotenv import load_dotenv  # load_dotenv reads the .env file and makes its values available via os.getenv().
import os                       # for reading .env variables (like our API key)
from fastapi import FastAPI     # the web framework that handles incoming HTTP requests.
from pydantic import BaseModel  # BaseModel from Pydantic lets us define the expected shape of incoming request data. FastAPI uses it to validate automatically.
from openai import OpenAI
from fastapi.staticfiles import StaticFiles  # lets FastAPI serve static files from a folder.
from fastapi.responses import FileResponse  # lets us return a specific file as a response.


# --- Setup ---------------------------------------------------
load_dotenv() # Load env variables from .env file, must run before os.getenv() below. 

# Create the FastAPI app. 
app = FastAPI() # This is the core object that registers all our routes and handles incoming HTTP requests.

# Mount the frontend folder so FastAPI serves its files.
# Any file inside frontend/ is accessible at /frontend/filename 
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Create the AI client. 
client = OpenAI(
    api_key=os.getenv("AI_API_KEY"), # api_key is read from .env file.
    base_url="https://openrouter.ai/api/v1", # Instead of connecting to OpenAI directly, point it at OpenRouter 
)


# --- Routes --------------------------------------------------
# A "route" maps a URL path + HTTP method to a Python function.
# When a request comes in, FastAPI calls the matching function
# and returns whatever it returns as a JSON response.

# Root route — serves the HTML page when you visit http://localhost:8000
@app.get("/")
def root():
    return FileResponse("frontend/index.html")


# Health route — used by deployment platforms like Render to check if the server is alive. 
# Returns a simple status message.
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Request Model -------------------------------------------
# This defines the shape of the JSON body we expect when the
# browser calls POST /chat. Pydantic will reject the request
# automatically if "message" is missing or not a string.
class ChatRequest(BaseModel):
    message: str


# Chat route — the main endpoint. 
# This replaces the while loop you'd normally have with a local program.
# Instead of input(), the browser sends a POST request with a JSON body like: {"message": "why is grass green?"}
@app.post("/chat")
def chat(request: ChatRequest):
    # Send the user's message to the AI model.
    response = client.chat.completions.create(
        model="google/gemma-4-31b-it:free",
        messages=[
            {"role": "system", "content": "You are an assistant that gives silly answers."}, # "system" message sets the AI's behavior.
            {"role": "user", "content": request.message}, # "user" message is what the user typed.
        ],
    )

    # Extract the AI's reply from the response and send it back to the browser as JSON: {"reply": "..."}
    return {"reply": response.choices[0].message.content}
