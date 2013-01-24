#! /usr/bin/python3
# -*- coding: utf-8 -*-

import argparse, signal, sys, time, urllib.request

__author__ = "Phil Shaw"
__version__ = 1.0
__copyright__ = "Copyright (c) 2012"

def signal_handler(signum, frame):
	"""
Handle print_exit via signals
"""
	print("\n(Terminated with signal %d)\n" % (signum))
	# Do exit stuff here
	sys.exit(0)

def setup_signal_handler():
	signal.signal(signal.SIGINT, signal_handler) # Handle Ctrl-C
	if hasattr(signal, "SIGBREAK"):
		# Handle Ctrl-Break e.g. under Windows
		signal.signal(signal.SIGBREAK, signal_handler)

def main(args):
	setup_signal_handler() # handle Ctrl-C

	parser = argparse.ArgumentParser(description='{}'.format(__doc__))
	parser.add_argument('-v', '--verbose', action='count', help='provides more output durring execution. -vv will display even more...')
	parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
	opts = parser.parse_args()

	# start of program
	with urllib.request.urlopen('http://www.google.com/finance?q=NASDAQ:NYMT') as f:
		content = f.read().decode('utf-8')
	markerClassPrice = """<span class="pr">"""
	mindex = content.find(markerClassPrice)
	price = content[mindex+len(markerClassPrice):mindex+100]
	price = price[price.find('>')+1:price.find("</span>")]
	print(price)


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
