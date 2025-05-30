#!/usr/bin/env python3

# run.py

from src.main import parse_args, configure_logging, main
import sys

if __name__ == "__main__":
    args = parse_args()
    configure_logging(args.verbose)
    sys.exit(main(verbosity=args.verbose, force=args.force, csv_file=args.tickers))

