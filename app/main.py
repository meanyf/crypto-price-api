# main.py
from app.factory import create_app
from app.api.v1.api import api_router
from app.api.v1.errors import register_exception_handlers

app = create_app()

register_exception_handlers(app)
app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "ok"}
