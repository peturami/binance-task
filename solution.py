from lib.binance import get_highest_vol, get_order_books_all, get_max_trades, get_spreads_all, run_stream
from lib.utils import init_config
from lib.server import start_server

# Read configuration file
cfg = init_config("conf.yml")

q1 = get_highest_vol(**cfg["q1"])
print(q1)

q3 = get_order_books_all(**cfg["q3"], symbols_2_fetch=q1)
print(q3)

q2 = get_max_trades(**cfg["q2"])
print(q2)

q4 = get_spreads_all(**cfg["q4"], symbols_lst=q2)
print(q4)

# q5
#run_stream(q2, cfg["q4"])

# q6
#start_server()
