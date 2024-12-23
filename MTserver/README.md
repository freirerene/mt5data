# MTserver

simple server to streamline the proccess of getting current price.

Usage:

```
[wine] pip install fastapi uvicorn MetaTrader5
[wine] uvicorn main:app
```

And to get the price:

```
curl GET http://127.0.0.1:8000/price/EURUSD
```
