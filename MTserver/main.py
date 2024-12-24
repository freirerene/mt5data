from routers import orders, history, close
from utils.mtfunctions import get_ticks
from utils.credentials import MT_PATH, LOGIN, PASSWORD, SERVER

from fastapi import FastAPI, HTTPException
import MetaTrader5 as mt5

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    if not mt5.initialize(MT_PATH, login=LOGIN, password=PASSWORD, server=SERVER):
        raise HTTPException(status_code=500, detail="Falha ao iniciar MetaTrader5")


@app.on_event("shutdown")
async def shutdown_event():
    mt5.shutdown()


@app.get("/price/{symbol}")
async def get_price(symbol: str):
    tick_info = get_ticks(symbol)
    return tick_info


@app.post("/close-all")
async def close_all_positions():
    close_info = close()
    return close_info


app.include_router(orders.router)
app.include_router(history.router)
