import re
import json
import urllib.parse
import time
import os
import math
import hashlib
from dotenv import load_dotenv
from pathlib import Path
import logging
from webscraper.utlis_web import get_request, post_request, puppetter, selenium_function

try:
    load_dotenv()
except:
    env_path = Path(".env")
    load_dotenv(dotenv_path=env_path)

if not os.path.exists('logs'):
    os.makedirs('logs')

if not os.path.exists('html_files'):
    os.makedirs('html_files')

datacenter_proxy =  {
    'http':  os.getenv("datacenter_proxy"),
    'https': os.getenv("datacenter_proxy").replace("http","https")
}

residential_proxy =  {
    'http':  os.getenv("residential_proxy"),
    'https': os.getenv("residential_proxy").replace("http","https")
}

""" log creation """
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kayak_webscraper_log.log')#log filename
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%m-%d-%y %H:%M:%S')
fh = logging.handlers.TimedRotatingFileHandler('logs/kayak_webscraper_log.log', when='S', interval=3600)#log filename
fh.setFormatter(formatter)
logger.addHandler(fh)

class FlightScraper:
    def __init__(self,outbound_date, inbound_date,is_one_way,pos,origin_iata_code,provider_origin_additional_fields,destination_iata_code,provider_destination_additional_fields,outbound_time_band_start,outbound_time_band_end,inbound_time_band_start,inbound_time_band_end,cabin_class,flight_selection,num_of_adults,children_ages,currency):
        self.retry_count=1
        self.proxy_retry_count=1
        self.all_details=[]
        self.outbound_date=outbound_date
        self.inbound_date=inbound_date
        self.is_one_way=is_one_way
        self.pos=pos
        self.origin_iata_code=origin_iata_code
        self.provider_origin_additional_fields=provider_origin_additional_fields
        self.destination_iata_code=destination_iata_code
        self.provider_destination_additional_fields=provider_destination_additional_fields
        self.outbound_time_band_start=outbound_time_band_start
        self.outbound_time_band_end=outbound_time_band_end
        self.inbound_time_band_start=inbound_time_band_start
        self.inbound_time_band_end=inbound_time_band_end
        self.cabin_class=cabin_class
        self.flight_selection=flight_selection
        self.num_of_adults=num_of_adults
        self.children_ages=children_ages
        self.currency=currency

        self.url=""
         
    def regex_parse(self, pattern, text):
        """ extract text from regex """
        if re.search(pattern, text, re.I):
            data = re.findall(pattern, text, re.I)
            return data[0]
        else:
            return ""
    
    def get_response(self):
        """ get response page"""
        outbound_date=self.outbound_date.strftime("%Y-%m-%d")
        inbound_date=self.inbound_date.strftime("%Y-%m-%d")

        Point_of_Sale={"AU":"kayak.com.au", "HK":"kayak.com.hk", "ID":"kayak.co.id", "IN":"kayak.co.in", "JP":"kayak.co.jp", "KR":"kayak.co.kr", "MY":"kayak.com.my", "PH":"kayak.com.ph", "SG":"kayak.sg", "VN":"vn.kayak.com", "TH":"kayak.co.th", "TW":"tw.kayak.com"}
        len_child=len(self.children_ages)
        if self.children_ages != [""]:
            if len_child!=0:
                child_output = ''.join(['-1L' if age <= 2 else '-11' for age in self.children_ages])
                passengers=f"{self.num_of_adults}adults"+'/'+'children'+child_output
        else:
            passengers=f"{self.num_of_adults}adults"
       
        if self.is_one_way==False:
            is_way_date=outbound_date+"/"+inbound_date
            sort_mode="price"
        else:
            is_way_date=outbound_date
            sort_mode="bestflight"

        if self.flight_selection=="Cheapest":
            flight_select="?sort=price_a"
        else:
            flight_select="?sort=bestflight_a"

        if self.outbound_time_band_start:
            outbound_time_start=str(self.outbound_time_band_start.hour)+":"+str(self.outbound_time_band_start.minute)
            outbound_time_end=str(self.outbound_time_band_end.hour)+":"+str(self.outbound_time_band_end.minute)
            inbound_time_start=str(self.inbound_time_band_start.hour)+":"+str(self.inbound_time_band_start.minute)
            inbound_time_end=str(self.inbound_time_band_end.hour)+":"+str(self.inbound_time_band_end.minute)
            
            takeoff_time=outbound_time_start+","+outbound_time_end+"__"+inbound_time_start+","+inbound_time_end
            takeoff_dict={}
            takeoff_dict["takeoff"]=takeoff_time
            payload_takeoff=str(takeoff_dict)
            pos=self.pos
            url=f"https://www.{Point_of_Sale[pos]}/flights/"+self.origin_iata_code+"-"+self.destination_iata_code+"/"+is_way_date+"/"+f"{passengers}"+"/"+self.cabin_class+"/"+flight_select+"&fs=takeoff="+takeoff_time
            headers = {
                'authority': f'www.{Point_of_Sale[pos]}',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'Cookie': 'Apache=c2FHwA-AAABiU4XW0w-fb-WgPl$A; cluster=4; csid=329037b6-f79a-4a6a-bdaa-86b47e6fe782; kayak=Fm4O_KOYnTuRKLfQgRbe; kayak.mc=AdBjhdeM23CyzYbQpYhizXtG5AE7Xd_G-gPtkwbhy8oKVBTp-Olu5mqmGgfpta4QBNweMde0cx8Bu0OasuJxqXIf8o8Y3mLFmMTQom6YEZRdFnLAuZbBtjbjg1IEiHf9dgzbJCe0bE8Bb9gBIz6BavlOnATuEUMlAbu64kPdO4OT5OasRpaH774d_Y7GsEPM43FqUIBEVKh05yGJlbQi5cq9OJ30A4w8VIQXYIox_Wh4bwoBVYkwT6PriHM3_7T7Ji1XFSY7bQebKoXl58_fQ3RwPPjoMtdvIUnnswHAMhpNJdbAzRK4Wb-efHQ8nuO-EOBAsnJTCP_TdcJ8AoDYxRzBfFyjT1hohfUTbazF_Kds; mst_iBfK2g=FAgFPPxpSpdbg-M54qtgVhfNpEWgVxMl99HEfD4QDBykd3RLuPkcMgRQjxFAnf3XqspGVrZIcpjnlxFAy4crNg; p1.med.sid=R-4qQDNhDNGnhSprLUw8dlA-Fryz4kgfLYFGXOiF9n1dc4yIu6JtguaxjbxNe0S9b',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            self.url=url
            pos_head=Point_of_Sale[pos]
            get_page_response=get_request(url,headers,residential_proxy,logger)
           
            if get_page_response==False:
                return "proxy failure"
            return get_page_response, pos_head, sort_mode, payload_takeoff
            
    def post_response(self,pollnumber):
        """ post response page"""
        response,pos_head,sort_mode,payload_takeoff=self.get_response()
        if response==False:
            return "proxy failure"
        search_id = self.regex_parse(r'"searchId":\s*\"(.*?)\"', response.text)
        script_metadata = self.regex_parse(r'data-type="script-metadata2">\s*(.*?)<', response.text)
        styles_metadata = self.regex_parse(r'data-type="style-metadata2">\s*(.*?)<', response.text)
        r9_version = self.regex_parse(r'name="r9-version"\s*content="(.*?)"', response.text)
        csrf_token=urllib.parse.quote(self.regex_parse(r'"global"\:\{"formtoken":"(.*?)"', response.text))
        ajaxts=str(int(time.time() * 1000))
      
        pagenumber=pollnumber+1

        post_url = f"https://www.{pos_head}/s/horizon/flights/results/FlightSearchPoll?p={pollnumber}"
        print('search_id------>',search_id)
        print("page_number---------->",pagenumber)
       
        headers = {
            'authority': f'www.{pos_head}',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': f'https://www.{pos_head}',
            'referer': str(self.url),
            'Cookie': 'Apache=c2FHwA-AAABiU4XW0w-fb-WgPl$A; cluster=4; csid=329037b6-f79a-4a6a-bdaa-86b47e6fe782; kayak=Fm4O_KOYnTuRKLfQgRbe; kayak.mc=AdBjhdeM23CyzYbQpYhizXtG5AE7Xd_G-gPtkwbhy8oKVBTp-Olu5mqmGgfpta4QBNweMde0cx8Bu0OasuJxqXIf8o8Y3mLFmMTQom6YEZRdFnLAuZbBtjbjg1IEiHf9dgzbJCe0bE8Bb9gBIz6BavlOnATuEUMlAbu64kPdO4OT5OasRpaH774d_Y7GsEPM43FqUIBEVKh05yGJlbQi5cq9OJ30A4w8VIQXYIox_Wh4bwoBVYkwT6PriHM3_7T7Ji1XFSY7bQebKoXl58_fQ3RwPPjoMtdvIUnnswHAMhpNJdbAzRK4Wb-efHQ8nuO-EOBAsnJTCP_TdcJ8AoDYxRzBfFyjT1hohfUTbazF_Kds; mst_iBfK2g=FAgFPPxpSpdbg-M54qtgVhfNpEWgVxMl99HEfD4QDBykd3RLuPkcMgRQjxFAnf3XqspGVrZIcpjnlxFAy4crNg; p1.med.sid=R-4qQDNhDNGnhSprLUw8dlA-Fryz4kgfLYFGXOiF9n1dc4yIu6JtguaxjbxNe0S9b',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-csrf': str(csrf_token),
            'x-r9-blue-green-version': str(r9_version),
            'x-requested-with': 'XMLHttpRequest',
            'x-requestid': 'flights#results#ogNMhY',
            }
        if payload_takeoff!="":
            payload_takeoff=payload_takeoff.replace("'",'"')
        else:
            payload_takeoff=""

        payload={
            "searchId": str(search_id),
            "poll": "true",
            "pollNumber": str(pollnumber),
            "applyFilters": "true",
            "filterState": payload_takeoff,
            "useViewStateFilterState": "false",
            "pageNumber": str(pagenumber),
            "watchedResultId": "",
            "append": "true",
            "sortMode": sort_mode,
            "ascending": "true",
            "priceType": "daybase",
            "requestReason": "PAGINATE",
            "phoenixRising": "true",
            "isSecondPhase": "false",
            "displayAdPageLocations": "left,bottom-left,bottom,upper-right,right",
            "existingAds": "true",
            "activeLeg": "-1",
            "hasFilterPreferences": "false",
            "view": "list",
            "renderPlusMinusThreeFlex": "false",
            "renderAirlineStopsMatrix": "false",
            "requestAlternateFlexDates": "false",
            "ajaxts": str(ajaxts),
            "scriptsMetadata": str(script_metadata),
            "stylesMetadata": str(styles_metadata),
            "r9version": str(r9_version)
        }
        post_page_response = post_request(post_url, headers, payload,residential_proxy,logger)
        return post_page_response
            
    def main(self):
        """ start the script"""
        response,pos_head,sort_mode,payload_takeoff=self.get_response()#get page response
        if response==False:
            return "proxy failure"
        
        flight_total_count=self.regex_parse(r'"totalCount":(.*?),', response.text)
        flight_count_str = self.regex_parse(r'"filtered":(.*?)\}', response.text)
        
        if flight_total_count=='0' and flight_count_str=='0':
            logger.info("<----------no fights found--------->")
            return [{"error":"no flights found","msg":"There are no flights available on your chosen dates. Try changing the dates of your search"}]
        
        if flight_count_str:
            if flight_count_str!='0':
                flight_count = int(flight_count_str)
            elif flight_count_str=='0':
                flight_count = 1
        else:
            flight_count = 0
        page_range=math.ceil(flight_count / 15)
        print("flightcount------>",flight_count)
        page_range=2
        for pollnumber in range(0,page_range):
            post_response_content=self.post_response(pollnumber)#post page response
            if post_response_content==False:
                return "proxy failure"
        
            all_item_details = self.parse_flight_detail(post_response_content,pollnumber)
            if all_item_details is not None:
                self.all_details.extend(all_item_details)
        
        if self.all_details!=[]:
            item=[]
            for i, block in enumerate(self.all_details, start=1):
                block['rank']=i
                item.append(block)
            self.save_to_json(self.all_details, 'flight_details.json')
            return item
        else:
            return None
    
    def parse_flight_detail(self, pages_response,pollnumber):
        """ parse fight detail information """
        
        hash_obj = hashlib.md5(self.url.encode("utf-8"))
        filename = hash_obj.hexdigest()+'.html'
        file_path = os.path.join('html_files', filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(pages_response.text)
        pages = pages_response.text.replace('\\', '')

        if re.search(r'state\:\s*{"resultIds"\:(.*?),"results"', pages):
            resultids=re.findall(r'state\:\s*{"resultIds"\:\[(.*?)\],"results"',pages)
            aaa=''.join(resultids).split(',')
            modified_list = [s.replace('"', '') for s in aaa]
            
        if re.search(r'],"results"\:(.*?\}\})\,"resultsChanged"',pages):
            page_texts = self.regex_parse(r'],"results"\:(.*?\}\})\,"resultsChanged"',pages)
            
            all_item_details = []
            flight_json_all = json.loads(page_texts)
            for resultid in modified_list:
                flight_json=flight_json_all.get(resultid,'')
                if flight_json.get('resultId',''):
                    resultid=flight_json.get('resultId','')
                    legs = flight_json.get('legs', [])
                    
                    if len(legs)==2:
                        first_leg = legs[0]
                        out_trip_duration_minutes=first_leg.get("legDurationMinutes","")
                        segments = first_leg.get('segments', [])
                        if len(segments)==1:
                            first_segment = segments[0]
                            airline = first_segment.get('airline',"")
                            if airline:
                                out_carrier = airline.get('name', "")
                                out_flight_code=airline.get('code', "")
                                out_flight_no = first_segment.get('flightNumber', "")
                                out_flight_number=f'{out_flight_code}-{out_flight_no}'
                                out_departure_time = first_segment.get('departure', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                out_arrival_time = first_segment.get('arrival', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                old_out_travel_stop_over = first_segment.get('layover', {}).get('message', "")
                                out_travel_stop_over=self.regex_parse(r'Change\s*planes\s*in\s*(.*?)\s*\(', old_out_travel_stop_over)
                                old_out_travel_stop_duration = first_segment.get('layover', {}).get('duration', "")
                                if out_travel_stop_over:
                                    outnew_travel_stop_over=old_out_travel_stop_duration+' stopover '+old_out_travel_stop_duration
                                else:
                                    outnew_travel_stop_over=''
                                if old_out_travel_stop_duration:
                                    numeric_values = re.findall(r'\d+', old_out_travel_stop_duration)
                                    
                                    out_hours = int(numeric_values[0])
                                    out_minutes = int(numeric_values[1])  
                                    out_travel_stop_duration = out_hours * 60 + out_minutes
                                else:
                                    out_travel_stop_duration=''
                                out_cabin_class = first_segment.get('cabinDisplay', "")
                        elif len(segments)>1:
                            lay_over=segments
                            first_segment=segments[0]
                            second_segment=segments[-1]
                            airline1 = first_segment.get('airline','')
                            airline2 = second_segment.get('airline','')
                            if airline1 and airline2:
                                out_departure_time = first_segment.get('departure', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                out_carrier_flight_name=[]
                                out_carrier_flight_code=[]
                                out_carrier_flight_number=[]
                                lay_over_stops=[]
                                lay_over_stop_duration=[]
                                rate_cabin=[]
                                for lay in lay_over:
                                    lay_point=lay.get('layover',{}).get('message', '')
                                    lay_duration=lay.get('layover',{}).get('duration','')
                                    flight_name=lay.get('airline',{}).get('name','')
                                    flight_code=lay.get('airline',{}).get('code','')
                                    cabin=lay.get('cabinDisplay',"")
                                    flight_number=lay.get('flightNumber',"")
                                    if lay_point:
                                        lay_over_stops.append(lay_point)
                                    if lay_duration:
                                        lay_over_stop_duration.append(lay_duration)
                                    if flight_name:
                                        out_carrier_flight_name.append(flight_name)
                                    if flight_code:
                                        out_carrier_flight_code.append(flight_code)
                                    if flight_number:
                                        out_carrier_flight_number.append(flight_number)
                                    if cabin:
                                        rate_cabin.append(cabin)

                                out_carrier_name_code=[]
                                for i in range(len(out_carrier_flight_code)):
                                    out_carrier_name_code.append(f"{out_carrier_flight_code[i]}-{out_carrier_flight_number[i]}")
                                out_carrier=','.join(out_carrier_flight_name)
                                out_flight_number=','.join(out_carrier_name_code)
                                new_lay_over=[self.regex_parse(r'Change\s*planes\s*in\s*(.*?)\s*\(', x) for x in lay_over_stops]
                                out_travel_stop_over=','.join(new_lay_over)
                                out_stop_over = []
                                if new_lay_over:
                                    for i in range(len(new_lay_over)):
                                        out_stop_over.append(f"{lay_over_stop_duration[i]} stopover {new_lay_over[i]}")
                                else:
                                    out_stop_over.append([])
                                outnew_travel_stop_over=','.join(out_stop_over)
                                if lay_over_stop_duration:
                                    old_out_travel_stop_duration=[]
                                    for dur_min in lay_over_stop_duration:
                                        numeric_values = re.findall(r'\d+', dur_min)
                                        out_hours = int(numeric_values[0])
                                        out_minutes = int(numeric_values[1])  
                                        travel_stop_duration = out_hours * 60 + out_minutes
                                        old_out_travel_stop_duration.append(travel_stop_duration)
                                else:
                                    old_out_travel_stop_duration=[]
                                out_travel_stop_duration=sum(old_out_travel_stop_duration)
                                out_cabin_class = ','.join(list(set(rate_cabin)))
                                out_arrival_time = second_segment.get('arrival', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                
                        
                        second_leg = legs[1]
                        in_trip_duration_minutes=second_leg.get("legDurationMinutes","")
                        segments = second_leg.get('segments', [])
                        if len(segments)==1:
                            second_segment = segments[0]
                            airline = second_segment.get('airline')
                            if airline:
                                in_carrier = airline.get('name', "")
                                in_flight_code = airline.get('code', "")
                                in_flight_no = second_segment.get('flightNumber', "")
                                in_flight_number=f'{in_flight_code}-{in_flight_no}'
                                in_departure_time = second_segment.get('departure', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                in_arrival_time = second_segment.get('arrival', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                old_in_travel_stop_over = second_segment.get('layover', {}).get('message', "")
                                in_travel_stop_over=self.regex_parse(r'Change\s*planes\s*in\s*(.*?)\s*\(', old_in_travel_stop_over)
                                old_in_travel_stop_duration = second_segment.get('layover', {}).get('duration', "")
                                if in_travel_stop_over:
                                    innew_travel_stop_over=old_in_travel_stop_duration+' stopover '+old_in_travel_stop_duration
                                else:
                                    innew_travel_stop_over=''
                                if old_in_travel_stop_duration:
                                    numeric_values = re.findall(r'\d+', old_in_travel_stop_duration)
                                    out_hours = int(numeric_values[0])
                                    out_minutes = int(numeric_values[1])  
                                    in_travel_stop_duration = out_hours * 60 + out_minutes
                                else:
                                    in_travel_stop_duration=''
                                in_cabin_class = second_segment.get('cabinDisplay', "")

                        elif len(segments)>1:
                            lay_over=segments
                            first_segment=segments[0]
                            second_segment=segments[-1]
                            airline1 = first_segment.get('airline')
                            airline2 = second_segment.get('airline')
                            
                            if airline1:
                                in_departure_time = first_segment.get('departure', {}).get('isoDateTimeLocal', "").replace('T', ' ')
                                in_carrier_flight_name=[]
                                in_carrier_flight_code=[]
                                in_carrier_flight_number=[]
                                lay_over_stops=[]
                                lay_over_duration=[]
                                rate_cabin=[]
                                for lay in lay_over:
                                    lay_point=lay.get('layover',{}).get('message', '')
                                    lay_duration=lay.get('layover',{}).get('duration','')
                                    flight_name=lay.get('airline',{}).get('name','')
                                    flight_code=lay.get('airline',{}).get('code','')
                                    flight_number=lay.get('flightNumber',"")
                                    cabin=lay.get('cabinDisplay',"")
                                    if lay_point:
                                        lay_over_stops.append(lay_point)
                                    if lay_duration:
                                        lay_over_duration.append(lay_duration)
                                    if flight_name:
                                        in_carrier_flight_name.append(flight_name)
                                    if flight_code:
                                        in_carrier_flight_code.append(flight_code)
                                    if flight_number:
                                        in_carrier_flight_number.append(flight_number)
                                    if cabin:
                                        rate_cabin.append(cabin)
                                in_carrier_flight_name_code=[]
                                for i in range(len(in_carrier_flight_code)):
                                    in_carrier_flight_name_code.append(f"{in_carrier_flight_code[i]}-{in_carrier_flight_number[i]}")
                                in_carrier=','.join(in_carrier_flight_name)
                                in_flight_number=','.join(in_carrier_flight_name_code)
                                new_lay_over=[self.regex_parse(r'Change\s*planes\s*in\s*(.*?)\s*\(', x) for x in lay_over_stops]
                                in_travel_stop_over=','.join(new_lay_over)
                                in_stop_over = []
                                if new_lay_over:
                                    for i in range(len(new_lay_over)):
                                        in_stop_over.append(f"{lay_over_duration[i]} stopover {new_lay_over[i]}")
                                else:
                                    in_stop_over=[]
                                innew_travel_stop_over=','.join(in_stop_over)
                                if lay_over_duration:
                                    old_out_travel_stop_duration=[]
                                    for dur_min in lay_over_duration:
                                        numeric_values = re.findall(r'\d+', dur_min)
                                        out_hours = int(numeric_values[0])
                                        out_minutes = int(numeric_values[1])  
                                        travel_stop_duration = out_hours * 60 + out_minutes
                                        old_out_travel_stop_duration.append(travel_stop_duration)
                                else:
                                    old_out_travel_stop_duration=[]
                                in_travel_stop_duration=sum(old_out_travel_stop_duration)
                                in_cabin_class = ','.join(list(set(rate_cabin)))
                                in_arrival_time = second_segment.get('arrival', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                
                        options_by_fare = flight_json.get('optionsByFare', [{}])

                        if options_by_fare:
                            options = options_by_fare[0].get('options', [{}])
                            out_option = options[0]
                            net_price = net_price = out_option.get('fees', {}).get("totalPrice", "").replace('\xa0', '').replace('\u20b9', '').replace(',','').replace('.','').replace("u20B9u00A0","").replace("u00A0u20AB","")
                            out_net_price = float(re.sub(r'[^\d.,]+', '', net_price))
                            shown_price = out_option.get('displayPrice', "").replace('\xa0', '').replace('\u20b9', '').replace(',','').replace('.','').replace("u20B9u00A0","").replace("u00A0u20AB","")
                            out_shown_price = float(re.sub(r'[^\d.,]+', '', shown_price))
                            out_currency = out_option.get('providerInfo', {}).get('currency', "")
                            in_net_price = out_net_price
                            in_shown_price = out_shown_price
                            in_currency = out_currency
                            out_rate_name = out_option.get('fees', {}).get("rawPrice", "")
                            in_rate_name = out_rate_name
                        
                            outbound_flight={"arrival_time":out_arrival_time, "carrier":out_carrier, "currency":out_currency, "departure_time":out_departure_time, "flight_number":out_flight_number,"rate_name":out_cabin_class, "shown_price":out_shown_price, "total_price":out_net_price, "travel_stop_over":outnew_travel_stop_over, "trip_duration_minutes":out_trip_duration_minutes, "travel_stop_over_place":out_travel_stop_over,"travel_stop_over_minutes":out_travel_stop_duration}
                            inbound_flight={"arrival_time":in_arrival_time, "carrier":in_carrier, "currency":in_currency, "departure_time":in_departure_time, "flight_number":in_flight_number, "rate_name":in_cabin_class,"shown_price":in_shown_price, "total_price":in_net_price, "travel_stop_over":innew_travel_stop_over, "trip_duration_minutes":in_trip_duration_minutes, "travel_stop_over_place":in_travel_stop_over,"travel_stop_over_minutes":in_travel_stop_duration}
                            flight_details={"inbound_flight":inbound_flight, "outbound_flight":outbound_flight, "url":self.url, "rank":"", "snapshot_url":filename}    
                            all_item_details.append(flight_details)
                    elif len(legs)==1:    
                        first_leg = legs[0]
                        out_trip_duration_minutes=first_leg.get("legDurationMinutes","")
                        segments = first_leg.get('segments', [])
                        if len(segments)==1:
                            first_segment = segments[0]
                            airline = first_segment.get('airline',"")
                            if airline:
                                out_carrier = airline.get('name', "")
                                out_flight_code=airline.get('code', "")
                                out_flight_no = first_segment.get('flightNumber', "")
                                out_flight_number=f'{out_flight_code}-{out_flight_no}'
                                out_departure_time = first_segment.get('departure', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                out_arrival_time = first_segment.get('arrival', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                old_out_travel_stop_over = first_segment.get('layover', {}).get('message', "")
                                out_travel_stop_over=self.regex_parse(r'Change\s*planes\s*in\s*(.*?)\s*\(', old_out_travel_stop_over)
                                old_out_travel_stop_duration = first_segment.get('layover', {}).get('duration', "")
                                if out_travel_stop_over:
                                    outnew_travel_stop_over=old_out_travel_stop_duration+' stopover '+old_out_travel_stop_duration
                                else:
                                    outnew_travel_stop_over=''
                                if old_out_travel_stop_duration:
                                    numeric_values = re.findall(r'\d+', old_out_travel_stop_duration)
                                    
                                    out_hours = int(numeric_values[0])
                                    out_minutes = int(numeric_values[1])  
                                    out_travel_stop_duration = out_hours * 60 + out_minutes
                                else:
                                    out_travel_stop_duration=''
                                out_cabin_class = first_segment.get('cabinDisplay', "")
                        elif len(segments)>1:
                            lay_over=segments
                            first_segment=segments[0]
                            second_segment=segments[-1]
                            airline1 = first_segment.get('airline','')
                            airline2 = second_segment.get('airline','')
                            if airline1 and airline2:
                                out_departure_time = first_segment.get('departure', {}).get('isoDateTimeLocal', "").replace('T',' ')
                                out_carrier_flight_name=[]
                                out_carrier_flight_code=[]
                                out_carrier_flight_number=[]
                                lay_over_stops=[]
                                lay_over_stop_duration=[]
                                rate_cabin=[]
                                for lay in lay_over:
                                    lay_point=lay.get('layover',{}).get('message', '')
                                    lay_duration=lay.get('layover',{}).get('duration','')
                                    flight_name=lay.get('airline',{}).get('name','')
                                    flight_code=lay.get('airline',{}).get('code','')
                                    cabin=lay.get('cabinDisplay',"")
                                    flight_number=lay.get('flightNumber',"")
                                    if lay_point:
                                        lay_over_stops.append(lay_point)
                                    if lay_duration:
                                        lay_over_stop_duration.append(lay_duration)
                                    if flight_name:
                                        out_carrier_flight_name.append(flight_name)
                                    if flight_code:
                                        out_carrier_flight_code.append(flight_code)
                                    if flight_number:
                                        out_carrier_flight_number.append(flight_number)
                                    if cabin:
                                        rate_cabin.append(cabin)

                                out_carrier_name_code=[]
                                for i in range(len(out_carrier_flight_code)):
                                    out_carrier_name_code.append(f"{out_carrier_flight_code[i]}-{out_carrier_flight_number[i]}")
                                out_carrier=','.join(out_carrier_flight_name)
                                out_flight_number=','.join(out_carrier_name_code)
                                new_lay_over=[self.regex_parse(r'Change\s*planes\s*in\s*(.*?)\s*\(', x) for x in lay_over_stops]
                                out_travel_stop_over=','.join(new_lay_over)
                                out_stop_over = []
                                if new_lay_over:
                                    for i in range(len(new_lay_over)):
                                        out_stop_over.append(f"{lay_over_stop_duration[i]} stopover {new_lay_over[i]}")
                                else:
                                    out_stop_over.append([])
                                outnew_travel_stop_over=','.join(out_stop_over)
                                if lay_over_stop_duration:
                                    old_out_travel_stop_duration=[]
                                    for dur_min in lay_over_stop_duration:
                                        numeric_values = re.findall(r'\d+', dur_min)
                                        out_hours = int(numeric_values[0])
                                        out_minutes = int(numeric_values[1])  
                                        travel_stop_duration = out_hours * 60 + out_minutes
                                        old_out_travel_stop_duration.append(travel_stop_duration)
                                else:
                                    old_out_travel_stop_duration=[]
                                out_travel_stop_duration=sum(old_out_travel_stop_duration)
                                out_cabin_class = ','.join(list(set(rate_cabin)))
                                out_arrival_time = second_segment.get('arrival', {}).get('isoDateTimeLocal', "").replace('T',' ')
     
                        options_by_fare = flight_json.get('optionsByFare', [{}])

                        if options_by_fare:
                            options = options_by_fare[0].get('options', [{}])

                            
                            out_option = options[0]
                            net_price = net_price = out_option.get('fees', {}).get("totalPrice", "").replace('\xa0', '').replace('\u20b9', '').replace(',','').replace('.','').replace("u20B9u00A0","").replace("u00A0u20AB","")
                            out_net_price = float(re.sub(r'[^\d.,]+', '', net_price))
                            shown_price = out_option.get('displayPrice', "").replace('\xa0', '').replace('\u20b9', '').replace(',','').replace('.','').replace("u20B9u00A0","").replace("u00A0u20AB","")
                            out_shown_price = float(re.sub(r'[^\d.,]+', '', shown_price))
                            out_currency = out_option.get('providerInfo', {}).get('currency', "")
                            in_net_price = out_net_price
                            in_shown_price = out_shown_price
                            in_currency = out_currency
                            out_rate_name = out_option.get('fees', {}).get("rawPrice", "")
                            in_rate_name = out_rate_name

                        outbound_flight={"arrival_time":out_arrival_time, "carrier":out_carrier, "currency":out_currency, "departure_time":out_departure_time, "flight_number":out_flight_number,"rate_name":out_cabin_class, "shown_price":out_shown_price, "total_price":out_net_price, "travel_stop_over":outnew_travel_stop_over, "trip_duration_minutes":out_trip_duration_minutes, "travel_stop_over_place":out_travel_stop_over,"travel_stop_over_minutes":out_travel_stop_duration}
                        flight_details={"outbound_flight":outbound_flight, "url":self.url, "rank":"", "snapshot_url":filename}

                        all_item_details.append(flight_details)
            
            return all_item_details
        else:
            if self.retry_count < 5:
                logger.info(f"retry_count-------->{self.retry_count}")
                self.retry_count+=1
                retry_response=self.post_response(pollnumber)
                if retry_response==False:
                    return None
                retry_result=self.parse_flight_detail(retry_response,pollnumber)
                return retry_result
            
            elif self.retry_count==5:
                if pollnumber == 0:
                    logger.info("<------------retry on puppeteer---------->")
                    logger.info(f"retry_count-------->{self.retry_count}")
                    self.retry_count+=1
                    puppetter_response=puppetter(self.url, logger)
                    if puppetter_response==False:
                        return None
                    else:
                        puppetter_result=self.parse_flight_detail(puppetter_response,pollnumber)
                        return puppetter_result
               
            # elif self.retry_count==5:
            #     if pollnumber == 0:
            #         logger.info("<------------retry on selenium---------->")
            #         logger.info(f"retry_count-------->{self.retry_count}")
            #         self.retry_count+=1
            #         selenium_response=selenium_function(self.url, logger)
            #         if selenium_response==False:
            #             # return ["puppetter failure"]
            #             # return None
            #             pass
            #         else:
            #             selenium_result=self.parse_flight_detail(selenium_response,pollnumber)
            #             return selenium_result

            else:
                logger.info("<------------6 times retry exists---------->")
                return None
            
    def save_to_json(self, data, filename):
        """ result save in json file """
        with open(filename, 'a') as file: 
            json.dump(data, file, indent=4)
        logger.info("<-----------------json written successfully----------------->")