from fastapi import FastAPI, Request, HTTPException, status, Security
from webscraper.kayak_api_scraper import KayakMobileScraper
from api_analytics.fastapi import Analytics
from fastapi.staticfiles import StaticFiles
from slowapi.util import get_remote_address
from fastapi.security import APIKeyHeader
from pydantic import BaseModel,Field
from typing import Optional,Literal
from dotenv import load_dotenv
from datetime import date
from slowapi import Limiter
from pathlib import Path
import slack_notifications as slack
import configparser
import uvicorn
import logging
import json
import os


try:
    load_dotenv()
except:
    env_path = Path(".env")
    load_dotenv(dotenv_path=env_path)

if not os.path.exists('html_files'):
    os.makedirs('html_files')
if not os.path.exists('cookie'):
    os.makedirs('cookie')

config = configparser.RawConfigParser()
config.read("aircraft.ini")

API_KEYS = (os.getenv("api_keys")).split(",")
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

slack.ACCESS_TOKEN =  os.getenv("slack_token")

app = FastAPI(openapi_url="/docs/openapi.json",redoc_url=None,swagger_ui_parameters={"syntaxHighlight": False})
app.add_middleware(Analytics, api_key=os.getenv("fastapi_analytics"))
app.mount("/static", StaticFiles(directory="html_files"), name="static")
limiter = Limiter(key_func=get_remote_address)


app.error_count=0
app.maintainence=False


logging.basicConfig(filename='logs/api_log.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    level=logging.INFO)
api_logger = logging.getLogger('logs/api_log.log')


async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """get_api_key is implemented for security purpose.It will check the api key is valid or not."""
    if api_key_header in API_KEYS:
        return api_key_header
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or missing API Key")

def notification(status):
    '''notification function will trigger slack notification if api request fails continuously 30 times and reset to 0 for all success response'''
    if "fail"==status:
        app.error_count+=1
        if app.error_count%30==0:
            slack.send_notify('#api_alerts', username='api_alerts', text=f'{app.error_count} request has Failed')
            # app.maintainence=True
    else:
        app.error_count=0
    


class Item(BaseModel):
    '''Class Item validates all input and set defaut value for necessary fields'''
    outbound_date: date = Field(detail="Departure date")
    inbound_date: Optional[date] = Field(default=None,detail="Return date")
    is_one_way: Optional[bool] = Field(default="false")
    pos: Literal[tuple((config.get("pos","pos")).split(","))] = Field(detail="Point of sell")
    origin_iata_code: str = Field(detail="IATA code of the origin airport",min_length=3,max_length=3)
    destination_iata_code: str = Field(detail="IATA code of the destination airport",min_length=3,max_length=3)
    cabin_class: Optional[str] = Field(default="economy",detail= "Economy, Premium Economy, Business class, First class")
    flight_selection: str = Field(default="Cheapest",detail="Defines the rate(s) to collect")
    num_of_adults: int = Field(detail="Defines no of adults")
    children_ages: Optional[list] = Field(default=[],detail="Defines number of children")
    currency: Optional[Literal[tuple((config.get("currency","currency")).split(","))]] = Field(default=None,detail="Currency")
    myid : Optional[str]= Field(default=None)
    domain:Optional[str]= Field(default=None)
    device:Optional[str]= Field(default=None)
    snapshot_required :Optional[bool]= Field(default=True)
    node_ips :Optional[list]= Field(default=[])
    server_ips:Optional[list]= Field(default=[])
    hotel_id:Optional[str]= Field(default=None)
    arc:Optional[str]= Field(default=None)
    number_of_stops: Optional[Literal[0,1,2]] = Field(default=2,detail= "nonstop=>0,one stop or nonstop=>1,2=>any number of stop ,default value =>2")


    

@app.post("/api/v1/kayakmobile/")
@limiter.limit("20/minute")
async def post_airlines_scraper(request: Request,item:Item,api_key: str = Security(get_api_key)):
    # if app.maintainence:
    #     raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail={'status':False,'message':'Server Under Maintainance.Try Again Later.'})
    # else:
    scraper=KayakMobileScraper()
    api_logger.info(f"request_url_received--------->{item}")
    results=scraper.kayakmobile(item)
    if results is not None and "errors" not in results and 'error' not in results:
        notification("success")
        if results.get("result",{}).get("snapshot_url",''):
            results['result']["snapshot_url"]=request.url_for('static', path=results.get("result",{}).get("snapshot_url",''))._url
        api_logger.info(f"status 200 OK ------------> success {item.myid}")
        return results
    elif results is not None and  "errors" in results:
        message=json.loads(results).get("message",None)
        if message is None:
            message=json.loads(results).get("errors",'')
        if "proxy" in message :
            api_logger.info(f"status failed 305--------->{item.myid}")
            notification("fail")
            raise HTTPException(status_code=status.HTTP_305_USE_PROXY, detail={'status':False,'message':message})
        elif "Too many" in message: # too many request
            notification("fail")
            api_logger.info(f"status failed 429--------->{item.myid}")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail={'status':False,'message':message})
        elif "one way is false" in message or 'Inbound date' in message or "cabin class" in message or 'start search' in message or 'destination' in message or 'Invalid date' in message:
            api_logger.info(f"status failed 400--------->{item.myid}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'status':False,'message':message})
        elif "Captcha Required".lower() in message.lower():
            api_logger.info(f"status failed 403--------->{item.myid}")
            notification("fail")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={'status':False,'message':message})
        else:
            notification("fail")
            api_logger.info(f"status failed 400--------->{item.myid}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'status':False,'message':message}) 

    else:
        api_logger.info(f" status failed 404 request failed--------->{item.myid}")
        notification("fail")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'status':False,'message':'no results found'})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,log_config="aircraft.ini")
