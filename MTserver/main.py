from fastapi import FastAPI, HTTPException
import MetaTrader5 as mt5

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    path = "Z:\\home\\user\\.mt5\\drive_c\\Program Files\\MetaTrader 5\\terminal64.exe"
    if not mt5.initialize(path, login="YOURLOGIN", password="YOURPASSWORD", server="YOURSERVER"):
        raise HTTPException(status_code=500, detail="Falha ao iniciar MetaTrader5")

@app.on_event("shutdown")
async def shutdown_event():
    mt5.shutdown()

@app.get("/price/{symbol}")
async def get_price(symbol: str):
    tick_info = mt5.symbol_info_tick(symbol)
    if not tick_info:
        raise HTTPException(status_code=404, detail=f"Símbolo '{symbol}' não encontrado.")

    return {
        "symbol": symbol,
        "bid": tick_info.bid,
        "ask": tick_info.ask,
        "last": tick_info.last
    }
