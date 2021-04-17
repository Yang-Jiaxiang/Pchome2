import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
from datetime import datetime
import sys

wab = input('請輸入想要爬蟲的商品:')
print("======================================")
headers = {'cookie': 'ECC=GoogleBot',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}

query = wab
# 每次加載分頁有20筆資料，可以依需求增加/減少
pages = int (input('請輸入想要爬蟲商品的頁數:'))
print("======================================")

FileName = input('請輸入檔案名稱:')
FFileName='./'+FileName+'.xlsx'
print("======================================")

# get prods list
prodids = []
for page in list(range(1, pages)):
    url = 'https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={}&page={}&sort=sale/dc'.format(query, page)
    resp = requests.get(url,headers=headers)
    for prodid in resp.json()["prods"]:
        prodids.append(prodid['Id'])
    prodids = list(set(prodids))
    print('There are {} products in list.'.format(len(prodids)))

# ecapi
df1 = []
for i, Id in enumerate(prodids):
    columns, values = [], []
    print('Dealing with {}: {}'.format(i, Id))
    sleep(0.7)
    ecapi = 'https://mall.pchome.com.tw/ecapi/ecshop/prodapi/v2/prod/{}&fields=Seq,Id,Stmt,Slogan,Name,Nick,Store,PreOrdDate,SpeOrdDate,Price,Discount,Pic,Weight,ISBN,Qty,Bonus,isBig,isSpec,isCombine,isDiy,isRecyclable,isCarrier,isMedical,isBigCart,isSnapUp,isDescAndIntroSync,isFoodContents,isHuge,isEnergySubsidy,isPrimeOnly,isWarranty,isLegalStore,isOnSale,isPriceTask,isBidding,isETicket&_callback=jsonp_prod&1587196620'.format(Id)
    resp = requests.get(ecapi, headers=headers)
    data = re.sub('try{jsonp_prod\(|\}\);\}catch\(e\)\{if\(window.console\)\{console.log\(e\)\;\}','',resp.text)
    data = json.loads(data)[Id+'-000']

    for key, value in data.items():
        columns.append(key)
        values.append(value)
    ndf = pd.DataFrame(data=values, index=columns).T
    df1.append(ndf)
df1 = pd.concat(df1, ignore_index=True)


# cdn
df2 = []
for i, Id in enumerate(prodids):
    columns, values = [], []
    print('Dealing with {}: {}'.format(i, Id))
    sleep(0.7)
    cdn = 'https://ecapi.pchome.com.tw/cdn/ecshop/prodapi/v2/prod/{}/desc&fields=Id,Stmt,Equip,Remark,Liability,Kword,Slogan,Author,Transman,Pubunit,Pubdate,Approve&_callback=jsonp_desc'.format(Id+'-000')
    resp = requests.get(cdn, headers=headers)
    data = re.sub('try\{jsonp_desc\(|\}\);\}catch\(e\)\{if\(window.console\)\{console.log\(e\)\;\}','',resp.text)
    data = json.loads(data)
    data = data[Id]

    for key, value in data.items():
        columns.append(key)
        values.append(value)
    ndf = pd.DataFrame(data=values, index=columns).T
    df2.append(ndf)

df2 = pd.concat(df2, ignore_index=True)


df1['Id'] = df1['Id'].apply(lambda x: re.sub('-000$','',x))
df = pd.merge(df1, df2, how='left',on='Id')
df.info()

df.to_excel(FFileName)
df
