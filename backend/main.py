from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from routers import router
from config import settings

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    filename='py_log.log',
    filemode='w',
    format="%(asctime)s %(levelname)s %(message)s"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)