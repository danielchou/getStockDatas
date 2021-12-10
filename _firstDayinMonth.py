
### 計算月K資料
import pandas as pd
import pyodbc
import sqlalchemy
import pyodbc
from finlab.data import Data
# from sqlalchemy.engine import URL
from sqlalchemy import create_engine, event
from talib import abstract
import _beowSet as bs          #自己寫的

engine = create_engine(
    "mssql+pyodbc://DB_9AB840_Vague_admin:Apple005@SQL5059.site4now.net/DB_9AB840_Vague"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)


data = Data()
price = pd.read_pickle("history/tables/bargin_report.pkl")
pp = price.tail(1)
pp = pp.index.levels[0]

stockIds = bs.getAllStockIds(pp, False) 
#print(pd.__version__)

def talib2df(talib_output, ma1):
    if type(talib_output) == list:
        ret = pd.DataFrame(talib_output).transpose()
    else:
        ret = pd.Series(talib_output)
    ret.index = ma1.index
    return ret

for stockId in stockIds:
    #print(i,stockId)
    if stockId >= "1101":
        
#         print(stockId)
        df = data.get("收盤價")[stockId]
        do = data.get("開盤價")[stockId]
        dl = data.get("最低價")[stockId]
        dh = data.get("最高價")[stockId]
        volumns = round(data.get("成交股數")[stockId] /1000)
        
        ttp="M"
        dfw = df.resample(ttp).last() 
        dfw["stockId"] = stockId
        dfw["close"] = df.resample(ttp).last()  #進行轉換，只取一周中最後一個交易日。
        dfw["open"] = do.resample(ttp).first()  #進行轉換，只取一周中最後一個交易日。
        dfw["low"] = dl.resample(ttp).min()  #進行轉換，只取一周中最後一個交易日。
        dfw["high"] = dh.resample(ttp).max()  #進行轉換，只取一周中最後一個交易日。
        dfw["volumn"] = volumns.resample(ttp).sum() #這一周的成交股數
        dfw["close"] = dfw["close"].dropna()
        dfw["high"] = dfw["high"].dropna()
        dfw["low"] = dfw["low"].dropna()
        
        ma1 = dfw["close"]
        ma04r = round(ma1.ewm(span=4, adjust=False).mean(), 2)
        ma12r = round(ma1.ewm(span=12, adjust=False).mean(), 2)
        ma48r = round(ma1.ewm(span=48, adjust=False).mean(), 2)
        ma120r = round(ma1.ewm(span=120, adjust=False).mean(), 2)
        
#         kdDf = [dfw["high"], dfw["low"], dfw["close"]]
#         kdDf = kdDf.dropna()
#         display(kdDf)
        
        kd = talib2df(abstract.STOCH(dfw["high"], dfw["low"], dfw["close"], fastk_period=9), ma1)
#         j = 3*kd[0]- 2*kd[1]
#         print(abstract.STOCH)
        
        frames = [ dfw["open"], dfw["high"], dfw["low"], dfw["close"], dfw["volumn"], ma04r, ma12r, ma48r, ma120r, round(kd[0],2), round(kd[1],2)]
        
        monthBars = pd.concat(frames, axis=1, keys=["o", "h", "l","c","v","ma4","ma12","ma48","ma120","K","D"])
        idx = monthBars.index
        #monthBars = monthBars.reset_index().drop('index', axis=1)
        monthBars = monthBars.reset_index(drop=True)
        monthBars["stockId"] = stockId
        monthBars["date"] = idx
        monthBars = monthBars.dropna().tail(1)
        print(monthBars)
        
        # write the DataFrame to a table in the sql database
        monthBars.to_sql("monthBarsTmp", engine , if_exists='append')