from utils.schemas import TradeRequest, GetHistory

import pandas as pd
from datetime import datetime
from fastapi import HTTPException

import MetaTrader5 as mt5


TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
    "W1": mt5.TIMEFRAME_W1,
    "MN1": mt5.TIMEFRAME_MN1,
}


def get_ticks(symbol):
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


def get_history(info_request: GetHistory):

    timeframe = info_request.timeframe
    symbol = info_request.symbol
    from_date = info_request.from_date
    ticks = info_request.ticks

    if timeframe not in TIMEFRAMES:
        raise HTTPException(
            status_code=400,
            detail=f"Timeframe inválido. Disponíveis: {list(TIMEFRAMES.keys())}",
        )

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise HTTPException(
            status_code=404, detail=f"Símbolo '{symbol}' não encontrado."
        )

    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
            raise HTTPException(
                status_code=400,
                detail=f"Falha ao selecionar símbolo '{symbol}' no Market Watch.",
            )

    mt5_timeframe = TIMEFRAMES[timeframe]

    if from_date:
        from_date = f"{from_date} 18:00:00"
        from_date = datetime.fromisoformat(from_date)
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, from_date, ticks)
    else:
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, ticks)

    if rates is None or len(rates) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Não foi possível obter dados de '{symbol}' no timeframe '{timeframe}'.",
        )

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")

    df.rename(columns={"time": "timestamp"}, inplace=True)
    df = df[["timestamp", "open", "low", "high", "close"]]

    return df


def buy(trade: TradeRequest):

    symbol_info = mt5.symbol_info(trade.symbol)
    if symbol_info is None:
        raise HTTPException(
            status_code=404, detail=f"Símbolo '{trade.symbol}' não encontrado."
        )

    if not symbol_info.visible:
        if not mt5.symbol_select(trade.symbol, True):
            raise HTTPException(
                status_code=400, detail=f"Falha ao selecionar símbolo '{trade.symbol}'."
            )

    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": trade.symbol,
        "volume": trade.volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": symbol_info.ask,
        "deviation": trade.deviation,
        "magic": trade.magic,
        "comment": trade.comment,
        "type_time": mt5.ORDER_TIME_GTC,  # good-till-cancelled
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(order_request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise HTTPException(
            status_code=400,
            detail=f"Falha ao enviar ordem de BUY. Retcode={result.retcode}, {result.comment}",
        )

    return {
        "message": "Ordem de BUY enviada com sucesso!",
        "symbol": trade.symbol,
        "volume": trade.volume,
        "magic": trade.magic,
        "comment": trade.comment,
        "order_result": {
            "retcode": result.retcode,
            "comment": result.comment,
            "order": result.order,
        },
    }


def sell(trade: TradeRequest):
    symbol_info = mt5.symbol_info(trade.symbol)
    if symbol_info is None:
        raise HTTPException(
            status_code=404, detail=f"Símbolo '{trade.symbol}' não encontrado."
        )
    if not symbol_info.visible:
        if not mt5.symbol_select(trade.symbol, True):
            raise HTTPException(
                status_code=400, detail=f"Falha ao selecionar símbolo '{trade.symbol}'."
            )

    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": trade.symbol,
        "volume": trade.volume,
        "type": mt5.ORDER_TYPE_SELL,
        "price": symbol_info.bid,
        "deviation": trade.deviation,
        "magic": trade.magic,
        "comment": trade.comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(order_request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise HTTPException(
            status_code=400,
            detail=f"Falha ao enviar ordem de SELL. Retcode={result.retcode}, {result.comment}",
        )

    return {
        "message": "Ordem de SELL enviada com sucesso!",
        "symbol": trade.symbol,
        "volume": trade.volume,
        "magic": trade.magic,
        "comment": trade.comment,
        "order_result": {
            "retcode": result.retcode,
            "comment": result.comment,
            "order": result.order,
        },
    }


def close():
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
