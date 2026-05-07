from fastapi import FastAPI

app = FastAPI(title="openfincal API")


@app.get("/")
def root():
    return {"service": "openfincal-api", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
