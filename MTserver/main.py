from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import MetaTrader5 as mt5

app = FastAPI()


class TradeRequest(BaseModel):
    symbol: str
    volume: float


@app.on_event("startup")
async def startup_event():
    path = "Z:\\home\\user\\.mt5\\drive_c\\Program Files\\MetaTrader 5\\terminal64.exe"
    if not mt5.initialize(
        path, login="YOURLOGIN", password="YOURPASSWORD", server="YOURSERVER"
    ):
        raise HTTPException(status_code=500, detail="Falha ao iniciar MetaTrader5")


@app.on_event("shutdown")
async def shutdown_event():
    mt5.shutdown()


@app.get("/price/{symbol}")
async def get_price(symbol: str):
    tick_info = mt5.symbol_info_tick(symbol)
    if not tick_info:
        raise HTTPException(
            status_code=404, detail=f"Símbolo '{symbol}' não encontrado."
        )

    return {
        "symbol": symbol,
        "bid": tick_info.bid,
        "ask": tick_info.ask,
        "last": tick_info.last,
    }


@app.post("/buy")
async def buy_order(trade: TradeRequest):
    """
    Envia uma ordem de COMPRA (BUY) do símbolo e volume informados.
    Exemplo de corpo (JSON):
    {
      "symbol": "EURUSD",
      "volume": 0.01
    }
    """
    symbol_info = mt5.symbol_info(trade.symbol)
    if symbol_info is None:
        raise HTTPException(
            status_code=404, detail=f"Símbolo '{trade.symbol}' não encontrado."
        )

    # Se o símbolo não está visível no Market Watch, tentar exibir
    if not symbol_info.visible:
        if not mt5.symbol_select(trade.symbol, True):
            raise HTTPException(
                status_code=400, detail=f"Falha ao selecionar símbolo '{trade.symbol}'."
            )

    # Monta a requisição de compra
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": trade.symbol,
        "volume": trade.volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": symbol_info.ask,  # preço de compra
        "deviation": 10,  # tolerância de variação de preço
        "magic": 234000,  # ID arbitrário para identificar a estratégia
        "comment": "Buy order from FastAPI",
        "type_time": mt5.ORDER_TIME_GTC,  # good-till-cancelled
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # Envia a ordem
    result = mt5.order_send(order_request)

    # Verifica resultado
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise HTTPException(
            status_code=400,
            detail=f"Falha ao enviar ordem de BUY. Retcode={result.retcode}, {result.comment}",
        )

    return {
        "message": "Ordem de BUY enviada com sucesso!",
        "symbol": trade.symbol,
        "volume": trade.volume,
        "order_result": {
            "retcode": result.retcode,
            "comment": result.comment,
            "order": result.order,
        },
    }


@app.post("/sell")
async def sell_order(trade: TradeRequest):
    """
    Envia uma ordem de VENDA (SELL) do símbolo e volume informados.
    Exemplo de corpo (JSON):
    {
      "symbol": "EURUSD",
      "volume": 0.01
    }
    """
    symbol_info = mt5.symbol_info(trade.symbol)
    if symbol_info is None:
        raise HTTPException(
            status_code=404, detail=f"Símbolo '{trade.symbol}' não encontrado."
        )

    # Se o símbolo não está visível no Market Watch, tentar exibir
    if not symbol_info.visible:
        if not mt5.symbol_select(trade.symbol, True):
            raise HTTPException(
                status_code=400, detail=f"Falha ao selecionar símbolo '{trade.symbol}'."
            )

    # Monta a requisição de venda
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": trade.symbol,
        "volume": trade.volume,
        "type": mt5.ORDER_TYPE_SELL,
        "price": symbol_info.bid,  # preço de venda
        "deviation": 10,  # tolerância de variação de preço
        "magic": 234000,
        "comment": "Sell order from FastAPI",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # Envia a ordem
    result = mt5.order_send(order_request)

    # Verifica resultado
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise HTTPException(
            status_code=400,
            detail=f"Falha ao enviar ordem de SELL. Retcode={result.retcode}, {result.comment}",
        )

    return {
        "message": "Ordem de SELL enviada com sucesso!",
        "symbol": trade.symbol,
        "volume": trade.volume,
        "order_result": {
            "retcode": result.retcode,
            "comment": result.comment,
            "order": result.order,
        },
    }


@app.post("/close-all")
async def close_all_positions():
    """
    Fecha todas as posições abertas na conta.
    """
    positions = mt5.positions_get()
    if positions is None:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível obter as posições. Verifique a conexão/conta.",
        )
    if len(positions) == 0:
        return {"message": "Não há posições abertas para fechar."}

    closed_positions = []
    for pos in positions:
        # Se a posição for BUY (pos.type == 0), enviamos ordem SELL para fechar.
        # Se a posição for SELL (pos.type == 1), enviamos ordem BUY para fechar.
        order_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY

        symbol_info = mt5.symbol_info(pos.symbol)
        if not symbol_info:
            closed_positions.append(
                {"symbol": pos.symbol, "error": "Símbolo não encontrado."}
            )
            continue

        # Definimos o preço adequado para fechar a posição
        price = symbol_info.bid if pos.type == 0 else symbol_info.ask

        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,  # fechar todo o volume
            "type": order_type,
            "position": pos.ticket,  # ticket da posição aberta
            "price": price,
            "deviation": 10,
            "magic": 234000,
            "comment": "Close position from FastAPI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(close_request)

        # Armazena o resultado para cada posição
        closed_positions.append(
            {
                "symbol": pos.symbol,
                "ticket": pos.ticket,
                "volume": pos.volume,
                "close_result": {
                    "retcode": result.retcode,
                    "comment": result.comment,
                    "order": result.order,
                },
            }
        )

    return {
        "message": "Tentativa de fechar todas as posições.",
        "closed_positions": closed_positions,
    }
