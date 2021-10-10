from time import sleep
from typing import Dict, List, Union
from lib.utils import get_request, sort_by_col


####################################################################################################
# 1. Print the top 5 symbols with quote asset BTC 
# and the highest volume over the last 24 hours in descending order.
####################################################################################################

def get_highest_vol(url: str, quote_in: str, sort_col: str) -> List:
    """Returns top 5 symbols by volume in past 24h (only quoted in BTC).

    Args:
        url (str): endpoint
        quote_in (str): quoting currency
        sort_col (str): sorting column

    Returns:
        List: top 5 symbols by volume, ordered desc
    """
    
    r = get_request(url)
    sorted_result = sort_by_col(r, quote_in, sort_col)

    return [i.get("symbol") for i in sorted_result[:5]]


####################################################################################################
# 3. Using the symbols from Q1, what is the total notional value of the top 200 bids and asks 
# currently on each order book?
####################################################################################################

def get_sum(array: List[List]) -> int:
    """Get sum from nested lists.

    Args:
        array (List[List]): array

    Returns:
        int: sum of nested lists
    """

    ttl = 0
    for item in array:
        ttl += float(item[1])
    return ttl


def sum_order_book(url: str, symbol: str, limit: int) -> Dict[str, Union[str, int]]:
    """Returns sum of the top 200 bids/asks in the order book.

    Args:
        url (str): endpoint
        symbol (str): symbol
        limit (int): limit of orders in the order book

    Returns:
        Dict[str, Union[str, int]]: sum of bids/asks per symbol
    """

    params = {'symbol': symbol, 'limit': limit}

    order_book = get_request(url, params)

    return {"symbol": symbol,
            "bids_sum": get_sum(order_book['bids']),
            "asks_sum": get_sum(order_book['asks'])
            }

    
def get_order_books_all(url: str, limit: int, symbols_2_fetch: List) -> List[Dict]:
    """Returns list of summed order books for symbols from Q1.

    Args:
        url (str): endpoint
        limit (int): limit of orders in the order book
        symbols_2_fetch (List): list of symbols from Q1

    Returns:
        List[Dict]: list of all symbols and its bids/asks sum
    """

    order_book_all = []
    for symbol in symbols_2_fetch:
        order_book_all.append(sum_order_book(url, symbol, limit))

    return order_book_all


####################################################################################################
# 2. Print the top 5 symbols with quote asset USDT and the highest number of trades over 
# the last 24 hours in descending order.
####################################################################################################

def get_max_trades(url: str, quote_in: str, sort_col: str) -> List:
    """Returns top 5 symbols by number of trades in past 24h (only quoted in USDT).

    Args:
        url (str): endpoint
        quote_in (str): quoting currency
        sort_col (str): sorting column

    Returns:
        List: top 5 symbols by number of trades, ordered desc
    """

    r = get_request(url)
    
    sorted_res = sort_by_col(r, quote_in, sort_col)

    return [i.get("symbol") for i in sorted_res[:5]]


####################################################################################################
# 4. What is the price spread for each of the symbols from Q2?
####################################################################################################

def get_spread(url: str, symbol: str) -> float:
    """Returns spread per symbol.

    Args:
        url (str): endpoint
        symbol (str): symbol

    Returns:
        int: spread (ask-bid)
    """

    params = {'symbol': symbol}
    ticker_res = get_request(url, params)
    spread = float(ticker_res['askPrice']) - float(ticker_res['bidPrice'])
    return spread


def get_spreads_all(url: str, symbols_lst: List) -> Dict:
    """Returns spread for all symbols from Q2.

    Args:
        url (str): endpoint
        symbols_lst (List): list of symbols from Q2

    Returns:
        Dict: spread for all Q2 symbols
    """

    spreads_all = {}
    for s in symbols_lst:
        spreads_all[s] = get_spread(url, s)

    return spreads_all


####################################################################################################
# 5. Every 10 seconds print the result of Q4 and the absolute delta from the previous value for each symbol.
####################################################################################################

class Symbol:
    """Class for storing symbol data."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.current_spread = 0
        self.last_spread = 0
        self.delta = 0

    def update_delta(self, spread: float) -> None:
        """Updates delta (spread current - previous).

        Args:
            spread (float): spread
        """

        self.last_spread = spread if self.current_spread == 0 else self.current_spread
        self.current_spread = spread
        self.delta = abs(self.last_spread - self.current_spread)

    @staticmethod
    def symbol_refresh(objects: Dict, symbols_lst: List, conf: Dict) -> None:
        """Refresh spread for all symbols from Q2.

        Args:
            objects (Dict): objects
            symbols_lst (List): symbols from Q2
            conf (Dict): settings
        """

        spreads = get_spreads_all(**conf, symbols_lst=symbols_lst)
        for _, s in objects.items():
            s.update_delta(spreads[s.name])
            print(f"{s.name} delta: {s.delta:.10f} - current_spread: {s.current_spread:.10f} "
                  f"- last_spread: {s.last_spread:.10f}")


def run_stream(symbols_lst: List, conf: Dict):
    """Run 'streaming' - print spreads + delta every 10s.

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
