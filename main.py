#!/usr/bin/env python3

import sys
from cik_lookup import get_cik

def load_tickers(filename="tickers.txt"):
    with open(filename, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

def main(argv):
    ticker_cik_map = ticker_cik_map()
    print(tickers)
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
