# Stock

This is a python script to track and analyze stock data

## Features

- Pulls stock information from sec.gov/edgars
- command-line interface (CLI)

## Setup
1. Clone the repo:
```bash
git clone git@github.com:poshaw/stock.git
cd stock
```
2. Create the virtual environment
```
python -m venv .venv
source .venv/Scripts/activate
```
3. Install dependencies
```
python -m pip install --upgrade pip requests
```


4. Run tests
```
python -m unittest discover -s test
```