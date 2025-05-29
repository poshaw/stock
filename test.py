import requests

CIK = "0001046179"
url = f"https://data.sec.gov/submissions/CIK{CIK}.json"

headers = {
    "User-Agent": "Phil Shaw (posop@hotmail.com)",
    "Accept": "application/json"
}

resp = requests.get(url, headers=headers)
print("Status:", resp.status_code)

if resp.ok:
    data = resp.json()
    for filing in data.get("filings", {}).get("recent", {}).get("form", []):
        print(filing)

