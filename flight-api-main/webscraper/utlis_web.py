import requests
import sys
import os
from dotenv import load_dotenv
from pathlib import Path
import urllib.parse
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

try:
    load_dotenv()
except:
    env_path = Path(".env")
    load_dotenv(dotenv_path=env_path)

puppetter_url=os.getenv("puppetter_url")

def get_request(url,headers,proxy,logger,proxy_retry_count=1):
    """ get the url return the page response using requests module"""
    try:
        response=requests.get(url,headers=headers,proxies=proxy,stream=True)
        return response 
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        if proxy_retry_count < 4:
            logger.info(f"get_request_proxy_retry_count-------->{proxy_retry_count}")
            proxy_retry_count+=1
            get_request(url,headers,proxy,logger,proxy_retry_count=proxy_retry_count)
        else:
            logger.error(f"get_request_proxy_retry_count--------->{exc_type, fname, exc_tb.tb_lineno}")
            return False

def post_request(post_url,headers,payload,proxy,logger,proxy_retry_count=1):
    """ get the url return the page response using requests module"""
    try:
        pages_response = requests.post(post_url, headers=headers, data=payload, proxies=proxy, stream=True)
        return pages_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        if proxy_retry_count < 4:
            logger.info(f"post_request_proxy_retry_count-------->{proxy_retry_count}")
            proxy_retry_count+=1
            post_request(post_url,headers,payload,proxy,logger,proxy_retry_count=proxy_retry_count)
        else:
            logger.error(f"post_request_proxy_retry_count--------->{exc_type, fname, exc_tb.tb_lineno}")
            return False
        
def puppetter(url,logger):
    """ get the url return the page response using puppetter """
    try:
        logger.info("<--------------puppetter_function-------------->")
        browser_url=puppetter_url+urllib.parse.quote(url).replace("/","%2F")
        logger.info(f"puppetter_url----------->{browser_url}")
        puppetter_response=requests.get(browser_url)
        if puppetter_response.text=="check the url":
            logger.error("puppetter_error----------->check the given url in puppetter")
            return False
        else:
            return puppetter_response
    except Exception as e:
        logger.error(f"puppetter_error----------->{e}")
        return False

def selenium_function(url,logger):
    try:
        driver = webdriver.Chrome(executable_path="/home/hemesh/Projects/live_projects/fastapi_project/chromedriver")  # This will open the Chrome window
        sleep(2)
        driver.get(url)
        wait = WebDriverWait(driver, 60).until(lambda driver: driver.find_element(By.CSS_SELECTOR, 'div.col-advice > div[aria-busy]').get_attribute("aria-busy") == "false")
        response = driver.page_source
        driver.quit()
        return response
    except Exception as e:
        logger.error(f"selenium_error----------->{e}")
        return False
