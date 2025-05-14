from src import *
from fastapi import APIRouter
router = APIRouter()
router.include_router(account_router)
