from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import twstock
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
from datetime import datetime
import pytz
import requests 
from bs4 import BeautifulSoup
import time
from lxml import etree 
from multiprocessing import Process, Pool
import multiprocessing
import asyncio
import pprint
# 參考 twstock 取得需要的 URL
SESSION_URL = 'http://mis.twse.com.tw/stock/index.jsp'
STOCKINFO_URL = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={stock_id}&_={time}'


# def get_realtime_price(stockNo, ex='tse'):
    
#     req = requests.Session()
#     req.get(SESSION_URL)
    
#     stock_id = '{}_{}.tw'.format(ex, stockNo)
#     r = req.get(STOCKINFO_URL.format(stock_id=stock_id, time=int(time.time()) * 1000))
#     try:
#         return r.json()['msgArray'][0]['z']
#     except json.decoder.JSONDecodeError:
#         return {'rtmessage': 'json decode error', 'rtcode': '5000'}
# def get_stocks_realtime_price(numberList): 
#     data = { "stock_realtime_price": { }}
#     print(numberList.stock_list)
#     for stock_number in numberList.stock_list:
#         try:
#             data["stock_realtime_price"][stock_number] = get_realtime_price(stock_number)
#         except:
#             print("Connection refused by the server..")
#             print("Let me sleep for 5 seconds")
#             print("ZZzzzz...")
#             print("Was a nice sleep, now let me continue...")

    # with open('stock_realtime_price.json', 'w') as f:
    #     json.dump(data, f)
    # print(data["stock_realtime_price"]["0056"], 333)
    # return data
  

key = os.getenv("FAKE_VALUE")
app = FastAPI()

origins = [
    "http://localhost:3001", # test url
    "http://localhost:3000", # test url
    "https://web-api-test.onrender.com",
    "https://garytsai.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Stock(BaseModel):
    stock_list: list

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/realtime_price/")
async def stock_price(numberList: Stock):
    # tw = pytz.timezone('Asia/Taipei')
    # now_utc = datetime.now(tw)
    # date = datetime.now().date()
    # currentDateTime = datetime(now_utc.year, now_utc.month, now_utc.day, now_utc.hour, now_utc.minute)

    # stock_end_time = datetime(date.year, date.month, date.day, 13, 30)
    # data = {}
    # for stock_number in numberList.stock_list:
    #     if((stock_number in twstock.codes) == True):
    #         if(currentDateTime < stock_end_time):
    #             data[stock_number] = twstock.realtime.get(stock_number)['realtime']['best_ask_price'][0]
    #         else: 
    #             data[stock_number] = twstock.realtime.get(stock_number)['realtime']['latest_trade_price']
    # ----------------------------------------------------------------------------------------------------
    # data = {}
    # print(numberList)
    # for stock_number in numberList.stock_list:
    #     url = "https://tw.stock.yahoo.com/quote/{}.TW".format(stock_number)
    #     res = requests.get(url) 
    #     Soup = BeautifulSoup(res.text,'html.parser')
    #     soup = Soup.find("span", string="成交") 
    #     price = soup.find_next_siblings("span")
    #     data[stock_number] = price[0].get_text().strip()
    # -----------------------------------------------------------------------------------------------------

    data = {}
    price_offset = {}
    def crawl(stock_number):
        url = "https://tw.stock.yahoo.com/quote/{}.TW".format(stock_number)
        res = requests.get(url)
        Soup = BeautifulSoup(res.text, 'lxml')
        soup = Soup.find("span", string="成交")
        price = soup.find_next_siblings("span")
        soup = Soup.find("span", string="昨收")
        pre_offset = soup.find_next_siblings("span")

        data[stock_number] = price[0].get_text().strip()
        price_offset[stock_number] = round( float(price[0].get_text().strip()) - float(pre_offset[0].get_text().strip()), 2)
        

    loop = asyncio.get_event_loop()
    start = time.time()
    for stock_number in numberList.stock_list:
       await loop.run_in_executor(None, crawl, stock_number)
    end = time.time()
    print('time',end - start)
    return [data, price_offset]

@app.post("/dividend/")
async def read_dividend(numberList: Stock):
    webHtml = []
    data = []
    sockInfos = []
    final_sockInfos = []
    perSockInfo = {}

    def crawl(stock_number):
        data.clear()
        webHtml.clear()
        perSockInfo.clear()

        url = "https://www.cmoney.tw/forum/stock/{}?s=dividend".format(stock_number)
        res = requests.get(url)
        Soup = BeautifulSoup(res.text, 'lxml')
        for item in Soup.find_all("tr"):
            webHtml.append(item.text)

        for item in webHtml[2].split():
            if webHtml[2].split().index(item) < 6:
                data.append(item)
        # 00929 月配        
        if '00929' in stock_number:
            for item in webHtml[3].split():
                if webHtml[3].split().index(item) < 5:
                    data.append(item)
        if '00929' in stock_number:
            print(data)
            perSockInfo['stock_number'] = stock_number       
            perSockInfo['timePeriod'] = data[0]
            perSockInfo['dividend'] = data[2]
            perSockInfo['ex-dividend-date'] = data[3]
            perSockInfo['distributeDividend-date'] = data[4]
            perSockInfo['dividend_second'] = data[10]
            perSockInfo['ex-dividend-date_second'] = data[11]
            perSockInfo['distributeDividend-date_second'] = data[12]
            print(perSockInfo)
        if '00' in stock_number:
            perSockInfo['stock_number'] = stock_number       
            perSockInfo['timePeriod'] = data[0]
            perSockInfo['dividend'] = data[2]
            perSockInfo['ex-dividend-date'] = data[3]
            perSockInfo['distributeDividend-date'] = data[4]
        else :
            perSockInfo['stock_number'] = stock_number       
            perSockInfo['timePeriod'] = data[0]
            perSockInfo['dividend'] = data[1]
            perSockInfo['ex-dividend-date'] = data[2]
            perSockInfo['distributeDividend-date'] = data[3]

        temp = perSockInfo.copy()
        sockInfos.append(temp)
    # test stock list
    # numberList = {
    #     "stock_list":["00929", "3260", "2303", "9958", "00919", "8299", "6147", "4549", "3034", "3231", "00878", "2337", "3481", "00927", "1101","0056"]
    #     }
    loop = asyncio.get_event_loop()
    start = time.time()
    for stock_number in numberList.stock_list:
       await loop.run_in_executor(None, crawl, stock_number)
    end = time.time()
    print('time',end - start)
    print(str(datetime.now().year - 1))
    for stock in sockInfos: 
        if datetime.today().strftime("%Y") in stock['timePeriod'] or (str(datetime.now().year - 1)) in stock['timePeriod']:
            if datetime.today().strftime("%Y/%m") in stock['distributeDividend-date']:
                final_sockInfos.append(stock)
            if '00929' in stock['stock_number'] and datetime.today().strftime("%Y/%m") in stock['distributeDividend-date_second']:
                final_sockInfos.append(stock)

    return [ final_sockInfos ]