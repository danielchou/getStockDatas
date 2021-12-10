import pyodbc
import time

#排除不列入追蹤的股票，加快速度
remove_stocks =[
"0050","0051","0052","0053","0054","0055","0056","0057",
"1213","1258","1262","1324","1333","1417","1418","1438","1470","1472","1475","5227", #資料不連續，壞了"
"1538","1566","1603","1704","1787","2008","2012","2035","2061","2064","2066","2067","2104","2230","2424","2475",
"2543","2611","2712","2718","2722","2724","2734","2740","2910","2924","2936","2937","3036","3064","3066",
"3073","3086","3093","3095","3130","3162","3207","3219","3219","3226","3288","3308","3332","3339","3434",
"3452","3465","3516","3519","3555","3557","3562","3579","3629","3682","3701","3709","4131","4180","4183",
"4304","4305","4406","4415","4416","4419","4429","4533","4542","4543","4556","4711","4725","4741","4754","4767",
"4905","4911","4934","4947","4950","5011","5013","5202","5205","5259","5269","5276","5304","5317","5348",
"5364","5381","5398","5455","5468","5480","5516","5520","5543","5601","5603",
"5703","5704","5820","5902","6103","6144","6174","6198","6199","6204",
"6212","6218","6221","6228","6241","6242","6246","6247","6287","6291","6418","6419","6425",
"6464","6512","6574","6590","6593","6594","6616","6625","6629","6640","6649","6680",
"7402","8067","8080","8080","8087","8291","8342","8354","8409","8418","8420","8423",
"8426","8455","8472","8481","8488","8913","8917","8921","8923","8927","8934","8937",
"8941","9157","9918","9926","9928","9931","9950","9960",
"1454","1468", "1525", #昶和 上下針太多
"1726","1799",
"1808", "6264", #建材營造
"2302","2364",
"2476", #鉅祥 :上下針太多
"3051", #特力
"5533", "5355", #黃鼎，上下針太多
"5475", #德宏，水餃股
"5701", #劍湖山，太小了
"6131", #悠克? 太怪
"6133", #金橋
"6225", #雞蛋水餃股
"6548","8072", #太奇怪
"9949", #受疫情影響，估2月份到2/13止大陸/台灣地區營收分別減少24萬人民幣、130萬台幣 
### 大陸工廠 ###    
"3593", #力銘(蘇州廠)
"1902","2311","2325","1902","2499", #台指,日月光...下市
"3514","3561","2856","4984","6145","6422","8287", #被併購、暫停交易
"6201","6203","6205","6206","6207","6208","8201" # 元大富櫃50  這算三大法人數量會出問題
"3068","3553","4762","4965","5384","5491","6022","6105","6107","6554","9103","9105","9106","9110","9136","9188"
]

def DisplayNameMA(v):
    return { 5: "週", 20: "月",60: "季",240: "年", }.get(v,'error') 

def getAllStockIds(lastStockPrices, isAll):
    i=0
    stkIds=[]  #初始化清除歸零
    
    for p in lastStockPrices:
        arr = p.split(" ")
        stockId = arr[0]
        if (len(stockId)==4):
            stkIds.append(stockId)
            i+=1
    
    res = stkIds if isAll else [i for i in stkIds if i not in remove_stocks] 
    res2 = set(res)
    print(len(stkIds), "要取消的股票:", len(remove_stocks), "去重複之前:",len(res), "去除重複之後:", len(res2) )  
    return sorted(res2)

#寫入到資料庫中.....
def InsertIntoMSSQL2017(sql):
    server = 'SQL5059.site4now.net'
    database = 'DB_9AB840_Vague'
    username = 'DB_9AB840_Vague_admin'
    password = 'Apple005'
    driver= '{ODBC Driver 13 for SQL Server}'
    cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    
    cursor.execute(sql)
    cursor.commit()

#寫入到資料庫中.....
def ExecuteMSSQL(sql):
    server = 'SQL5059.site4now.net'
    database = 'DB_9AB840_Vague'
    username = 'DB_9AB840_Vague_admin'
    password = 'Apple005'
    driver= '{ODBC Driver 13 for SQL Server}'
    cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()

    cursor.execute(sql)
    cursor.commit()
    

def proc_final_SqlScript(today):
    
    """將每日重複手動執行的sql指令最後自動化完成

    Keyword arguments:
    Args:
        today: 今天日期
    """

    sql="""
        EXEC dbo.sp_upateLatestCloseDate;
        EXEC dbo.sp_setKbar '{0}';
        EXEC dbo.sp_removeDupeVolumn '{0}';
        EXEC dbo.sp_SetBWM_BoxTopIsCross '{0}';
        EXEC dbo.sp_SetDayTradeTarget '{0}';	
    """
    sql = sql.format(today)
    _start = time.strftime("%H:%M:%S", time.localtime())
    ExecuteMSSQL(sql)
    _end = time.strftime("%H:%M:%S", time.localtime())
    
    print(today, "股票資料處理結束", _start, _end)
    ###end