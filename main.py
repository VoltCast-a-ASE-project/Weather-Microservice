from fastapi import FastAPI

app = FastAPI(title="Weather & Location Microservice")

@app.get("/")
async def root():
    return {"message": "Hello, Weather Microservice!"}
