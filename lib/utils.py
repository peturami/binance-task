from typing import Dict, List, Any, Union
import yaml
import requests


def get_request(url: str, params: Dict = None) -> Union[List, Dict]:
    try:
        r = requests.get(url, params)
        return r.json()
    except Exception as ex:
        print(ex)


def init_config(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding='utf8') as yml_file:
        cfg = yaml.safe_load(yml_file)
    return cfg


def sort_by_col(array: List, quote_currency: str, order_col: str) -> List:
    """Implementation of quick sort"""
    
    if len(array) < 2:
        return array

    low, same, high = [], [], []
    pivot_val = array[int(len(array)/2)] 

    for item in array:

        if item.get('symbol')[-len(quote_currency):].lower() != quote_currency:
            continue
            
        if float(item.get(order_col)) < float(pivot_val.get(order_col)):
            low.append(item)
        elif float(item.get(order_col)) == float(pivot_val.get(order_col)):
            same.append(item)
        elif float(item.get(order_col)) > float(pivot_val.get(order_col)):
            high.append(item)

    return sort_by_col(high, quote_currency, order_col) + same + sort_by_col(low, quote_currency, order_col)
