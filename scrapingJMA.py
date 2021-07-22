#!/usr/bin/env python
# References: https://qiita.com/Cyber_Hacnosuke/items/122cec35d299c4d01f10
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import timedelta
import datetime as dt
import os, sys
from Location import *

class JMAData:
    def __init__(self, prec_str, block_str, startyear, startmonth, startday, endyear=None, endmonth=None, endday=None):
        """
        Args:
            prec_str(str): 都道府県・地方情報
            block_str(str): 地点情報
            startyear(int): 開始年
            startmonth(int): 開始月
            startday(int): 開始日
            endyear(int): 終了年
            endmonth(int): 終了月
            endday(int): 終了日
        """
        self.prec_str = prec_str
        self.block_str = block_str
        if endyear is None:
            endyear = startyear
        if endmonth is None:
            endmonth = startmonth
        if endday is None:
            endday = startday
        self.prec_no, self.block_no = self.getlocationcode()
        self.startDateTime = pd.to_datetime(str(startyear)+'/'+str(startmonth)+'/'+str(startday))
        self.endDateTime = pd.to_datetime(str(endyear)+'/'+str(endmonth)+'/'+str(endday))
        self.isVarid_specifiedDatetime(self.startDateTime, self.endDateTime)
        self.header = ['時刻', '現地気圧(hPa)', '海面気圧(hPa)', '降水量(mm)', '気温(℃)',  '相対湿度(％)',
            '平均風速(m/s)', '平均風向', '最大瞬間風速(m/s)', '最大瞬間風向',
        ]
        self.jma_df = pd.DataFrame(columns=self.header)

    def isVarid_specifiedDatetime(self, sd, ed):
        if sd > ed:
            sys.exit('開始日時が終了日時よりも過去になっています。')
        today = pd.to_datetime('today').date()
        if sd >= today or ed >= today:
            sys.exit('指定日時が現在よりも未来になっています。昨日までの日時を指定してください。')

    def getlocationcode(self):
        loc = Location(self.prec_str, self.block_str)
        return loc.prec_no, loc.block_no

    def str2float(self, string):
        try:
            return float(string)
        except:
            return 0.0

    def construct_oneday_WeatherData(self, year, month, day):
        """
        oneday
        """
        today = pd.to_datetime(str(year)+'/'+str(month)+'/'+str(day))
        yesterday = today - timedelta(days=1)

        # 昨日の24:00 
        url = f'http://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no={self.prec_no}&block_no={self.block_no}&year={yesterday.year}&month={yesterday.month}&day={yesterday.day}&view='
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'html.parser')
        rows = soup.findAll('tr', class_='mtx')
        rows = rows[2:]
        for row in rows:
            data = row.findAll('td')
            rowData = []
            if data[0].string == '24:00':
                datetime = str(year)+'/'+str(month)+'/'+str(day)+' '+'00:00:00'
                datetime = pd.to_datetime(datetime)
                rowData.append(datetime)
                rowData.append(self.str2float(data[1].string))  
                rowData.append(self.str2float(data[2].string))  
                rowData.append(self.str2float(data[3].string))  
                rowData.append(self.str2float(data[4].string))  
                rowData.append(self.str2float(data[5].string))  
                rowData.append(self.str2float(data[6].string))  
                rowData.append(data[7].string)  
                rowData.append(self.str2float(data[8].string))
                rowData.append(data[9].string)  
                rowData = pd.DataFrame([rowData], columns = self.header)
                self.jma_df = pd.concat([self.jma_df, rowData])

        # 今日の00:00-23:50
        url = f'http://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no={self.prec_no}&block_no={self.block_no}&year={year}&month={month}&day={day}&view='
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'html.parser')
        rows = soup.findAll('tr', class_='mtx')
        rows = rows[2:]
        for row in rows:
            data = row.findAll('td')
            rowData = []
            if data[0].string != '24:00':
                datetime = str(year)+'/'+str(month)+'/'+str(day)+' '+data[0].string+':00'
                datetime = pd.to_datetime(datetime)
                rowData.append(datetime)
                rowData.append(self.str2float(data[1].string))  
                rowData.append(self.str2float(data[2].string))  
                rowData.append(self.str2float(data[3].string))  
                rowData.append(self.str2float(data[4].string))  
                rowData.append(self.str2float(data[5].string))  
                rowData.append(self.str2float(data[6].string))  
                rowData.append(data[7].string)  
                rowData.append(self.str2float(data[8].string))
                rowData.append(data[9].string)  
                rowData = pd.DataFrame([rowData], columns = self.header)
                self.jma_df = pd.concat([self.jma_df, rowData])
    
    def constructWeatherData(self):
        datetime = self.startDateTime
        while True:
            if datetime == self.endDateTime+timedelta(days=1):
                break
            year = datetime.year
            month = datetime.month
            day = datetime.day
            self.construct_oneday_WeatherData(year=year, month=month, day=day)
            datetime += timedelta(days=1)
        self.jma_df.reset_index(inplace=True, drop=True)
        return self.jma_df
                
    def dumpcsv(self, everydays=False):
        """
        気象データDataFrameをcsvにdumpする。

        Args:
            everydays(bool): これがTrueのとき、開始日〜終了日までの1日ごとのcsvにdumpされる。
                             これがFalseならば、DataFrameは一つのファイルに全てdumpされる。
        """
        dumpdirname = 'csvout'
        if not os.path.exists(dumpdirname):
            os.mkdir(dumpdirname)
        if not everydays:
            startday_str = self.startDateTime.strftime('%Y%m%d')
            endday_str = self.endDateTime.strftime('%Y%m%d')
            self.jma_df.to_csv(f'./csvout/jmaData_{self.prec_str}_{self.block_str}_{startday_str}_{endday_str}.csv', index=False)
        else:
            datetime = self.startDateTime
            while True:
                if datetime == self.endDateTime+timedelta(days=1):
                    break
                day_str = datetime.strftime('%Y%m%d')
                day_df = self.jma_df.loc[self.jma_df['時刻'].dt.date==datetime]
                day_df.to_csv(f'./csvout/jmaData_{self.prec_str}_{self.block_str}_{day_str}_{day_str}.csv', index=False)
                datetime += timedelta(days=1)

def main():
    pass

if __name__ == '__main__':
    main()

