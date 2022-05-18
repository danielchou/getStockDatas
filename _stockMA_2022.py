# %%
import pandas as pd
import numpy as np
import datetime
from finlab.data import Data
from datetime import date,timedelta
from talib import abstract
import math
import _beowSet as bs  
import _beowFmt as fm 
import time

data = Data()
pd.set_option('display.expand_frame_repr', False)

# print(data.get("開盤價")["1101"].fillna(0).astype(float)[250: -1] )
def talib2df(talib_output, ma1):
    ret = pd.DataFrame(talib_output).transpose() if (type(talib_output) == list) else pd.Series(talib_output)
    ret.index = ma1.index
    return ret

def genInsertStockParasSQL(stockId):
    iStart = -250

    open    = data.get("開盤價")[stockId].fillna(0).astype(float)[iStart: ]      #如果資料有空白自動填0
    c       = data.get("收盤價")[stockId].fillna(0).astype(float)[iStart: ]
    high    = data.get("最高價")[stockId].fillna(0).astype(float)[iStart: ]
    low     = data.get("最低價")[stockId].fillna(0).astype(float)[iStart: ]
    volumn= data.get("成交股數")[stockId].fillna(0).astype(float)[iStart: ]    
    ma5   = c.ewm(span=5, adjust=False).mean().round(2)                         #以Series來做四捨五入
    ma7   = c.ewm(span=7, adjust=False).mean().round(2)
    ma10  = c.ewm(span=10, adjust=False).mean().round(2)
    ma20  = c.ewm(span=20, adjust=False).mean().round(2)
    ma60  = c.ewm(span=60, adjust=False).mean().round(2)
    ma240 = c.ewm(span=240, adjust=False).mean().round(2)
    kbar  = (c > open)
    kbar  = kbar.apply(lambda x: "R" if x else "G")
    
    yc = c.shift(1, axis = 0)               #昨天的收盤價, shift往後移一天，超級方便!!
    yh = high.shift(1, axis = 0)            #昨天的最高價, shift往後移一天，超級方便!!
    yl = low.shift(1, axis = 0)             #昨天的最低價, shift往後移一天，超級方便!!

    dff = pd.DataFrame({
        "kbar": kbar, "open" :open, "high" : high, "low" : low, "close" : c, 
        "yc": yc, "yh":yh, "yl": yl, "volumn": volumn,
        "ma5" : ma5, "ma7" : ma7, "ma10": ma10, "ma20": ma20, "ma60": ma60, "ma240": ma240
    })
    
    dff["volumn"]       = dff["volumn"].apply(lambda x : 1 if( math.isnan(x) == True ) else int(x/1000))    #張數  
    dff["kbar_top"]     = dff.apply(fm.setKbarTop,    axis = 1)
    dff["kbar_top_y"]   = dff["kbar_top"].shift(1, axis = 0)                                                #昨天的K棒最高點 
    dff["kbar_bottom"]  = dff.apply(fm.setKbarBottom, axis = 1)
    dff["upper-shadow"] = dff.apply(fm.fmtUpperShadow,axis = 1) 
    dff["lower-shadow"] = dff.apply(fm.fmtLowerShadow,axis = 1) 
    dff["kbar-body"]    = dff.apply(fm.fmtKbarBody,   axis = 1)
    dff["amplitude"]    = dff.apply(fm.fmtAmplitude,  axis = 1)  
    dff["iCtnC"]        = dff.apply(fm.fmtCtnC,       axis = 1)
    dff["iGap"]         = dff.apply(fm.fmtIGap,       axis = 1)
    dff["ma_dscr"]      = dff.apply(fm.diffRatio,     axis = 1)
    dff["d_ma5"]        = dff.apply(fm.isCrossMA5,    axis = 1)
    dff["d_ma10"]       = dff.apply(fm.isCrossMA10,   axis = 1)
    dff["d_ma20"]       = dff.apply(fm.isCrossMA20,   axis = 1)
    dff["d_ma60"]       = dff.apply(fm.isCrossMA60,   axis = 1)
    dff["d_ma240"]      = dff.apply(fm.isCrossMA240,  axis = 1)

    dff["sMa5"]         = dff["ma5"] - dff["ma5"].shift(1, axis =0)
    dff["sMa5"]         = dff["sMa5"].apply(lambda x: 1 if (x > 0 ) else -1)
    dff["sMa5y"]        = dff["sMa5"].shift(1, axis =0)
    dff["crvFlagMa5"]   = dff["sMa5"] * dff["sMa5"].shift(1, axis = 0)
    dff["maF5"]         = dff.apply(fm.fmtGetCurvHook, axis = 1)

    dff["sMa10"]         = dff["ma10"] - dff["ma10"].shift(1, axis =0)
    dff["sMa10"]         = dff["sMa10"].apply(lambda x: 1 if (x > 0 ) else -1)
    dff["sMa10y"]        = dff["sMa10"].shift(1, axis =0)
    dff["crvFlagMa10"]   = dff["sMa10"] * dff["sMa10"].shift(1, axis = 0)
    dff["maF10"]         = dff.apply(fm.fmtGetCurvHook, axis = 1)

    dff["sMa20"]         = dff["ma20"] - dff["ma20"].shift(1, axis =0)
    dff["sMa20"]         = dff["sMa20"].apply(lambda x: 1 if (x > 0 ) else -1)
    dff["sMa20y"]        = dff["sMa20"].shift(1, axis =0)
    dff["crvFlagMa20"]   = dff["sMa20"] * dff["sMa20"].shift(1, axis = 0)
    dff["maF20"]         = dff.apply(fm.fmtGetCurvHook, axis = 1)

    dff["sMa60"]         = dff["ma60"] - dff["ma60"].shift(1, axis =0)
    dff["sMa60"]         = dff["sMa60"].apply(lambda x: 1 if (x > 0 ) else -1)
    dff["sMa60y"]        = dff["sMa60"].shift(1, axis =0)
    dff["crvFlagMa60"]   = dff["sMa60"] * dff["sMa60"].shift(1, axis = 0)
    dff["maF60"]         = dff.apply(fm.fmtGetCurvHook, axis = 1)

    dff["sMa240"]        = dff["ma240"] - dff["ma240"].shift(1, axis =0)
    dff["sMa240"]        = dff["sMa240"].apply(lambda x: 1 if (x > 0 ) else -1)
    dff["sMa240y"]       = dff["sMa240"].shift(1, axis =0)
    dff["crvFlagMa240"]  = dff["sMa240"] * dff["sMa240"].shift(1, axis = 0)
    dff["maF240"]        = dff.apply(fm.fmtGetCurvHook, axis = 1)

    # 改善dtypes來提升效能
    dff = dff.astype({"kbar":"category","ma_dscr":"category","d_ma5":"category","d_ma5":"category","d_ma10":"category","d_ma20":"category","d_ma60":"category","d_ma240":"category","maF5":"category","maF10":"category","maF20":"category","maF60":"category","maF240":"category"})
    # print(dff.dtypes)

    tailNum = 30
    ma1 = c.tail(tailNum)
    kd = talib2df(abstract.STOCH(high.tail(tailNum), low.tail(tailNum), ma1, fastk_period=9), ma1) #計算KD 
    k = round(kd.tail(1)[0].values[0], 2)
    d = round(kd.tail(1)[1].values[0], 2)
    # print(k,d)

    # Mbox, Qbox, Ybox = c[-30:], c[-60:], c[-240:]                                            #近30、60、240日最大的數值 
    # Highest_MM, Lowest_MM  = c[(c == Mbox.max())].tail(1) , c[(c == Mbox.min())].tail(1)    #找出月內最高與最低的股價
    # Highest_QQ, Lowest_QQ  = c[(c == Qbox.max())].tail(1) , c[(c == Qbox.min())].tail(1)    #找出月內最高與最低的股價
    # Highest_YY, Lowest_YY  = c[(c == Ybox.max())].tail(1) , c[(c == Ybox.min())].tail(1)    #找出月內最高與最低的股價
    # Highest_MM_Date, Lowest_MM_Date = Highest_MM.index[0].strftime("%Y-%m-%d"), Lowest_MM.index[0].strftime("%Y-%m-%d")
    # Highest_QQ_Date, Lowest_QQ_Date = Highest_QQ.index[0].strftime("%Y-%m-%d"), Lowest_QQ.index[0].strftime("%Y-%m-%d")
    # Highest_YY_Date, Lowest_YY_Date = Highest_YY.index[0].strftime("%Y-%m-%d"), Lowest_YY.index[0].strftime("%Y-%m-%d")
    # print("月", Highest_MM_Date, Lowest_MM_Date, Highest_MM.values[0], Lowest_MM.values[0])
    # print("季", Highest_QQ_Date, Lowest_QQ_Date, Highest_QQ.values[0], Lowest_QQ.values[0])
    # print("年", Highest_YY_Date, Lowest_YY_Date, Highest_YY.values[0], Lowest_YY.values[0])
    # print(dff[-5:])

    df = dff[-1:].copy()                            # 資料若不copy會引發 Returning a view versus a copy 的錯誤。
    df[["stockId","k","d"]] = [stockId, k, d]
    df["today"]             = df.index.date[0].strftime("%Y-%m-%d")
    df["sql_Paras"]         = df.apply(fm.fmtSql_stockParas, axis = 1)
    df["sql_MA"]            = df.apply(fm.fmtSql_stockMA   , axis = 1)
    sql_Paras               = df.iloc[0]["sql_Paras"]
    sql_MA                  = df.iloc[0]["sql_MA"]
    return [sql_Paras, sql_MA]

#==================================================================

_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

nowDate = data.get("開盤價")["1101"].fillna(0).astype(float).tail(1).index.date[0]
price   = pd.read_pickle("history/tables/bargin_report.pkl")
pp      = price.tail(1).index.levels[0]

sqlkeep, i, sql_Paras, sql_MA, arr, brr, stockIds = "", 0, "", "", [], [], bs.getAllStockIds(pp, False)

for stockId in stockIds:
    if(stockId >= "1101" and stockId <="9963" ):
        i += 1
        ss = genInsertStockParasSQL(stockId)
        
        arr.append(ss[0])
        brr.append(ss[1])
        
        if (i % 50 == 0):
            sql_Paras = "insert into dbo.StockParas (stockId, closeDate,kbar, v, o, c, h, l, yc, head, body, footer, iGap,amplitude,k,d) values " + "\n,".join(arr)
            sql_MA    = "insert into dbo.StockMA (stockId, closeDate,kbar,ma_dscr, ma5, ma7, ma10, ma20, ma60, ma240, d_ma5, d_ma10, d_ma20, d_ma60, d_ma240, maF5, maF10, maF20, maF60, maF240) values " + "\n,".join(brr)
            sql = sql_Paras +"\n"+ sql_MA
            print(i)
            sqlkeep += sql
            bs.InsertIntoMSSQL2017(sql) #一次輸入給SQL新增。更快!
            sql_Paras, sql_MA, arr, brr = "", "", [], []


sql_Paras = "insert into dbo.StockParas (stockId, closeDate,kbar, v, o, c, h, l, yc, head, body, footer, iGap,amplitude,k,d) values " + "\n,".join(arr)
sql_MA    = "insert into dbo.StockMA (stockId, closeDate,kbar,ma_dscr, ma5, ma7, ma10, ma20, ma60, ma240, d_ma5, d_ma10, d_ma20, d_ma60, d_ma240, maF5, maF10, maF20, maF60, maF240) values " + "\n,".join(brr)
sql = sql_Paras +"\n"+ sql_MA
print(i)
sqlkeep += sql
bs.InsertIntoMSSQL2017(sql) #一次輸入給SQL新增。更快!
sql_Paras, sql_MA, arr, brr = "", "", [], []

import os
import codecs
fm.write_LogFile(f"sqlback/{nowDate}.sql", sqlkeep)   #備份指令的路徑
sqlkeep = ""
today   = nowDate.strftime("%Y-%m-%d")

dfpp = pd.read_pickle("history/tables/bargin_report.pkl")
dfpp = dfpp[dfpp.index.get_level_values("date") == today ]  # .reset_index()重新洗index也是方法， pd.indexSlice切index也是方法
dfpp = dfpp.rename( columns = {
    "外陸資買進股數(不含外資自營商)" : "fcb", "外陸資賣出股數(不含外資自營商)" : "fcs", "外陸資買賣超股數(不含外資自營商)": "fc", "外資自營商買進股數" : "fob", "外資自營商賣出股數" : "fos", "外資自營商買賣超股數" : "fo",
    "投信買進股數" : "icb", "投信賣出股數" : "ics", "投信買賣超股數" : "ic", 
    "自營商買進股數(自行買賣)" : "dlb", "自營商賣出股數(自行買賣)" : "dls","自營商買賣超股數(自行買賣)" : "dealer", "自營商買進股數(避險)" : "dvb", "自營商賣出股數(避險)" : "dvs", "自營商買賣超股數(避險)" : "dealer2"
}, errors="raise")

dfpp            = dfpp.drop(["fcb","fcs","fob","fos","fo","icb","ics","dlb","dls","dvb","dvs"], axis=1)    #第一次移除不必要的欄位
dfpp["sid"]     = dfpp.index.get_level_values("stock_id").str.split(" ")
dfpp["stock_id"]= dfpp["sid"].apply(lambda x : x[0] if (len(x) == 2) else "")
dfpp["_fc"]     = (dfpp["fc"].astype("int")/1000).round()
dfpp["_ic"]     = (dfpp["ic"].astype("int")/1000).round()
dfpp["_dc"]     = ((dfpp["dealer"].astype("int") + dfpp["dealer2"].astype("int"))/1000).round()
dfpp["dt"]      = dfpp.index.get_level_values("date").strftime("%Y-%m-%d")
dfpp            = dfpp.drop(["sid","dealer","dealer2"], axis=1)                                     #第二次移除不必要的欄位
# print(dfpp)
v     = data.get("成交股數").fillna(0).astype(float)[-70:]    #計算股票數量/1000 = ?張數
v     = (v/1000).round().astype(int).fillna(0) 
yv    = v.shift(1, axis = 0).fillna(0).astype(int)
vma5  = v.ewm(span=5, adjust=False).mean().round().astype(int).fillna(0)
vma20 = v.ewm(span=20, adjust=False).mean().round().astype(int).fillna(0)
vma60 = v.ewm(span=60, adjust=False).mean().round().astype(int).fillna(0)

dfi =pd.DataFrame({
    "yv"   : yv.loc[today],
    "v"    : v.loc[today], 
    "ma5"  : vma5.loc[today], 
    "ma20" : vma20.loc[today], 
    "ma60" : vma60.loc[today]
})
dfpp.index          = dfpp.index.droplevel()
dfp                 = pd.merge(dfpp, dfi, on ="stock_id")   #將[三大法人] 與 [數量統計]合併merge。
print(dfp[:10])
# #--------------------------------------------------
dfp["sql_volumn"]   = dfp.apply(fm.fmtSql_Volumn, axis= 1)  #產出SQL指令碼

svaccum, sql_volumn = "",""                                 #切成100筆一份同時 insert到MSSQL當中。
for i in range(1,17):
    a, b = (i-1)*100, i*100
    sql_volumn = "insert into volumn(stockId,closeDate,fc,ic,dealer,accu_fc,accu_ic,k_fc,k_ic,yv,v,ma5,ma20,ma60) values " + ",".join(dfp[dfp["stock_id"].str.len() == 4 ]["sql_volumn"][a:b].tolist())
    # print(sql_volumn)
    svaccum += sql_volumn
    bs.InsertIntoMSSQL2017(sql_volumn)                      #一次輸入給SQL新增。更快!

fm.write_LogFile(f"sqlback/{today}_volumns.sql", svaccum)   #備份指令的路徑


# ---月營收計算------------------------------------------------------------------------
df = data.get("當月營收")
df = df[df.notna()]         #找出不是nan的資料
drKeys  = df.keys()         #GOOD!
Now     = df.tail(1).max().fillna(0).astype("int")
Max     = df.max().fillna(0).astype("int")
Max2    = df[:-1].max().fillna(0).astype("int")         #上個月之前的歷史最高營收
NowDt   = df.tail(1).idxmax().dt.strftime("%Y-%m-%d")
MaxDt   = df.idxmax().dt.strftime("%Y-%m-%d")           #.index[0].strftime("%Y-%m-%d")
Max2Dt  = df[:-1].idxmax().dt.strftime("%Y-%m-%d")

df2 = pd.DataFrame({"stockId":drKeys, "now": Now, "nowDt": NowDt, "max": Max, "maxDt": MaxDt, "max2": Max2, "max2Dt": Max2Dt})
df2["isHisMax"] = (df2["now"] == df2["max"])

target           = df2[df2["isHisMax"]==True].copy().dropna()
target["sql"]    = target.apply(fm.fmtSQL_maxMMRevenue, axis = 1)

sql_maxMonthEarn = "\n".join(target["sql"].tolist())
fm.write_LogFile(f"sqlback/{today}_monthEarn.sql", sql_maxMonthEarn)
bs.InsertIntoMSSQL2017(sql_maxMonthEarn)
bs.proc_final_SqlScript2(today)                         #執行SP

print("開始", _start)
print("結束", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))