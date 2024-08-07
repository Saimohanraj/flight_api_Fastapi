import requests
import json
import os
import re
from dotenv import load_dotenv
from pathlib import Path
import json

import random
from random import randint
from time import sleep
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
port_pos=['AU','HK','ID','IN','JP','MY','PH','SG','TH','TW','VN']
tokens=[
        {'id':'1','token':'udid=d74d24d353ca1112&secureHash=A4FA6C3A0E964C0988381B399A4AAF412BA95B8A3EBA8F0C4C56B98F3BE0BCA6&model=SM-G965N&osVersion=7.1.2&appId=kayakFree&appDist=store&tz=Asia%2FCalcutta&locale=en_US&carrierName=Hexcom%20India&connectionType=none&advertisingId=&dataSharingOptOut=false'},
        {'id':'2','token':'udid=a5ccb829e21e28f5&secureHash=A334174E332B27BB8BA99AC08597376FE4C622C04F823AB47E819A97D2813C91&model=SM-G945N&osVersion=7&appId=kayakFree&appDist=store&tz=Asia%2FCalcutta&locale=en_US&carrierName=Hexcom%20India&connectionType=none&advertisingId=&dataSharingOptOut=false'},
        {'id':'3','token':'udid=0d741e7db3506f54&secureHash=21345051D55AA2F8DE3F5E93A8D035C2EB736A2248BDC33F54AE22194C837675&model=SM-G961N&osVersion=8&appId=kayakFree&appDist=store&tz=Asia%2FCalcutta&locale=en_US&carrierName=Hexcom%20India&connectionType=none&advertisingId=&dataSharingOptOut=false'},
        {'id':'4','token':'udid=b2aada5e2ce2dcc0&secureHash=6924198EDFF945DA6B52CADD1F46EFBBD028E11AD9A970679C77AF353D8B9865&model=SM-N976N&osVersion=9&appId=kayakFree&appDist=store&tz=Asia%2FCalcutta&locale=en_US&carrierName=Hexcom%20India&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'5','token':'udid=47e807b2526e91af&secureHash=779374EFF6F0C3A552BF1FA809F60182ACCBFDB8ECF5F4DF58A496DDF7EE9AC6&model=SM-N978N&osVersion=9&appId=kayakFree&appDist=store&tz=Asia%2FCalcutta&locale=en_US&carrierName=Hexcom%20India&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'6','token':'udid=31b7f6d150da5924&secureHash=033F1F6BC0B3549F089D71405A945C268A6263342B8C66D04939B215208E65CD&model=SM-G966N&osVersion=10&appId=kayakFree&appDist=store&tz=Asia%2FCalcutta&locale=en_US&carrierName=Hexcom%20India&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'7','token':'udid=f531c7cdb7117331&secureHash=D4534649802029937D5F40EAA4E2349F71EB57D5D504A05DD7BCAF957DB9C5BE&model=Phone&osVersion=11&appId=kayakFree&appDist=store&tz=America%2FNew_York&locale=en_US&carrierName=Hexcom%20India&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'8','token':'udid=8e169bdb1b44d3a&secureHash=EE44C081012E5AE8563326B0DE44034DC4569990791DA262C16FD45FCB45AD0A&model=unknown&osVersion=9&appId=kayakFree&appDist=store&tz=America%2FNew_York&locale=en_US&carrierName=Hexcom%20India&connectionType=vpn&advertisingId=&dataSharingOptOut=false'},
        {'id':'9','token':'udid=2ac0337014ea9c39&secureHash=1B1F65B33B9A73747859B659F53DF97F9A85512736CDF2D69C70F254FF264D25&model=unknown&osVersion=9&appId=kayakFree&appDist=store&tz=America%2FNew_York&locale=en_US&carrierName=Hexcom%20India&connectionType=vpn&advertisingId=&dataSharingOptOut=false'},
        {'id':'10','token':'udid=4121cd3e4de724c3&secureHash=2A0A7CAEDAF7AD0B0C2DEE7FCA45C55D6AE309915139E5CEAFEE604B92A7791C&model=unknown&osVersion=9&appId=kayakFree&appDist=store&tz=America%2FNew_York&locale=en_US&carrierName=Hexcom%20India&connectionType=vpn&advertisingId=&dataSharingOptOut=false'},
        {'id':'11','token':'udid=7f6e2647a61ef473&secureHash=75BA1BA4A420856F9D8B3450CBE1E921530EE6724BB199876667472979BB2077&model=unknown&osVersion=9&appId=kayakFree&appDist=store&tz=America%2FNew_York&locale=en_US&carrierName=Hexcom%20India&connectionType=vpn&advertisingId=&dataSharingOptOut=false'},
        {'id':'12','token':'udid=1a18c09c87886d9f&secureHash=13A42C608900604DCE0CB85128886FC00C0B52D91D49597C72AD924CAA71ADB6&model=unknown&osVersion=12&appId=kayakFree&appDist=store&tz=America%2FNew_York&locale=en_US&carrierName=Hexcom%20India&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'13','token':'udid=cfe0b37e642b0b97&secureHash=0F31A1327D22976F028DA6DF5F0E76786F4870B5B74AA48F4B32C751F31B4397&model=Pixel&osVersion=12&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'14','token':'udid=b2219f2d4d17403d&secureHash=BA8BE71569293EF165198B4DC90312AD087B16DCAC7B2C8AAE1B8690786F8355&model=Pixel&osVersion=12&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'15','token':'udid=614e666f5521ebae&secureHash=3FB14E3E566B39B0ECD300D2FFCA9A08841520E4FFA20A7F1152878E8F59E942&model=Pixel&osVersion=12&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'16','token':'udid=ef46a4ff763339ec&secureHash=2BFE5E441C7679D552C7D78840CE1F9DF312A0A88C2F1150ACB1E4A390ACEAB6&model=Pixel&osVersion=12&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'17','token':'udid=10c30f13ed4f2e1&secureHash=0DCB7E27148F8C831A39EAAD6BAC96A4A34102B09B75FB4144425872DA88C0CF&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'18','token':'udid=b473f9f70017dbae&secureHash=6B3B37A3D13EB49F4E5C3ECCD4935F6D7B63DD375CD536BBF7F25553F477B31E&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'19','token':'udid=7797282827c117f4&secureHash=D504FF878DD943C52EBA34377772E57FD11FE9A0A5068962D97AB91ADDAC3F1C&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'20','token':'udid=8c327257e2959de1&secureHash=FBE6FD55103F188DDFB614F7B895AF6AD30EDA7B82ADCAE49A893E719C226A04&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'21','token':'udid=af0e053eda3a7b14&secureHash=F2BCF19966748A96D0EB7F005DDB64E80D42F5A01F13810B622F846078FD4372&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'22','token':'udid=e8a8ae4ab9a819b3&secureHash=1FA93B46344356B3A2DD83F6A3D1B416739F1CA2EA0E4E1CA94FB65A94F39650&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'23','token':'udid=ad32587afd467d10&secureHash=D08C94D8D681F2CB95F7EB5ADB2D8FEF2C80E725248408860986E1A5C4E5FB76&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'24','token':'udid=ae3bf6d79f9ea0d2&secureHash=63B8F8BA7556C3C758215506CC935BE3E157A1101A10C17E010ACE4AB4F530B4&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},              
        {'id':'25','token':'udid=bb846da8313cc341&secureHash=B412260BB359B0633BCCA7DDD47DF2A36B5EF24AD22AA7FE8A6AC75D1766381A&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'26','token':'udid=51681929a5ca1a4b&secureHash=1B270F754E3C20F0BAF7E3D9EFA7C13C00F91C7973D8E72ADACC9FA3E067F508&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'27','token':'udid=2e55494dfe2b29d8&secureHash=19765AE06D14AF80475C61607AE32D210C3EA9ADD738D36D4CC37841B84C240B&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'28','token':'udid=2bbe08795257db55&secureHash=B80C8AA89F38F9DE600A8F1AF0DD514551329CD3075D8D2077DC6EF00278B81B&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},              
        {'id':'29','token':'udid=5053a6a205973ce6&secureHash=815AE31B39AB6E4D4E5E1F5C5D51086416678C9032ABB2D2C330BCC10E40A92C&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
        {'id':'30','token':'udid=6e86348a2e0fd04a&secureHash=5CBFB742EADF26DD9D071DB9B92FA52AB76D5B22D349F92AF1FCEB68E56CAF00&model=Pixel&osVersion=11&appId=kayakFree&appDist=store&tz=GMT&locale=en_US&carrierName=Android&connectionType=wifi&advertisingId=&dataSharingOptOut=false'},
    ]


def second_api_request_fuction(url,pos,logger,input,region,currency):
    """second_api_request_fuction will process the data collection request and check if cookie is expired or not and if expired will create new cookie"""
    retry=0
    token=random.choice(tokens)
    cookie_id=token.get("id")
    token_value=token.get("token")
    while retry<5:
        if not os.path.exists(f"cookie/kayak_mobile_cookie_{cookie_id}.json"):
            create_cookie(pos,logger,cookie_id,token_value,region)
        try:
            with open(f'cookie/kayak_mobile_cookie_{cookie_id}.json') as f:
                cookie = json.load(f)
        except Exception as e:
            create_cookie(pos,logger,cookie_id,token_value,region)
            logger.info(f"cookie file error:{e}")
            with open(f'cookie/kayak_mobile_cookie_{cookie_id}.json') as f:
                cookie = json.load(f)
        try:
            headers = {
            'User-Agent': 'kayakandroidphone/183.1 Android 7.1.2 API 25 (SM-G965N; samsung; samsung)',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json; charset=UTF-8',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Cookie': f'kayak={cookie["kayak"]}; Apache={cookie["apache"]}; {cookie["mst_AD_key"]}={cookie["mst_AD_value"]}; cluster={cookie["cluster"]}; p1.med.sid={cookie["p1_med_sid"]}; kayak.mc={cookie["kayak_mc"]}; kmkid=A-LdUFdHq_RPCiagP70cF7M; p1.med.sid.http={cookie["p1_med_sid"]}',
            }
            # breakpoint()
            proxy_server=random.choice(proxy_ip)
            if residential_port.get(pos,None) is not None:
                port =residential_port.get(pos,'4468')
            else:
                port=residential_port.get(random.choice(port_pos),'4467')
            proxies = {"http":f'{proxy_server}:{port}','https':f'{proxy_server}:{port}'}
            
            # proxies={'http':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225','https':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225'}
            proxies={'http':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225','https':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225'}
            # sleep(randint(1,3))
            # time.sleep(1)
            response = requests.request("GET", url, headers=headers,proxies=proxies,timeout=10)
        except KeyError as e:
            retry=retry+1
            # logger.info(f"request error---> retry {retry} times  error:{e}")
            create_cookie(pos,logger,cookie_id,token_value,region)
            continue
        except Exception as e:
           retry=retry+1
           
           if retry==4 and  'Connection reset by peer' in str(e) or 'proxy' in str(e):
                logger.info(f"proxy error ===>{proxies}")
                return '{"status":false,"errors":"proxy error"}',None
           continue
        if response.status_code==403:
            logger.info(f"Capcha Detected")
            if retry==5:
                return response.text,None

        if json.loads(response.text).get('error',False):
            if 'anonymous access to kayak API denied'.lower() in json.loads(response.text).get("message",'').lower():
                create_cookie(pos,logger,cookie_id,token_value,region)
            else:
                return response.text ,None
        elif response.status_code==200:
            if len(json.loads(response.text).get('tripset',[]))>100 or json.loads(response.text).get('completed',False):
                logger.info(f"request success --> 200")
                return response.text,headers
            if retry<=1:
                retry=retry+1    
                search_id= json.loads(response.text).get('searchid','')
                url=f'https://www.{region}/api/search/V8/flight/poll?c=4000&nc=4000&includeSplit=true&getsort=true&showAirlineLogos=true&includeopaques=true&includeFilters=true&cheapestProviderData=true&includeFilterHistory=true&searchid={search_id}&currency={currency}&payment_fees_enabled=true&includeCarryOnFee=false&filterPriceMode=totaltaxes&bags=0&covidBadge=true&modalDialogs=true'
                continue
            return response.text,headers
        retry=retry+1
        # logger.info(f"request failed---> retry {retry} times  response code:{response.status_code}")
    logger.critical(f"request failed---> {input}")
    return None,None
  
def broker_request(headers,url,logger,pos):
    """broker_request will process broker for each tickets"""
    try:
        retry=1
        while retry<3:
            # sleep(randint(1,3))
            proxy_server=random.choice(proxy_ip)
            if residential_port.get(pos,None) is not None:
                port =residential_port.get(pos,'4468')
            else:
                port=residential_port.get(random.choice(port_pos),'4467')
            proxies = {"http":f'{proxy_server}:{port}','https':f'{proxy_server}:{port}'}
            
            # proxies={'http':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225','https':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225'}
            proxies={'http':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225','https':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225'}
            response=requests.get(url,headers=headers,timeout=30,proxies=proxies)
            
            if not json.loads(response.text).get('err',True):
                return response
            else:
                logger.critical(f"broker request failed---> {response}")
                retry=retry+1
        return None
    except:
        return None


def create_kayak_apache_mst(pos,logger,region):
  ''' create_kayak_apache_mst function will create cookie elements'''
  
  retry=0
  while retry<5:
    try:
        url = f"https://www.{region}/a/api/experiments/client"
        proxy_server=random.choice(proxy_ip)
        if residential_port.get(pos,None) is not None:
            port =residential_port.get(pos,'4468')
        else:
            port=residential_port.get(random.choice(port_pos),'4467')
        proxies = {"http":f'{proxy_server}:{port}','https':f'{proxy_server}:{port}'}
        
        # proxies={'http':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225','https':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225'}
        proxies={'http':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225','https':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225'}
        response = requests.request("GET", url, headers=headers,proxies=proxies)
        data['kayak']=re.findall("kayak=(.*?);",response.headers['set-cookie'])[0]
        data['kayak_mc']=re.findall("kayak.mc=(.*?);", response.headers['set-cookie'])[0]
        data['apache']=re.findall("Apache=(.*?);", response.headers['set-cookie'])[0]
        data['cluster']=re.findall("cluster=(.*?);", response.headers['set-cookie'])[0]
        mst_token=re.findall("mst_(.*?);", response.headers['set-cookie'])[0]
        data['mst_AD_key']=f"mst_{mst_token.split('=')[0]}"
        data['mst_AD_value']=mst_token.split("=")[1]
        # logger.info("Created create_kayak_apache_mst id fuction")
        break
    except Exception as e:
        retry=retry+1
        logger.error(f"Error in create_kayak_apache_mst fuction retry-->{retry} times | {e}")


def create_mst_iBfK2w(pos,logger,region):
  """create_mst_iBfK2w function will create cookie elements"""
  retry=0
  while retry<5:
    try:
        url = f"https://www.{region}/h/mobileapis/currency/list"
        proxy_server=random.choice(proxy_ip)
        if residential_port.get(pos,None) is not None:
            port =residential_port.get(pos,'4468')
        else:
            port=residential_port.get(random.choice(port_pos),'4467')
        proxies = {"http":f'{proxy_server}:{port}','https':f'{proxy_server}:{port}'}
        
        # proxies={'http':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225','https':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225'}
        proxies={'http':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225','https':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225'}
        # sleep(randint(1,3))
        # time.sleep(1)
        response = requests.request("GET", url, headers=headers,proxies=proxies)
        mst_token=re.findall("mst_(.*?);", response.headers['set-cookie'])[0]
        data['mst_key']=f"mst_{mst_token.split('=')[0]}"
        data['mst_value']=mst_token.split("=")[1]
        # logger.info("Created create_mst_iBfK2w id fuction")
        break
    except Exception as e:
        retry=retry+1
        logger.error(f"Error in create_mst_iBfK2w fuction retry-->{retry} times | {e}")

def create_p1_med_sid(pos,logger,token_value,region):
  """create_p1_med_sid function will create cookie elements"""
  retry=0
  while retry<5:
    try:
        url = f"https://www.{region}/a/api/device/session?platform=Android&deviceType=android"
        header = {
        'User-Agent': 'kayakandroidphone/170.3 Android 9 API 28 (Phone; Custom; Genymotion)',
        'Accept-Language': 'en-US',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate',
        }
        proxy_server=random.choice(proxy_ip)
        if residential_port.get(pos,None) is not None:
            port =residential_port.get(pos,'4468')
        else:
            port=residential_port.get(random.choice(port_pos),'4467')
        proxies = {"http":f'{proxy_server}:{port}','https':f'{proxy_server}:{port}'}
        
        # proxies={'http':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225','https':'http://brd-customer-hl_fb2f275a-zone-webautomation_residential:k5ce61lsuav9@brd.superproxy.io:22225'}
        proxies={'http':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225','https':'http://brd-customer-hl_9848bb58-zone-zone_we_kayak_mobile:yv5yh7g4hnsl@brd.superproxy.io:22225'}
        # sleep(randint(1,2))
        # time.sleep(1)
        response=requests.post(url, headers=header, data=token_value,proxies=proxies)
        data['p1_med_sid']=json.loads(response.text).get('sid',None)
        if json.loads(response.text).get('sid',None) is not None:
            # logger.info("Created p1_med_sid id fuction")
            break
        else:
            retry=retry+1
            # logger.error(f"Error in p1_med_sid fuction retry-->{retry} times | {e}")
    except Exception as e:
      retry=retry+1
      logger.error(f"Error in p1_med_sid fuction retry-->{retry} times | {e}")


def create_cookie(pos,logger,cookie_id,token_value,region):
    '''create_cookie fuction will create cookie and save in json for later use'''
    create_kayak_apache_mst(pos,logger,region)
    create_mst_iBfK2w(pos,logger,region)
    create_p1_med_sid(pos,logger,token_value,region)
    logger.info("Cookie Created")
    with open(f'cookie/kayak_mobile_cookie_{cookie_id}.json', 'w') as f:
        json.dump(data, f)
    
