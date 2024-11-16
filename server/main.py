from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from lib import agent 

# Initialize FastAPI app
app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all HTTP headers
)


# Define request model
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    output: str

@app.post("/query_location", response_model=QueryResponse)
async def query_location(request: QueryRequest):
    return QueryResponse(output=request.query)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        async for text in agent.enviro_agent.query(data):
            await websocket.send_text(text)
        await websocket.send_text("[END]")
