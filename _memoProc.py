#!/usr/bin/env python
# coding: utf-8
# ## 所有函數擺放在這!!

import pandas as pd
import numpy as np
import datetime
from finlab.data import Data
from datetime import date,timedelta
import math
from talib import abstract
import _beowSet as bs          #自己寫的

data = Data()
price = pd.read_pickle("history/tables/bargin_report.pkl")
pp = price.tail(1)
pp = pp.index.levels[0]
df = data.get("收盤價")


def getStockName(n):
    for p in pp:
        if n in p:
            arr = p.split(" ")
            return arr[1]


#判斷是否禮拜天? 如果是自動跳到上周五....但有國定假日就不行了。
def whatIsToday(diff_days, iYesterday):
    #參數 day: 距離今天多少天起
    today = date.today() - timedelta(days= diff_days)
    yesterday = date.today() - timedelta(days= diff_days + iYesterday)
    
    #如果是周日，再往前推兩天...未來如果有國定家日 可以另外再寫出來。
    if(yesterday.weekday()==6):
        yesterday = yesterday-timedelta(days=2)
        
    if(str(yesterday)=="2020-01-01"):
        yesterday = yesterday-timedelta(days=1)
    return str(today), str(yesterday), date.today().weekday()

        
def getMA_infor(today, yesterday, maRoll, days):
    fore = 0                        #前半段
    back = 0                        #後半段
    ratio = 0                       #曲率
    dscr =""                        #均線描述
    sep = 3
    i=1
    
    for c in reversed(maRoll):
        if(i<=sep):
            fore += c
        elif (i <= sep*2 and i >= sep):
            back += c
        i+=1
        
    td1= 1 if (math.isnan(maRoll[today])) else maRoll[today]
    td2= maRoll[yesterday]
    td_diff = td1 - td2
    td_slope = round((td1 - td2)/td2*100 ,2)
        
    diff = round(fore - back, 2)
    ratio = round(diff / back * 100, 2)
    
    dscr += bs.DisplayNameMA(days)
    
    if(abs(ratio) <= 0.04):                 #長均區間
        dscr += "－," + str(ratio)
    else:
        if(td_diff>0):
            dscr += "↗," + str(td_slope)+""
        if(td_diff<0):
            dscr += "↘," + str(td_slope)+""
        
    if(dscr=="季"):
        dscr="季?,"
    if(dscr=="年"):
        dscr="年?,"
        
    # print(days,today,yesterday,round(fore,4),round(back,4),ratio) #,td1,td2,td_diff)        
    
    return round(td1,2), dscr , td_diff


def diffRatio(w1,m1,q1,y1 ,wd,md,qd,yd, wr,mr,qr,yr):
    #精準描述均線的排列---------
    wmqy_dscr = wd+","+md+","+qd+","+yd          #不按照大小排列
    wmqy_dscr2 = ""                              #有按照大小排列
    dic = { wd : w1, md : m1, qd : q1, yd: y1 }  #以dict作為排列的工具
    dic2 = {k: v for k, v in sorted( dic.items(), key=lambda item: item[1], reverse = True )}
    for k in dic2.keys():
        wmqy_dscr2 += k + ","
    
    return wmqy_dscr, wmqy_dscr2


def isFlatMA(today, yesterday, stockId, close):
#     close = data.get("收盤價")[stockId]

    ma1 = close[-700 :]                   #ma1  收盤價
    #ma05r  = ma1.rolling(5).mean()     #ma5   週均線
    #ma20r  = ma1.rolling(20).mean()     #ma20  月均線
    #ma60r  = ma1.rolling(60).mean()     #ma60  季均線
    #ma240r = ma1.rolling(240).mean()   #ma240 年均線
    
    #自2021-02-16開始全面使用EMA指數均線
    ma05r = ma1.ewm(span=5, adjust=False).mean()
    ma07r = ma1.ewm(span=7, adjust=False).mean()
    ma10r = ma1.ewm(span=10, adjust=False).mean()
    ma20r = ma1.ewm(span=20, adjust=False).mean()
    ma60r = ma1.ewm(span=60, adjust=False).mean()
    ma240r = ma1.ewm(span=240, adjust=False).mean()
    
    # print("isFlatMA by 5",today, yesterday, ma05r,5)

    wv, wd, wr = getMA_infor(today, yesterday, ma05r,5)
    ev, ed, er = getMA_infor(today, yesterday, ma07r,7)
    fv, fd, fr = getMA_infor(today, yesterday, ma10r,10)
    mv, md, mr = getMA_infor(today, yesterday, ma20r,20)
    qv, qd, qr = getMA_infor(today, yesterday, ma60r,60)
    yv, yd, yr = getMA_infor(today, yesterday, ma240r,240)
    
    if(math.isnan(mv)):
        dscr, dscr2 = "序列不連續無法計算","?","?","?"
    else:
        dscr, dscr2 = diffRatio(wv,mv,qv,yv,    wd,md,qd,yd,    wr,mr,qr,yr)
        # print(diffRatio(wv,mv,qv,yv,    wd,md,qd,yd,    wr,mr,qr,yr))
    
    return wv, ev, fv, mv, qv, yv, dscr2 

#僅丟入收盤價(close)、成交量(volumns) 就能夠計算次箱位置
def getCriticalBox(today, yesterday,datediff,stockId,day,closes,volumns):
    #volumns = data.get("成交股數")[stockId]
    #closes = data.get("收盤價")[stockId]
    _day=0
    ori_today, yesterday, whatDay = whatIsToday(datediff , 1)   # 這邊如果沒有回溯 ，要改為跟datediff相同!!
    mmd1 = volumns.index.get_loc(today)
    mmd2 = volumns.index.get_loc(ori_today)
    _datediff = mmd1 - mmd2                              # 因為周休沒有交易 所以要計算實際交易的天數。
        
    if(day == -20):
        _datediff = -1 if (_datediff == 0) else _datediff
        _day = _datediff + day
        m_prd_stocks = volumns[ _day : _datediff]
        
    if(day == -60):
        _day = _datediff + day
        m_prd_stocks = volumns[ _day : _datediff - 40]
        
    if(day == -240):
        _day = _datediff + day - 60
        m_prd_stocks = volumns[ _day : _datediff - 180]
    
    vmax = m_prd_stocks[volumns == m_prd_stocks.max()]   #關鍵在哪一天? 量最大!!?
    vmin = m_prd_stocks[volumns == m_prd_stocks.min()]   #關鍵在哪一天? 量最大!!?
    
#     print(stockId, day, vmax, vmin)
    
    if (vmax.empty == True):
        vmax_str = "error date"
        boxV = 1
    else:
        vmax_str = vmax.index[0].strftime("%Y-%m-%d")
        boxV = closes[vmax.index][0]    
        
    if (vmin.empty == True):
        vmin_str = "error date"
        boxV2 = 1
    else:
        vmin_str = vmin.index[0].strftime("%Y-%m-%d")
        boxV2 = closes[vmin.index][0]
    
    return  vmax_str, boxV, vmin_str, boxV2


## 抓出真正一個月內的最高點、一季內的最高點、一年內的最高點。
def getTopBoxByClose(today, yesterday, datediff, stockId, day, closes, volumns):
    #volumns = data.get("成交股數")[stockId]
    #closes = data.get("收盤價")[stockId]
    _day=0
    ori_today, yesterday, whatDay = whatIsToday(datediff , 1)   # 這邊如果沒有回溯 ，要改為跟datediff相同!!
    mmd1 = closes.index.get_loc(today)
    mmd2 = closes.index.get_loc(ori_today)
    _datediff = mmd1 - mmd2                              # 因為周休沒有交易 所以要計算實際交易的天數。
    _datediff = -1 if (_datediff == 0) else _datediff
    
    if(day == -20):
        _day = _datediff + day
        m_prd_stocks = closes[ _day : _datediff]
        
    if(day == -60):
        _day = _datediff + day -20
        m_prd_stocks = closes[ _day : _datediff - 40]
        
    if(day == -240):
        _day = _datediff + day - 60
        m_prd_stocks = closes[ _day : _datediff - 180]   
    
    
    vmax = m_prd_stocks[closes == m_prd_stocks.max()]   #關鍵在哪一天? 量最大!!?
    vmin = m_prd_stocks[closes == m_prd_stocks.min()]   #關鍵在哪一天? 量最大!!?
    
    if (vmax.empty == True):
        vmax_str = "error date"
        boxV = 1
    else:
        vmax_str = vmax.index[0].strftime("%Y-%m-%d")
        boxV = closes[vmax.index][0]    
        
    if (vmin.empty == True):
        vmin_str = "error date"
        boxV2 = 1
    else:
        vmin_str = vmin.index[0].strftime("%Y-%m-%d")
        boxV2 = closes[vmin.index][0]
    
    return  vmax_str, boxV, vmin_str, boxV2


#確認是否共振?
def checkBoxResonance(today,yesterday,datediff,stockId,closes,volumns):    
    m, q, y = -20, -60, -240 #分別為月、季、年級數
    
#     md, mv, md2, mv2 = getCriticalBox(today,yesterday,datediff,stockId,m,closes,volumns)
#     qd, qv, qd2, qv2 = getCriticalBox(today,yesterday,datediff,stockId,q,closes,volumns)
#     yd, yv, yd2, yv2 = getCriticalBox(today,yesterday,datediff,stockId,y,closes,volumns)
    md, mv, md2, mv2 = getTopBoxByClose(today,yesterday,datediff,stockId,m,closes,volumns)
    qd, qv, qd2, qv2 = getTopBoxByClose(today,yesterday,datediff,stockId,q,closes,volumns)
    yd, yv, yd2, yv2 = getTopBoxByClose(today,yesterday,datediff,stockId,y,closes,volumns)
    
    #print(yd,yv,yd2, yv2)
    mq_r = round((mv-qv)/qv ,4)
    qy_r = round((qv-yv)/yv ,4)
    my_r = round((mv-yv)/yv ,4)
    
    i, msg = 0, ""
    sens = 0.02  #形容均線之間緊密度，這可隨狀況調整。
    
    if(abs(mq_r) < sens):
        msg+="、月季"
        i+=1
    if(abs(qy_r) < sens):
        msg+="、季年"
        i+=1
    if(abs(my_r) < sens):
        msg+="、月年"
        i+=1
        
    if(i==1 or i==2):
        msg+="關鍵點位共振"
    
    if(i==3):
        msg="月、季、年關鍵點位共振"
    
#     print("月關鍵:", md, mv, md2, mv2, "季關鍵:", qd, qv, qd2, qv2, "年關鍵:", yd, yv, yd2, yv2, msg[1:])  #檢查所有明細
    #print(abs(mq_r), abs(qy_r), abs(my_r), msg)  #檢查是否有級數共振!?
    return md, mv, md2, mv2,    qd, qv, qd2, qv2,    yd, yv, yd2, yv2,  msg[1:]


###### K棒是否壓過目標?     ##############
def isCover(active,k_begin,k_end,target):
    dscr = active
    return dscr if ((k_begin >= target and target >= k_end) or (k_end >= target and target >= k_begin) ) else "" 


def checkSimpleInfo(today,yesterday,datediff,stockId):
    o = data.get("開盤價")[stockId][today]    #open
    c = data.get("收盤價")[stockId][today]    #close
    yc = data.get("收盤價")[stockId][yesterday]    #close
    v = data.get("成交股數")[stockId][today]  #volumn
    h = data.get("最高價")[stockId][today]    #high
    l = data.get("最低價")[stockId][today]    #low
    v = 1 if( math.isnan(v) == True ) else int(v/1000)  #張數  
    kbar = "紅K" if(c>o) else "綠K"
    
    return kbar, o, yc, c, h, l, v

def talib2df(talib_output, ma1):
    if type(talib_output) == list:
        ret = pd.DataFrame(talib_output).transpose()
    else:
        ret = pd.Series(talib_output)
    ret.index = ma1.index
    return ret

    
def isCoverMA(today, yesterday,datediff, stockId):
    
    # volumn = data.get("成交股數")[stockId]
    close = data.get("收盤價")[stockId]
    high = data.get("最高價")[stockId]
    low = data.get("最低價")[stockId]
    tailNum = 30
    ma1 = close.tail(tailNum)
    kd = talib2df(abstract.STOCH(high.tail(tailNum), low.tail(tailNum), ma1, fastk_period=9), ma1) #計算KD  

    #這邊無法精準抓出某一row
    #kd.tail(2).index = pd.to_datetime(close.tail(2).index)
    # kd = pd.to_datetime(kd['date']).datetime.date
    # # .astype('datetime64[D]')
    # print("kkkd", kd.tail(2).index )
    # print(kd[pd.to_datetime(today, format='%Y%m%d', errors='ignore')])

    c = close[today]                       #今天收盤價
    o= data.get("開盤價")[stockId][today]   #今日開盤價
    h = high[today]                        #今日最高價
    l = low[today]                         #今日最低價

    kkd = kd[-1:]
    # print(kkd)
    k = round(kkd[0][today], 2)
    d = round(kkd[1][today], 2)
    
    k =  0 if (math.isnan(k)) else k
    d =  0 if (math.isnan(d)) else d
    
    # print("isCoverMA for KD", k, d, today, yesterday, stockId)
    yc = close[yesterday]                  #昨天收盤價
    yh = high[yesterday]                  #昨天最高價
    yl = low[yesterday]                  #昨天最低價
    
    ma5, ma7, ma10, ma20, ma60, ma240, ma_dscr2 = isFlatMA(today, yesterday, stockId, close)
    # print(isFlatMA(today, yesterday, stockId, close))
    
    bar = "紅K" if(c>o) else "綠K"
    amplitude = round((h-l)/c * 100,2)    
    iGap = round(l - yh ,2) #描述跳空缺口
    
    #計算扣抵值
    ddu5 = close[-5 :].head(1).values[0]
    ddu10= close[-10 :].head(1).values[0]
    ddu20= close[-20 :].head(1).values[0]
    ddu60= close[-60 :].head(1).values[0]
    ddu240 = close[-240 :].head(1).values[0]
    
    ddu5 =  0 if (math.isnan(ddu5)) else ddu5
    ddu10 = 0 if (math.isnan(ddu10)) else ddu10
    ddu20 = 0 if (math.isnan(ddu20)) else ddu20
    ddu60 = 0 if (math.isnan(ddu60)) else ddu60
    ddu240 = 0 if (math.isnan(ddu240)) else ddu240
    
#     ddu_result = "大於所有扣抵值" if (c >= ddu5 and c >= ddu10 and c >= ddu20 and c >=ddu60 and c>=ddu240) else "" 

    return bar, ma5, ma7, ma10, ma20, ma60, ma240, iGap, amplitude, ma_dscr2, ddu5, ddu10, ddu20, ddu60, ddu240, k, d
    
    
    
price = pd.read_pickle("history/tables/bargin_report.pkl")

def getStockVolumns(stockId, i):
    #變數i代表倒退幾天?
    nn = stockId+" "+ getStockName(stockId)
    i = i * -1    
    j = i - 1
    sql = ""
    
    try:
        pp = price.loc[nn][-1:] if (i==0) else price.loc[nn][j:i]
#         print(pp)
        
        dealer = int(int( pp["自營商買賣超股數(自行買賣)"] )/1000)
        dealer2 = int(int( "0" if (math.isnan( pp["自營商買賣超股數(避險)"])) else pp["自營商買賣超股數(避險)"]  )/1000)
        ic     = int(int( pp["投信買賣超股數"])/1000)
        fc     = int(int( pp["外陸資買賣超股數(不含外資自營商)"])/1000)
        
        dt     = pp.index[0].strftime("%Y-%m-%d")
        sql = "insert into volumn(stockId,closeDate,fc,ic,dealer) values ('{0}','{1}',{2},{3},{4}); "
        sql = sql.format(stockId, dt, fc, ic, dealer + dealer2)
        return sql
        
     
    except Exception as e:
        error_class = e.__class__.__name__            #取得錯誤類型
        detail = e.args[0]                            #取得詳細內容
        cl, exc, tb = sys.exc_info()                  #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1]  #取得Call Stack的最後一筆資料
        fileName , lineNum, funcName = lastCallStack[0], lastCallStack[1], lastCallStack[2]  #取得發生的檔案名稱、取得發生的行號、取得發生的函數名稱
        errMsg = "/* File \"{}\", line {}, in {}: [{}] {}  */".format(fileName, lineNum, funcName, error_class, detail)
        print(stockId, errMsg, sql) 
        return "/* Error "+ stockId + "-" + getStockName(stockId) +"*/"
    except:
        print("/* 三大法人非預期的錯誤", sys.exc_info()[0], "*/")

        


import os
from colorama import Fore,Style
import sys
import traceback
import csv
import time


def findTrendStock(today, yesterday, datediff):
    i=1
    stockName, errMsg, sql ="","",""

    for stockId in stockIds:
        
        if(stockId >= "1101" and stockId <="9962"): # 1101 ~　9962 最後一筆

            try:
                #初步先過濾簡單目標--------------------------------------------------
                kbar, o, yc, close, high, low, volumn = checkSimpleInfo(today, yesterday, datediff, stockId)
                
                if(close >= 8):                    
                    kbar, ma5, ma7, ma10, ma20, ma60, ma240, iGap, amplitude, ma_dscr2, ddu5, ddu10, ddu20, ddu60, ddu240, k,d = isCoverMA(today, yesterday, datediff, stockId)

                    i+=1
                    stockName = getStockName(stockId)
                    print (i, stockId, stockName, Fore.RED if(kbar=="紅K") else Fore.GREEN , close, "數量",k,d, Fore.YELLOW,  Style.RESET_ALL)                        
                    sql = """insert into StockParas (stockId, closeDate, v, o, c, h, l, yc,
                            ma5, ma7, ma10, ma20, ma60, ma240,
                            amplitude, ma_dscr, iGap, 
                            ddu5, ddu10, ddu20, ddu60, ddu240, k, d ) values (
                            '{0}', '{1}', {2}, {3}, {4}, {5}, {6}, {7},{8}, {9}, {10}, {11}, {12}, {13},
                            N'{14}', N'{15}', {16}, {17}, {18}, {19}, {20}, {21}, {22}, {23});"""; 
                    sql = sql.format(stockId, today, volumn, o, close, high, low, yc, ma5, ma7, ma10, ma20, ma60, ma240, amplitude, ma_dscr2, iGap, ddu5, ddu10, ddu20, ddu60, ddu240, k, d,)    
                    # print(sql)
                    bs.ExecuteMSSQL(sql)      #同時寫入兩個指令

                    # sql = """update stockparas set ma7={0},ma10={1} where closeDate='{2}' and stockId='{3}';"""
                    # sql = sql.format(ma7,ma10,today,stockId)
                    # print(sql)
                    # bs.ExecuteMSSQL(sql)


            except Exception as e:
                error_class = e.__class__.__name__ #取得錯誤類型
                detail = e.args[0] #取得詳細內容
                cl, exc, tb = sys.exc_info() #取得Call Stack
                lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
                fileName , lineNum, funcName = lastCallStack[0], lastCallStack[1], lastCallStack[2]  #取得發生的檔案名稱、取得發生的行號、取得發生的函數名稱
                errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
                print(stockId, errMsg, sql)



#####################################################################################################    


def findMonthInCome(stockId):
    df = data.get("當月營收")[stockId]
    df = df[df.notna()]         #找出不是nan的資料
    
    thisMM = df.tail(1)[0]
    lastMaxV = df[:-1].max()    #過去最高營收
    q = (df == lastMaxV)
    lastMaxDt = df[q].index[0].strftime("%Y-%m-%d")
    nowDate = df.tail(1).index[0].strftime("%Y-%m-%d")
    
#     print(df)
    return  lastMaxDt, round(lastMaxV/10000,2), nowDate, round(thisMM/10000 ,2), thisMM >= lastMaxV
            


def get_all_max_month_income():
    i=0
    for stockId in stockIds:
        if(stockId >= "1101" and stockId <="9962" ):
            try:
                lastMaxDt, lastMaxV, nowDate, nowRvn, isHistMax = findMonthInCome(stockId)
                stockName = getStockName(stockId)
                
                
                (stockId)

                if(isHistMax== True ):
                    i += 1
                    print(i, stockId, stockName, lastMaxDt, lastMaxV, nowDate, nowRvn, isHistMax)

                    sql = """
                    declare @isExist as int;
                    select @isExist = count(*) from maxMMRevenue where stockId={0} and nowDate='{2}';

                    if @isExist = 0
                    begin
                        insert into maxMMRevenue (stockId,stockName,nowDate,nowRvn,lastMaxDate,lastMaxRvn,createdDate) 
                                                values ('{0}',N'{1}','{2}',{3},'{4}',{5},getdate());  
                    end
                    """
                    sql = sql.format(stockId, stockName, nowDate, nowRvn, lastMaxDt, lastMaxV )
                    bs.InsertIntoMSSQL2017(sql)                
            except Exception as e:
                    error_class = e.__class__.__name__ #取得錯誤類型
                    detail = e.args[0] #取得詳細內容
                    cl, exc, tb = sys.exc_info() #取得Call Stack
                    lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
                    fileName , lineNum, funcName = lastCallStack[0], lastCallStack[1], lastCallStack[2]  #取得發生的檔案名稱、取得發生的行號、取得發生的函數名稱
                    errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
                    print(stockName, errMsg)
    
#-------------------------------------------------

_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
datediff, iYesterday, stockIds, vsql, i = 0 , 1, [], "", 0    #datediff =回推第幾天?
stockIds = bs.getAllStockIds(pp, False)
today, yesterday, whatDay = whatIsToday(datediff, iYesterday)   #今天是什麼日期? 前天交易日?
print("today:", today,"yesterday:", yesterday, whatDay, "開始", _start)


findTrendStock(today, yesterday, datediff)

j=0
for stockId in stockIds:
    if(stockId >= "1101" and stockId <="9962" ):
        i+=1
        if(j < 50):
            vsql += getStockVolumns(stockId, 0)
            j += 1
            print(i, stockId)
        else:
            bs.InsertIntoMSSQL2017(vsql)                #一次輸入給SQL新增。更快!! 但是送到遠端SQL會有遺漏?
            j = 0
            vsql = ""



get_all_max_month_income()

print("today:", today,"yesterday:", yesterday, whatDay)
print("開始", _start)
print("結束", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

bs.proc_final_SqlScript(today)

# %%
