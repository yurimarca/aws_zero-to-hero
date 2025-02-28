from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on AWS Lambda with Docker!"}

@app.post("/predict")
def predict(data: dict):
    return {"prediction": "some result"}

# AWS Lambda handler
handler = Mangum(app)
