# Mt5Data

A simple -- and not optimized -- way of getting financial data **for free (!)** using MetaTrader5 **on linux (!).**

This script is especially useful in the Brazilian market -- or, really, any other market that is somewhat difficult to get access to data. One just signs up in a broker that offers MT5 and one`s golden!

One should be able to easily adapt it to run on windows -- just put the `WINDOWS/windowsSTOCKS.py` inside your `get_stocks_history` (from `GETDATA.py`). No need to use `subprocess`.

As a bonus I also wrote a little function to get the mini-futures codes