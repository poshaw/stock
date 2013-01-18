#! /usr/bin/python3
# -*- coding: utf-8 -*-

import argparse, signal, sys, time

__author__ = "Phil Shaw"
__version__ = 1.0
__copyright__ = "Copyright (c) 2012 Flogistix"

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
	while True:
		time.sleep(5)
		if opts.verbose:
			print("hi")

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
