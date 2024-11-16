from typing import List
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from lib import agent 
from pathlib import Path

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


class File(BaseModel):
    name: str
    link: str

class QueryResponse(BaseModel):
    content: str
    files: List[File]


sources = [
    File(name="sr_snapping_turtle_0809_e.pdf", link="sr_snapping_turtle_0809_e.pdf")
]

@app.post("/query_agent", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    query = agent.agent.query(request.query)
    return QueryResponse(content=query.response, files=sources)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = Path("../data/raw/enviro-ns") / filename
    if file_path.exists():
        return FileResponse(file_path, media_type='application/octet-stream', filename=filename)
    return {"error": "File not found"}

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         query = agent.enviro_agent.query(data)
#         await websocket.send_text(query.response)
