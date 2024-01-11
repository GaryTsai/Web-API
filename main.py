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
    "https://web-api-test.onrender.com"
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
    data = {}
    print(numberList)
    for stock_number in numberList.stock_list:
        url = "https://tw.stock.yahoo.com/quote/{}.TW".format(stock_number)
        res = requests.get(url) 
        Soup = BeautifulSoup(res.text,'html.parser')
        soup = Soup.find("span", string="成交") 
        price = soup.find_next_siblings("span")
        data[stock_number] = price[0].get_text().strip()
    return data
