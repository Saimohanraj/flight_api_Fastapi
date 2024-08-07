import json
from webscraper.kayak_utils import second_api_request_fuction,broker_request
import os
import hashlib 
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from random import randint
from time import sleep
import re

if not os.path.exists('logs'):
    os.makedirs('logs')


#log
CURRENT_DATETIME = datetime.now()
CURRENT_DATE = CURRENT_DATETIME.strftime("%Y-%m-%d")
DATE=CURRENT_DATE.replace("-","_")

logging.basicConfig(filename=f'logs/kayak_scraper_log_{DATE}.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(f'logs/kayak_scraper_log_{DATE}.log')

class KayakMobileScraper:
    def kayakmobile(self,input_dict):
        is_one_way=input_dict.is_one_way
        outbound_date=input_dict.outbound_date.strftime("%Y-%m-%d")
        input_dict.outbound_date=outbound_date
        origin_iata_code=input_dict.origin_iata_code.upper()
        destination_iata_code=input_dict.destination_iata_code.upper()
        yesterday = datetime.now() - timedelta(1)
        yesterday = yesterday.strftime("%Y-%m-%d")
        if not yesterday <= outbound_date:
            return '{"status":true,"errors":"Invalid date"}'
        if input_dict.inbound_date is not None:
            inbound_date=input_dict.inbound_date.strftime("%Y-%m-%d")
            input_dict.inbound_date=inbound_date
        if is_one_way == False and input_dict.inbound_date is None:
            return '{"status":true,"errors":"If one way is false.Inbound date must be given"}'
        cabin_class=input_dict.cabin_class
        if cabin_class.lower() not in ['economy','premium-economy','business','first']:
            return '{"status":true,"errors":"cabin class must be economy,premium-economy,business,first"}'
        pos=input_dict.pos
        
        if origin_iata_code==destination_iata_code:
            return '{"status":true,"errors":"origin and destination should not be same"}'
        num_of_adults=int(input_dict.num_of_adults)
        children_ages=input_dict.children_ages
        num_of_children = len(children_ages)
        currency=input_dict.currency

        Point_of_Sale={"AU":"kayak.com.au", "HK":"kayak.com.hk", "ID":"kayak.co.id", "IN":"kayak.co.in", "JP":"kayak.co.jp", "KR":"kayak.co.kr", "MY":"kayak.com.my", "PH":"kayak.com.ph", "SG":"kayak.sg", "VN":"vn.kayak.com","TW":"tw.kayak.com","US":'kayak.com',"TH":"kayak.co.th"}
        region=Point_of_Sale[pos]
        currency_dict={"IN":'INR',"TH":'THB',"VN":'VND',"MY":'MYR',"ID":'IDR',"SG":'SGD',"PH":'PHP',"JP":'JPY',"HK":'HKD',"TW":'TWD',"AU":'AUD','KR':'KRW',"US":'USD',"TH":"THB"}
        if currency is None:
            currency=currency_dict[pos.upper()]
        rate_name={'econony':'e','first':'f','premium-economy':'p','business':'b'}
        cabin_class=rate_name.get(cabin_class.lower(),'e')
            
        if is_one_way is True:
            url = f"https://www.{region}/api/search/V8/flight/poll?c=4000&nc=4000&includeSplit=true&getsort=true&showAirlineLogos=true&includeopaques=true&includeFilters=true&cheapestProviderData=true&includeFilterHistory=true&nearbyO1=false&destination1={destination_iata_code}&depart_date_canon1={outbound_date}&nearbyD1=false&depart_time1=a&origin1={origin_iata_code}&depart_date_flex1=exact&children={num_of_children}&adults={num_of_adults}&cabin={cabin_class}&currency={currency}&payment_fees_enabled=true&includeCarryOnFee=false&filterPriceMode=totaltaxes&bags=0&pageType=FRONT_DOOR&covidBadge=true&modalDialogs=true"
        else:
            if  inbound_date < outbound_date:
                return '{"status":true,"errors":"Inbound date must be greater than or equal to outbound date"}'
            url=f"https://www.{region}/api/search/V8/flight/poll?c=4000&nc=4000&includeSplit=true&getsort=true&showAirlineLogos=true&includeopaques=true&includeFilters=true&cheapestProviderData=true&includeFilterHistory=true&destination1={destination_iata_code}&destination2={origin_iata_code}&depart_time2=a&depart_time1=a&nearbyO1=false&nearbyO2=false&origin2={destination_iata_code}&depart_date_canon2={inbound_date}&depart_date_canon1={outbound_date}&nearbyD2=false&nearbyD1=false&depart_date_flex2=exact&origin1={origin_iata_code}&depart_date_flex1=exact&children={num_of_children}&childAge1=11&adults={num_of_adults}&cabin={cabin_class}&currency={currency}&payment_fees_enabled=true&includeCarryOnFee=false&filterPriceMode=totaltaxes&bags=0&pageType=FRONT_DOOR&covidBadge=true&modalDialogs=true"
        # sleep(randint(1,10))
        
        response,headers=second_api_request_fuction(url,pos,logger,input_dict,region,currency)
        if response is None:
            return None
        if json.loads(response).get('errors',False) or json.loads(response).get('error',False):
            return response
        
        all_result=self.parse_details_2(url, response,region,dict(input_dict),currency,headers,pos)
        return {"status":True, "detail":[], "result":all_result}
    
    def parse_details_2(self,url,response,region,input,currency,headers,pos):
        try:
            if not os.path.exists('html_files'):
                os.makedirs('html_files')  
            file_directory='html_files'
            hash_obj = hashlib.md5(url.encode("utf-8"))
            filename = hash_obj.hexdigest()+".json"
            file_path = os.path.join(file_directory, filename)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response)
            except Exception as e:
                with open("error.txt",'a') as f:
                    f.write('skipped overwriting file\n')  
            page_json=json.loads(response)
            search_id=page_json.get('searchid','')
            tripsets=page_json.get('tripset',[])
            url=page_json.get('shareURL','')
            url= f'https://www.{region}'+url  
            segset=page_json.get('segset',{})
            airportDetails=page_json.get('airportDetails',{})
            airlines=page_json.get('airlines')
            rate_name={'e':'Economy','f':'first','p':'premium-economy','b':'business'}
            rank=1
            all_items_list=[]

            #Filter to get one stop and non stop
            number_of_stops=str(input.get('number_of_stops','any'))
            if number_of_stops=='0':
                tripsets=[d for d in tripsets if d.get('maxstops') == 0]
            elif  number_of_stops=='1':
                tripsets=[d for d in tripsets if d.get('maxstops') == 1 or d.get('maxstops') == 0]
            
            url_list=[]
            for tripset in tripsets[:15]:
                tripid=tripset.get('tripid',None)
                if tripid is not None:
                    url=f'https://www.{region}/api/search/V8/flight/detail?showlogos=true&searchid={search_id}&resultid={tripid}&bags=0&payment_fees_enabled=true&currency={currency}&airlinePolicies=true&includeCarryOnFee=false&pricemode=total'
                    url_list.append(url)

            
            with ThreadPoolExecutor() as executor:
                broker_list=list(executor.map(broker_request, [headers] * 100, url_list,[logger] * 100,[pos]*100))
                executor.shutdown(wait=True)

            broker_status=len([x for x in broker_list if x is not None and x.status_code==200])
            logger.info(f"Number of success broker {str(broker_status)}")
            


            for tripset_count,tripset in enumerate(tripsets,start=0):
                price=tripset.get('lowOriginalTotal',None)
                if price is not None:
                    data={}
                    data['shown_price']=price
                    data['currency']=tripset.get('currencyCode','')
                    data['rate_name']=rate_name.get(tripset.get("cabinClass",''))
                    codeShares=tripset.get('codeShares',[])
                    leg_list=tripset.get('legs',[])
                    for leg_count,(leg,code) in enumerate(zip(leg_list,codeShares),0): 
                        data['trip_duration_minutes']=leg.get("duration",0)
                        code_leg_segment= code.get('legSegments',[])
                        segment_list=leg.get('segments',[])
                        length_segments=len(segment_list)
                        data['flight_number']=[]
                        data['carrier']=[]
                        data['travel_stop_over']=[]
                        stops_duration_minutes=0
                        for count,(segment,laydur) in enumerate(zip(segment_list,code_leg_segment),0):
                            data['flight_number'].append(segset.get(segment,{}).get("airlineCode",'')+"-"+segset.get(segment,{}).get("flightNumber",''))
                            stops_duration_minutes+=laydur.get('laydur',0)
                            hours=laydur.get('laydur',0)//60
                            minutes=laydur.get('laydur',0)%60
                            stop_over=segset.get(segment,{}).get("destinationCode",'')
                            city= airportDetails.get(segset.get(segment,{}).get("destinationCode",''),'').get('city')
                            data['carrier'].append(airlines.get(segset.get(segment,{}).get("airlineCode",''),''))
                            if count==0:
                                data['departure_time']=segset.get(segment,{}).get("leaveTimeAirport","").replace("/","-")+":00"
                            if count==length_segments-1:
                                data['arrival_time']=segset.get(segment,{}).get("arriveTimeAirport","").replace("/","-")+":00"
                                continue
                            data['travel_stop_over'].append(f'{hours}h {minutes}m change planes in {city} ({stop_over})')
                        data['flight_number']= ",".join(data['flight_number'])
                        data['carrier']= ",".join(data['carrier'])
                        data['travel_stop_over']=",".join(data['travel_stop_over'])
                        data['stops_duration_minutes']=stops_duration_minutes
                        if leg_count==0:
                            outbound_flight=data.copy()
                        elif leg_count==1:
                            inbound_flight=data.copy()
                    if rank<=15:
                        broker=  broker_list[tripset_count]
                        duplicate_broker={}
                        if broker is not None:
                            providers=json.loads(broker.text).get('providers',[])
                            broker_rank=1
                            for provider in providers:
                                if broker_rank>10:
                                    break
                                broker_name=provider.get('name','')
                                if re.findall('\d+',provider.get('totalDisplayPrice','')):
                                    broker_price=int( "".join(re.findall('\d+',provider.get('totalDisplayPrice',''))))
                                else:
                                    broker_price=None
                                if broker_name not in duplicate_broker:
                                    duplicate_broker[broker_name]=broker_price
                                else:
                                    continue
                                if len(tripset.get('legs',[]))==2:
                                    outbound_flight['shown_price']=broker_price
                                    inbound_flight['shown_price']=broker_price
                                    all_items_list.append({"outbound_flight":outbound_flight.copy(),"inbound_flight":inbound_flight.copy(),'rank':rank,'broker':broker_name,'broker_rank':broker_rank}.copy())
                                elif len(tripset.get('legs',[]))==1:
                                    outbound_flight['shown_price']=broker_price
                                    all_items_list.append({"outbound_flight":outbound_flight.copy(),'rank':rank,'broker':broker_name,'broker_rank':broker_rank}.copy())
                                broker_rank+=1
                        else:
                            if len(tripset.get('legs',[]))==2:
                                all_items_list.append({"outbound_flight":outbound_flight,"inbound_flight":inbound_flight,'rank':rank,'broker':tripset.get('cheapestProvider',{}).get("name",''),'broker_rank':1}.copy())
                            elif len(tripset.get('legs',[]))==1:
                                all_items_list.append({"outbound_flight":outbound_flight,'rank':rank,'broker':tripset.get('cheapestProvider',{}).get("name",''),'broker_rank':1}.copy())
                    else:
                        if len(tripset.get('legs',[]))==2:
                            all_items_list.append({"outbound_flight":outbound_flight,"inbound_flight":inbound_flight,'rank':rank}.copy())
                        elif len(tripset.get('legs',[]))==1:
                            all_items_list.append({"outbound_flight":outbound_flight,'rank':rank}.copy())
                    rank+=1
            return {"elements":all_items_list,'options':input,"snapshot_url":filename,'status':True,'url':url}  
        except Exception as e:
            with open("error.txt",'a') as f:
                f.write(str(e)) 
            return {'elements':[],'options':input,"snapshot_url":filename,'status':False,'url':url}


