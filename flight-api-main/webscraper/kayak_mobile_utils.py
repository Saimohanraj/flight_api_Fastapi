import requests
import json
import os
import re
from dotenv import load_dotenv
from pathlib import Path
import json
import random
import ast
import time


try:
    load_dotenv()
except:
    env_path = Path(".env")
    load_dotenv(dotenv_path=env_path)

headers = {
  'User-Agent': 'kayakandroidphone/170.3 Android 9 API 28 (Phone; Custom; Genymotion)',
  'Accept-Language': 'en-US',
  'Accept-Encoding': 'gzip, deflate'}

data={}
proxy_ip=ast.literal_eval(os.getenv("proxy_ip"))
datacenter_port=json.loads(os.getenv("datacenter_port"))
residential_port= json.loads(os.getenv("residential_port"))


def request_fuction(url,payload,pos,logger,input,currency):
    retry=0
    p1_med_token=[{'id':'1','token':'0DZiq9yTD_PK1l22nHCjoL'},
                  {'id':'2','token':'Ms3ImggRbg9Q1pltXf0gQN'},
                  {'id':'3','token':'s$wpk4HQauLyM$0l2ABdXp'},
                  {'id':'4','token':'6eZDRu1rPTSU$lwADcf$hI'},
                  {'id':'5','token':'yPIdLiMnZ0xcZjP4XVBV1w'},
                  {'id':'6','token':'ywrt0$_Tume9Zl5082RmHt'}]
    while retry<5:
        currency_status=False
        token=random.choice(p1_med_token)
        cookie_id=token.get("id")
        token_value=token.get("value")
        if not os.path.exists(f"kayak_mobile_cookie_{cookie_id}.json"):
            create_cookie(pos,logger,cookie_id,token_value)
        if not os.path.exists(f"kayak_mobile_cookie_{cookie_id}.json"):
            create_cookie(pos,logger)
        with open(f'kayak_mobile_cookie_{cookie_id}.json') as f:
            cookie = json.load(f)
        try:
            if not currency_status:
                currency_status=set_currency(pos,logger,cookie,currency,token_value)
            headers = {
            'User-Agent': 'kayakandroidphone/183.1 Android 7.1.2 API 25 (SM-G965N; samsung; samsung)',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json; charset=UTF-8',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Cookie': f'p1.med.token={token_value}; mst_ADIrlA={cookie["mst_ADIrlA"]}; p1.med.sid={cookie["p1_med_sid"]}; {cookie["mst_key"]}={cookie["mst_value"]}; Apache={cookie["apache"]}; kayak.mc={cookie["kayak_mc"]}; kayak={cookie["kayak"]};; kmkid=A-LdUFdHq_RPCiagP70cF7M; cluster={cookie["cluster"]}; Apache={cookie["apache"]}; cluster={cookie["apache"]}; kayak={cookie["kayak"]};; kayak.mc={cookie["kayak_mc"]}; mst_ADIrlA={cookie["mst_ADIrlA"]}'
            }
            proxy_count=random.randint(0, len(proxy_ip) - 1)
            proxies = {"http":f'{proxy_ip[proxy_count]}:{residential_port.get(pos)}'}
            response = requests.request("POST", url, headers=headers, data=payload,proxies=proxies)
        except Exception as e:
           retry=retry+1
           logger.info(f"request error---> retry {retry} times  error:{e}")
           if retry==5 and  'Connection reset by peer' in str(e):
                return '{"status":true,"errors":"proxy error"}'
           continue
        # breakpoint()
        if response.status_code==401:
            create_cookie(pos,logger,cookie_id,token_value)
        
        elif response.status_code==200:
            if json.loads(response.text).get("status")=='complete':
                logger.info(f"request success-->{input}")
                return response.text
            elif (json.loads(response.text).get("status")=='complete' or  json.loads(response.text).get("status")=='first-phase') and len(json.loads(response.text).get("results"))!=0:
                if retry==2:
                    logger.info(f"request success-->{input}")
                    return response.text
            time.sleep(8)
        elif  response.status_code==400:
            return response.text
        elif  response.status_code==403:
            return response.text
        elif response.status_code==429:
            if retry==4:
                return '{"status":false,"errors":"Too many requests"}'
        retry=retry+1
        logger.info(f"request failed---> retry {retry} times  response code:{response.status_code}")
    logger.critical(f"request failed---> {input}")
    return None
  


def create_kayak_apache_mst(pos,logger):
  retry=0
  while retry<5:
    try:
        url = "https://www.kayak.com/a/api/experiments/client"
        proxy_count=random.randint(0, len(proxy_ip) - 1)
        if retry<2:
            proxies = {"http":f'{proxy_ip[proxy_count]}:{datacenter_port.get(pos)}'}
        else:
            proxies = {"http":f'{proxy_ip[proxy_count]}:{residential_port.get(pos)}'}
      
        response = requests.request("GET", url, headers=headers,proxies=proxies)
        data['kayak_mc']=re.findall("kayak.mc=(.*?);", response.headers['set-cookie'])[0]
        data['apache']=re.findall("Apache=(.*?);", response.headers['set-cookie'])[0]
        data['mst_ADIrlA']=re.findall("mst_ADIrlA=(.*?);", response.headers['set-cookie'])[0]
        data['cluster']=re.findall("cluster=(.*?);", response.headers['set-cookie'])[0]
        logger.info("Created create_kayak_apache_mst id fuction")
        break
    except Exception as e:
        retry=retry+1
        time.sleep(2)
        logger.error(f"Error in create_kayak_apache_mst fuction retry-->{retry} times | {e}")


def create_mst_iBfK2w(pos,logger):
  retry=0
  while retry<5:
    try:
        url = "https://www.kayak.co.in/h/mobileapis/currency/list"
        proxy_count=random.randint(0, len(proxy_ip) - 1)
        if retry<2:
            proxies = {"http":f'{proxy_ip[proxy_count]}:{datacenter_port.get(pos)}'}
        else:
            proxies = {"http":f'{proxy_ip[proxy_count]}:{residential_port.get(pos)}'}
        response = requests.request("GET", url, headers=headers,proxies=proxies)
        mst_token=re.findall("mst_(.*?);", response.headers['set-cookie'])[0]
        data['mst_key']=f"mst_{mst_token.split('=')[0]}"
        data['mst_value']=mst_token.split("=")[1]
        data['kayak']=re.findall("kayak=(.*?);",response.headers['set-cookie'])[0]
        logger.info("Created create_mst_iBfK2w id fuction")
        break
    except Exception as e:
        time.sleep(2)
        retry=retry+1
        logger.error(f"Error in create_mst_iBfK2w fuction retry-->{retry} times | {e}")

def create_p1_med_sid(pos,logger,token_value):
  retry=0
  while retry<5:
    try:
        url = "https://www.kayak.co.in/a/api/device/session"
        payload = "udid=a5ccb829e21e28f5&authToken=Ms3ImggRbg9Q1pltXf0gQN&model=Phone&appId=kayakFree&appDist=store&tz=Asia%2FKolkata&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=61f37bdf-7fe4-4daa-96e2-b1020351ce1c&adjustTracker=Organic&adjustDeviceId=bf57ad133462781235d14356db8497d4&dataSharingOptOut=false"
        header = {
        'User-Agent': 'kayakandroidphone/170.3 Android 9 API 28 (Phone; Custom; Genymotion)',
        'Accept-Language': 'en-US',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate',
        }
        proxy_count=random.randint(0, len(proxy_ip) - 1)
        if retry<2:
            proxies = {"http":f'{proxy_ip[proxy_count]}:{datacenter_port.get(pos)}'}
        else:
            proxies = {"http":f'{proxy_ip[proxy_count]}:{residential_port.get(pos)}'}
      
        response=requests.post(url, headers=header, data=payload,proxies=proxies)
        data['p1_med_sid']=re.findall('"sid":"(.*)\",',response.text)[0]
        logger.info("Created p1_med_sid id fuction")
        break
    except Exception as e:
      time.sleep(2)
      retry=retry+1
      logger.error(f"Error in p1_med_sid fuction retry-->{retry} times | {e}")

def set_currency(pos,logger,cookie,currency,token_value):
    retry=0
    while retry<4:
        try:
            proxy_count=random.randint(0, len(proxy_ip) - 1)
            if retry<2:
                proxies = {"http":f'{proxy_ip[proxy_count]}:{datacenter_port.get(pos)}'}
            else:
                proxies = {"http":f'{proxy_ip[proxy_count]}:{residential_port.get(pos)}'}
            if currency is None:
                currency_dict={"IN":'INR',"TH":'THB',"VN":'VND',"MY":'MYR',"ID":'IDR',"SG":'SGD',"PH":'PHP',"JP":'JPY',"HK":'HKD',"TW":'TWD',"AU":'AUD','KR':'KRW',"US":'USD',"TH":"THB"}
                currency=currency_dict[pos.upper()]
            url = f"https://www.kayak.com.hk/s/mobileutil?action=setcurrency&currency={currency}"
            payload={}
            Point_of_Sale={"AU":"kayak.com.au", "HK":"kayak.com.hk", "ID":"kayak.co.id", "IN":"kayak.co.in", "JP":"kayak.co.jp", "KR":"kayak.co.kr", "MY":"kayak.com.my", "PH":"kayak.com.ph", "SG":"kayak.sg", "VN":"kayak.vn.kayak.com","TH":"kayak.co.th"}
            time.sleep(3)
            headers = {
            'Host': 'www.kayak.com.hk',
            'User-Agent': 'kayakandroidphone/170.3 Android 9 API 28 (Phone; Custom; Genymotion)',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'Cookie': f'p1.med.token={token_value}; mst_ADIrlA={cookie["mst_ADIrlA"]}; p1.med.sid={cookie["p1_med_sid"]}; {cookie["mst_key"]}={cookie["mst_value"]}; Apache={cookie["apache"]}; kayak.mc={cookie["kayak_mc"]}; kayak={cookie["kayak"]};; kmkid=A-LdUFdHq_RPCiagP70cF7M; cluster={cookie["cluster"]}; Apache={cookie["apache"]}; cluster={cookie["apache"]}; kayak={cookie["kayak"]};; kayak.mc={cookie["kayak_mc"]}; mst_ADIrlA={cookie["mst_ADIrlA"]}'
            }
            response = requests.request("POST", url, headers=headers, data=payload,proxies=proxies)
            logger.info("Created set currency  fuction")
            return True
        except Exception as e:
            
            retry=retry+1
            logger.error(f"Error in set currency fuction retry-->{retry} times | {e}")


def create_cookie(pos,logger,cookie_id,token_value):
    create_kayak_apache_mst(pos,logger)
    create_mst_iBfK2w(pos,logger)
    create_p1_med_sid(pos,logger,token_value)
    logger.info("Cookie Created")
    with open(f'kayak_mobile_cookie_{cookie_id}.json', 'w') as f:
        json.dump(data, f)