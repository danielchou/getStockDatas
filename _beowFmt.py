import pandas as pd
import math

def diffRatio(r):
    w1 , m1, q1, y1 = r["ma5"], r["ma20"], r["ma60"], r["ma240"]
    wmqy_dscr2 = ""                              #有按照大小排列
    dic = { "w" : w1, "m" : m1, "q" : q1, "y": y1 }  #以dict作為排列的工具
    dic2 = { k: v for k, v in sorted( dic.items(), key=lambda item: item[1], reverse = True )}
    wmqy_dscr2 = ",".join(dic2)
    return wmqy_dscr2

def setKbarTop(r):
    return r["close"] if(r["kbar"] == "R") else r["open"]

def setKbarBottom(r):
    return r["close"] if(r["kbar"] == "G") else r["open"]

def isCrossMA5(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma5"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""

def isCrossMA10(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma10"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""

def isCrossMA20(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma20"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""

def isCrossMA60(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma60"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""

def isCrossMA240(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma240"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""
    
# 判斷上下彎勾 ####################################################
def fmtGetCurvHookMa5(r):
    rs, flagN, _n, _y = "", r["crvFlagMa5"], r["sMa5"], r["sMa5y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtGetCurvHookMa10(r):
    rs, flagN, _n, _y = "", r["crvFlagMa10"], r["sMa10"], r["sMa10y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtGetCurvHookMa20(r):
    rs, flagN, _n, _y = "", r["crvFlagMa20"], r["sMa20"], r["sMa20y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtGetCurvHookMa60(r):
    rs, flagN, _n, _y = "", r["crvFlagMa60"], r["sMa60"], r["sMa60y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtGetCurvHookMa240(r):
    rs, flagN, _n, _y = "", r["crvFlagMa240"], r["sMa240"], r["sMa240y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtUpperShadow(r):
    kbar_top, h = r["kbar_top"], r["high"]
    return 0 if (kbar_top == 0) else round((h - kbar_top) / kbar_top * 100, 2)

def fmtLowerShadow(r):
    kbar_bottom, l = r["kbar_bottom"], r["low"]
    return 0 if (l == 0) else round((kbar_bottom - l) / l * 100, 2)

def fmtKbarBody(r):
    kbar_bottom, kbar_top = r["kbar_bottom"], r["kbar_top"]
    return 0 if (kbar_bottom ==0) else round((kbar_top - kbar_bottom) / kbar_bottom * 100, 2)

def fmtAmplitude(r):
    yc, close = r["yc"], r["close"]
    return 0 if (yc ==0) else round((close - yc) / yc * 100, 2)

def fmtCtnC(r):
    yc, close = r["yc"], r["close"]
    return 1 if (yc > close) else 0

#描述價格往上跳空缺口
def fmtIGap(r):
    low, yh, h, ylow= r["low"], r["yh"], r["high"], r["yl"] 
    gap1 = 0 if (math.isnan(yh) or math.isnan(low)) else round(low - yh, 2)
    gap1 = gap1 if(gap1 > 0) else 0
    
    if (gap1 == 0):
        gap2 = 0 if (math.isnan(ylow) or math.isnan(h)) else round(ylow - h, 2)
        return gap2 if(gap2 > 0) else 0
    else:
        return gap1 

def fmtSql_stockParas(r):
    stockId, today, kbar, v, o, c, h, l, yc, iGap, amplitude, k ,d, head, body, footer = r["stockId"], r["today"], r["kbar"], r["volumn"], r["open"], r["close"], r["high"], r["low"], r["yc"], r["iGap"], r["amplitude"], r["k"], r["d"], r["upper-shadow"], r["kbar-body"], r["lower-shadow"]
    # insert into dbo.StockParas (stockId, closeDate,kbar, v, o, c, h, l, yc,iGap,amplitude,k,d) values 
    sql = f"""('{stockId}','{today}','{kbar}',{v},{o},{c},{h},{l},{yc},{head},{body},{footer},{iGap},{amplitude},{k},{d}) """
    return sql

def fmtSql_stockMA(r):
    stockId, today, kbar, ma_dscr           = r["stockId"], r["today"], r["kbar"], r["ma_dscr"]
    ma5, ma7, ma10, ma20, ma60, ma240       = r["ma5"], r["ma7"], r["ma10"], r["ma20"], r["ma60"], r["ma240"]
    maF5, maF10, maF20, maF60, maF240       = r["maF5"], r["maF10"], r["maF20"], r["maF60"], r["maF240"]
    maS5, maS10, maS20, maS60, maS240       = r["maS5a"], r["maS10a"], r["maS20a"], r["maS60a"], r["maS240a"]   #計算斜率
    d_ma5, d_ma10, d_ma20, d_ma60, d_ma240  = r["d_ma5"], r["d_ma10"], r["d_ma20"], r["d_ma60"], r["d_ma240"]
    
    #insert into dbo.StockMA (stockId, closeDate,kbar,ma_dscr, ma5, ma7, ma10, ma20, ma60, ma240, d_ma5, d_ma10, d_ma20, d_ma60, d_ma240, maF5, maF10, maF20, maF60, maF240) values 
    sql = f"""({stockId},'{today}','{kbar}','{ma_dscr}',{ma5},{ma7},{ma10},{ma20},{ma60},{ma240},'{d_ma5}','{d_ma10}','{d_ma20}','{d_ma60}','{d_ma240}','{maF5}','{maF10}','{maF20}','{maF60}','{maF240}',{maS5},{maS10},{maS20},{maS60},{maS240}) """
    return sql

def fmtSql_Volumn(r):
    stockId, dt, fc, ic, dealer, yv, v, ma5, ma20, ma60 = r["stock_id"], r["dt"], r["_fc"], r["_ic"],r["_dc"], r["yv"], r["v"], r["ma5"], r["ma20"], r["ma60"]
    #"insert into volumn(stockId,closeDate,fc,ic,dealer,accu_fc,accu_ic,k_fc,k_ic,yv,v,ma5,ma20,ma60) values 
    sql = f"('{stockId}','{dt}',{fc},{ic},{dealer},0,0,0,0,{yv},{v},{ma5},{ma20},{ma60})"                # Python 語法解析器把 f-string
    return sql

def fmtSQL_maxMMRevenue(r):
    stockId, nowDate, nowRvn, lastMaxDt, lastMaxV = r["stockId"], r["nowDt"], r["now"], r["max2Dt"], r["max2"]

    return f"""if (select count(*) from maxMMRevenue where stockId={stockId} and nowDate='{nowDate}') = 0
    begin insert into maxMMRevenue (stockId,nowDate,nowRvn,lastMaxDate,lastMaxRvn,createdDate) values ('{stockId}','{nowDate}',{nowRvn},'{lastMaxDt}',{lastMaxV},getdate());  end
    """
    
def fmtSql_capital(r):
    stockId, cap = r["stockId"], r["cap"]
    return f"update stock set capital={cap},modifiedDate=getdate() where id='{stockId}'"

import os
import codecs 

def write_LogFile(fileName, write_content):
    os.makedirs(os.path.dirname(fileName), exist_ok=True)
    f = codecs.open(fileName, mode="w", encoding="utf-8", errors="strict")
    f.write(write_content)
    f.close()