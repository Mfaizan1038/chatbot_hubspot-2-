from fastapi import FastAPI
from database import Base, engine
from routes.chat import router as chat_router
from routes.filters import router as filter_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chatbot with Contracts & SQL Filters")

app.include_router(chat_router)
app.include_router(filter_router, prefix="/api")
