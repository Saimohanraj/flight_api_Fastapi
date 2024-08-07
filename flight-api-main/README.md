# flight-api

## Installation

```shell
cd aircraft/
source ~/flight_api_env/bin/activate

```
## Running
Run without docker
```console
$ uvicorn main:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

To build docker 
```shell
docker compose build
```

Run with docker
```shell
docker compose up -d
```

To restart docker
```shell
docker compose restart
```

### Interactive API docs

Now go to <a href="http://127.0.0.1:8000/docs" class="external-link" target="_blank">http://127.0.0.1:8000/docs</a>.

You will see the automatic interactive API documentation (provided by <a href="https://github.com/swagger-api/swagger-ui" class="external-link" target="_blank">Swagger UI</a>):

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-01-swagger-ui-simple.png)

## Python Example 
```Python hl_lines="4  9-12  25-27"
import requests
import json

url = "https://flight-api.lapisdata.net/api/v1/kayakmobile/"

payload = json.dumps({
  "domain": "kayak.com",
  "device": "mobile",
  "snapshot_required": True,
  "destination_iata_code": "TPE",
  "inbound_date": "2023-11-24",
  "flight_selection": "Cheapest",
  "is_one_way": True,
  "num_of_adults": 1,
  "origin_iata_code": "SYD",
  "outbound_date": "2023-11-26",
  "pos": "AU",
  "cabin_class": "economy",
  "arc": "",
  "myid": "123456789",
  "currency": "AUD"
})
headers = {
  'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'Connection': 'keep-alive',
  'Content-Type': 'application/json',
  'Origin': 'https://flight-api.lapisdata.net',
  'Referer': 'https://flight-api.lapisdata.net/api/v1/docs',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
  'accept': 'application/json',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'x-api-key': '9d207bf0-10f5-4d8f-a479-22ff5aeff8d1'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```
