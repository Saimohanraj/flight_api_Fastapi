import requests
import json
import time
start_time = time.time()

url = "https://flight-api.lapisdata.net/api/v1/kayakmobile/"

payload = json.dumps({
    "currency": "AUD",
    "destination_iata_code": "TPE",
    "flight_selection": "Cheapest",
    "fn_destination_location_code": 695,
    "fn_origin_location_code": 261,
    "inbound_date": "2023-11-27",
    "is_one_way": True,
    "num_of_adults": 1,
    "number_of_stops": 0,
    "origin_iata_code": "SYD",
    "outbound_date": "2023-11-26",
    "pos": "AU",
    "scan_date": "2023-10-26"
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

response = requests.post(url, headers=headers, data=payload)

print(response.text)
end_time = time.time()
execution_time = start_time - end_time
print("Execution time:",execution_time)
breakpoint()