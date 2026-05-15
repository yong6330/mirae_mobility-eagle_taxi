from fastapi import FastAPI

app = FastAPI(title="Eagle Taxi API", version="0.1.0-alpha")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "eagle-taxi"}
