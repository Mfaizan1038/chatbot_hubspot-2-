from fastapi import FastAPI
from database import Base, engine
from routes.chat import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chatbot with Tools")

app.include_router(chat_router)
