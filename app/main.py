from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/ping")
def get_current_time():
    current_time = datetime.now().isoformat()
    return { "time": current_time } 


