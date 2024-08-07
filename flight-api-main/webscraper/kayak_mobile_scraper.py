import json
from webscraper.kayak_mobile_utils import request_fuction
import os
import hashlib 
import logging

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kayak_scraper_log.log')#log filename
logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
#                             datefmt='%m-%d-%y %H:%M:%S')
# fh = logging.handlers.TimedRotatingFileHandler('logs/kayak_scraper_log.log', when='S', interval=3600)#log filename
# fh.setFormatter(formatter)
# logger.addHandler(fh)


class KayakMobileScraper:
    def kayakmobile(self,input_dict):
        
        is_one_way=input_dict.is_one_way
        outbound_date=input_dict.outbound_date.strftime("%Y-%m-%d")
        if input_dict.inbound_date is not None:
            inbound_date=input_dict.inbound_date.strftime("%Y-%m-%d")
        if is_one_way == False and input_dict.inbound_date is None:
            return '{"status":true,"errors":"If one way is false.Inbound date must be given"}'
        
        cabin_class=input_dict.cabin_class
        if cabin_class.lower() not in ['economy','premium-economy','business','first']:
            return '{"status":true,"errors":"cabin class must be economy,premium-economy,business,first"}'
        pos=input_dict.pos
        origin_iata_code=input_dict.origin_iata_code
        destination_iata_code=input_dict.destination_iata_code
        
        
        flight_selection=input_dict.flight_selection
        if flight_selection=="Cheapest":
            flight_selection='price'
        num_of_adults=int(input_dict.num_of_adults)
        children_ages=input_dict.children_ages
        num_of_children = len(children_ages)
        passengers = ["ADT"] * num_of_adults + ["CHD"] * num_of_children
        Point_of_Sale={"AU":"kayak.com.au", "HK":"kayak.com.hk", "ID":"kayak.co.id", "IN":"kayak.co.in", "JP":"kayak.co.jp", "KR":"kayak.co.kr", "MY":"kayak.com.my", "PH":"kayak.com.ph", "SG":"kayak.sg", "VN":"kayak.vn.kayak.com","TW":"tw.kayak.com","US":'kayak.com',"TH":"kayak.co.th"}
        region=Point_of_Sale[pos]
        url =f"https://www.{Point_of_Sale[pos]}/i/api/search/v1/flights/poll?jsonFeatures=NumericPrices"
        currency=input_dict.currency
        logger.info(f"request url-->{url}")
        if is_one_way == False:
            if  inbound_date < outbound_date:
                return '{"status":true,"errors":"Inbound date must be greater than or equal to outbound date"}'
            payload={"airports":"v1","cabinClass":f"{cabin_class.lower()}","carryOnBags":0,"checkedBags":0,"covidBadge":"v1","displayMessages":"v1","filterParams":{"includeFilterHistory":True,"include":["airlines","airports","arrival","cabinClass","departure","equipment","flexOption","layover","legLength","price","quality","bookingSites","stops","stopsPerLeg"]},"gatedSignIn":False,"sort":[""+flight_selection+""],"inlineAdData":"v1","legs":[{"date":f"{outbound_date}","destination":{"airports":[""+f"{destination_iata_code}"+""],"locationType":"airports"},"flex":"exact","origin":{"airports":[""+f"{origin_iata_code}"+""],"locationType":"airports"}},{"date":f"{inbound_date}","destination":{"airports":[""+f"{origin_iata_code}"+""],"locationType":"airports"},"flex":"exact","origin":{"airports":[""+f"{destination_iata_code}"+""],"locationType":"airports"}}],"maxResults":10000,"modalDialogParams":{"version":"v1"},"passengers":passengers,"priceMode":"total","results":{"cabinClass":True},"savingMessage":"v1"}
        elif is_one_way == True:
            payload={"airports":"v1","cabinClass":f"{cabin_class.lower()}","carryOnBags":0,"checkedBags":0,"covidBadge":"v1","displayMessages":"v1","filterParams":{"includeFilterHistory":True,"include":["airlines","airports","arrival","cabinClass","departure","equipment","flexOption","layover","legLength","price","quality","bookingSites","stops","stopsPerLeg"]},"gatedSignIn":False,"sort":[""+flight_selection+""],"inlineAdData":"v1","legs":[{"date":f"{outbound_date}","destination":{"airports":[""+f"{destination_iata_code}"+""],"locationType":"airports"},"flex":"exact","origin":{"airports":[""+f"{origin_iata_code}"+""],"locationType":"airports"}}],"maxResults":10000,"modalDialogParams":{"version":"v1"},"passengers":passengers,"priceMode":"total","results":{"cabinClass":True},"savingMessage":"v1"}
        payload=json.dumps(payload)
        response=request_fuction(url,payload,pos,logger,input_dict,currency)
        if response is None:
            return None
        elif 'errors' in json.loads(response):
            return response
        all_result=self.parse_details(url, response,region,input_dict)
        return {"status":True, "detail":[], "result":all_result}
    
    def parse_details(self,url,response,region,input):
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
            all_items_list=[]
            flight_id=page_json.get('resultDetails','')
            for index, block in enumerate(flight_id, start=1):
                rank_start=index
                review_id=block.get('resultId','')
                test_legs_id=block.get("legs","")   
                if len(test_legs_id)==2:            
                    legs_id=block.get("legs","")[0]             
                    if len(page_json.get('legs'))==2:
                        for block1 in  page_json.get('legs')[0]:#intial legs in json
                            if  legs_id==block1.get("id",""):#match leg id
                                segments_id=block1.get('segments','')
                                airline_full_name_list=[]
                                airline_name_list=[]
                                airline_number_list=[]
                                travel_stop_over_list=[]
                                for segments in page_json.get('segments',''):
                                    for segments_id_two in segments_id:
                                        if  segments.get('id','') == segments_id_two:
                                            for results in  page_json.get("results",""):
                                                if review_id==results.get("resultId"):#match review id
                                                    full_name_airline=page_json.get('airlines','')
                                                    airline_name2= segments.get("airline","")
                                                    airline_name3=full_name_airline.get(airline_name2,'').get('name','')
                                                    airline_new_name=airline_name3
                                                    airline_full_name_list.append(airline_new_name)
                                                    airline_name_list.append(airline_name2)
                                                    airline_number1=segments.get('flightNumber','')
                                                    airline_number_list.append(airline_number1)
                                                    out_arrival_timestamp=block1['arrival'].replace("T"," ")
                                                    out_departure_timestamp=block1['departure'].replace("T"," ")
                                                    stop_over=segments.get('destination','')
                                                    travel_stop_over_list.append(stop_over)                                           
                                                    out_time_duration=block1['duration']
                                                    out_ticket_price=results.get('price','')
                                                    out_cabin_class=results['cabinClass']
                                                    currency=page_json['currency']
                                                    share_url=page_json.get('shareUrl','')
                                                    join_url= f'https://www.{region}'+share_url
                                output=[]   
                                for i in range(len(airline_name_list)):
                                    output.append(f'{airline_name_list[i]}-{airline_number_list[i]}')
                                flight_number=",".join(output)
                                full_name_airlines=airline_full_name_list
                                full_name=','.join(full_name_airlines)
                                airline_name1=airline_name_list
                                airline_name=','.join(airline_name1)
                                travel_stop=travel_stop_over_list[:-1]
                                out_travel_stop_over=','.join(travel_stop)
                                if out_ticket_price:
                                    outbound_flight={"arrival_timestamp":out_arrival_timestamp,"carrier":full_name,"currency":currency,"departure_timestamp":out_departure_timestamp,"flight_number":flight_number,"trip_duration_minutes":out_time_duration,"rate_name":out_cabin_class,"shown_price":out_ticket_price,"travel_stop_over":out_travel_stop_over}
                                    out_flight_details={"outbound_flight":outbound_flight}
                                else:
                                    out_flight_details={}              
                            
                    in_legs_id=block.get("legs","")[1]
                    if len(page_json.get('legs'))==2:
                        for legs_block1 in  page_json.get('legs')[1]:#intial legs in json
                            if  in_legs_id==legs_block1.get("id",""):#match leg id
                                in_segments_id=legs_block1.get('segments','')
                                in_airline_full_name_list=[]
                                in_airline_name_list=[]
                                in_airline_number_list=[]
                                in_travel_stop_over_list=[]
                                for in_segments in page_json.get('segments',''):
                                    for in_segments_id_two in in_segments_id:
                                        if  in_segments.get('id','') == in_segments_id_two:
                                            for in_results in  page_json.get("results",""):
                                                if review_id==in_results.get("resultId"):#match review id
                                                    in_airline_name2= in_segments.get("airline","")
                                                    in_airline_name3=full_name_airline.get(in_airline_name2,'').get('name','')
                                                    in_airline_new_name=in_airline_name3
                                                    in_airline_full_name_list.append(in_airline_new_name)
                                                    in_airline_name_list.append(in_airline_name2)
                                                    in_airline_number1=in_segments.get('flightNumber','')
                                                    in_airline_number_list.append(in_airline_number1)
                                                    in_arrival_timestamp=legs_block1['arrival'].replace("T"," ")
                                                    in_departure_timestamp=legs_block1['departure'].replace("T"," ")
                                                    in_stop_over=in_segments.get('destination','')
                                                    in_travel_stop_over_list.append(in_stop_over)
                                                    in_travel_stop_over='|'.join(in_travel_stop_over_list)
                                                    in_time_duration=legs_block1['duration']
                                                    in_ticket_price=in_results.get('price','')
                                                    in_cabin_class=in_results['cabinClass']
                                                    in_currency=page_json['currency']
                                                    share_url=page_json.get('shareUrl','')
                                                    join_url= f'https://www.{region}'+share_url
                                output=[]   
                                for i in range(len(in_airline_name_list)):
                                    output.append(f'{in_airline_name_list[i]}-{in_airline_number_list[i]}')
                                flight_number=",".join(output)
                                in_full_name_airlines=in_airline_full_name_list
                                in_full_name=','.join(in_full_name_airlines)
                                in_airline_name1=in_airline_name_list
                                in_airline_name=",".join(in_airline_name1) 
                                in_travel_stop=in_travel_stop_over_list[:-1]
                                in_travel_stop_over=','.join(in_travel_stop) 
                                if in_ticket_price:
                                    inbound_flights={"arrival_timestamp":in_arrival_timestamp,"carrier":in_full_name,"currency":in_currency,"departure_timestamp":in_departure_timestamp,"flight_number":flight_number,"rate_name":in_cabin_class,"trip_duration_minutes":in_time_duration,"shown_price":in_ticket_price,"travel_stop_over":in_travel_stop_over}            
                                    in_boudflight_details={"inbound_flight":inbound_flights}
                                else:
                                    in_boudflight_details={}
                        if out_flight_details and in_boudflight_details:
                            rank={"rank":rank_start}
                            final_dict = {**out_flight_details,**in_boudflight_details,**rank} 
                            all_items_list.append(final_dict)  
                            url = {"url":join_url}
                    
                elif len(test_legs_id)==1:            
                    legs_id=block.get("legs","")[0]             
                    if len(page_json.get('legs'))==1:
                        for block1 in  page_json.get('legs')[0]:#intial legs in json
                            if  legs_id==block1.get("id",""):#match leg id
                                segments_id=block1.get('segments','')
                                airline_full_name_list=[]
                                airline_name_list=[]
                                airline_number_list=[]
                                travel_stop_over_list=[]
                                for segments in page_json.get('segments',''):
                                    for segments_id_two in segments_id:
                                        if  segments.get('id','') == segments_id_two:
                                            for results in  page_json.get("results",""):
                                                if review_id==results.get("resultId"):#match review id
                                                    full_name_airline=page_json.get('airlines','')
                                                    airline_name2= segments.get("airline","")
                                                    airline_name3=full_name_airline.get(airline_name2,'').get('name','')
                                                    airline_new_name=airline_name3
                                                    airline_full_name_list.append(airline_new_name)
                                                    airline_name_list.append(airline_name2)
                                                    airline_number1=segments.get('flightNumber','')
                                                    airline_number_list.append(airline_number1)
                                                    out_arrival_timestamp=block1['arrival'].replace("T"," ")
                                                    out_departure_timestamp=block1['departure'].replace("T"," ")
                                                    stop_over=segments.get('destination','')
                                                    travel_stop_over_list.append(stop_over)                                           
                                                    out_time_duration=block1['duration']
                                                    out_ticket_price=results.get('price','')
                                                    out_cabin_class=results['cabinClass']
                                                    currency=page_json['currency']
                                                    share_url=page_json.get('shareUrl','')
                                                    join_url= f'https://www.{region}'+share_url               
                                output=[]   
                                for i in range(len(airline_name_list)):
                                    output.append(f'{airline_name_list[i]}-{airline_number_list[i]}')
                                flight_number=",".join(output)
                                full_name_airlines=airline_full_name_list
                                full_name=','.join(full_name_airlines)
                                airline_name1=airline_name_list
                                airline_name=','.join(airline_name1)
                                travel_stop=travel_stop_over_list[:-1]
                                out_travel_stop_over=','.join(travel_stop)
                                if out_ticket_price:
                                    outbound_flight={"arrival_timestamp":out_arrival_timestamp,"carrier":full_name,"currency":currency,"departure_timestamp":out_departure_timestamp,"flight_number":flight_number,"trip_duration_minutes":out_time_duration,"rate_name":out_cabin_class,"shown_price":out_ticket_price,"travel_stop_over":out_travel_stop_over}
                                    out_flight_details={"outbound_flight":outbound_flight}
                                else:
                                    out_flight_details={}
                    if out_flight_details:
                        rank={"rank":rank_start}
                        final_dict = {**out_flight_details,**rank} 
                        url = join_url
                        all_items_list.append(final_dict)
            return {"elements":all_items_list,'options':input,"snapshot_url":filename,'status':True,'url':url}
        except Exception as e:
            with open("error.txt",'a') as f:
                f.write(str(e))  
            return {'elements':[],'options':input,"snapshot_url":filename,'status':False,'url':url}


