from fastapi import FastAPI

app = FastAPI(title="Blue-Green Demo App")

VERSION = "1.0.0"
COLOR = "blue"


@app.get("/")
def root():
    return {"message": "Hello from Blue-Green deployment", "version": VERSION, "color": COLOR}


@app.get("/health")
def health():
    return {"status": "healthy", "version": VERSION, "color": COLOR}
