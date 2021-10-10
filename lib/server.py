from typing import Dict, List
from time import sleep
import threading
from flask import Flask
from prometheus_client import make_wsgi_app, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from lib.binance import Symbol, get_spreads_all, get_max_trades
from lib.utils import init_config


app = Flask(__name__)

# Add prometheus wsgi middleware to route '/metrics' requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

g_spread = Gauge('Spread', 'Shows current spread of the symbol', ['symbol'])
g_delta = Gauge('Delta', 'Shows spread-delta of the symbol', ['symbol'])


def exporter(symbols: Dict) -> None:
    """Send metrics.

    Args:
        symbols (Dict): symbols from Q2
    """

    for _, s in symbols.items():
        g_spread.labels(s.name).set(s.current_spread)
        g_delta.labels(s.name).set(s.delta)


def stream_n_export(symbols_lst: List, conf: Dict) -> None:
    """Run 'streaming' and prometheus export. Send metrics every 10s.

    Args:
        symbols_lst (List): symbols from Q2
        conf (Dict): settings
    """

    symbols = {}
    spread_top_5 = get_spreads_all(**conf, symbols_lst=symbols_lst)
    
    for sym in spread_top_5:
        symbols[sym] = Symbol(sym)

    while True:
        print("Sleeping ... (10s)")
        sleep(10)
        Symbol.symbol_refresh(symbols, symbols_lst, conf)
        exporter(symbols)


def start_server():
    cfg = init_config("conf.yml")
    q2 = get_max_trades(**cfg["q2"])

    t = threading.Thread(target=stream_n_export, args=(q2, cfg["q4"],))
    t.daemon = True
    t.start()
    app.run(port=8080)
