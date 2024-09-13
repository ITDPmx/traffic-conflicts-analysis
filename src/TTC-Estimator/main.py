import sys

#Importing path to generic classes
sys.path.append( '../' )

#Actual director class
from System.Director.ProjectDirector import ProjectDirector

#Fast API
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# API 
app = FastAPI()

# Base
class FileRequest(BaseModel):
    bucket: str
    path: str

@app.get("/process_video")
def process_video(request: FileRequest):
    bucket = request.bucket
    path = request.path
    ProjectDirector.go( sys.argv, bucket, path )

@app.get("/")
def read_root():
    return {"Message": "TCC-API"}

# Entry point to run the server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
