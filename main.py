#!/usr/bin/env python3

import sys
from cik_lookup import get_cik

def load_tickers(filename="tickers.txt"):
    with open(filename, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

def main(argv):
    '''
    symbol = "MSFT"
    try:
        cik = get_cik_for_ticker(symbol)
        print(f"CIK for {symbol.upper()}: {cik}")
    except Exception as e:
        print(f"Error: {e}")
    '''
    ticker_cik_map = ticker_cik_map()
    
    print(tickers)
    
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))