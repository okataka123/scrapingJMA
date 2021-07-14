#!/usr/bin/env python
# References: https://qiita.com/Cyber_Hacnosuke/items/122cec35d299c4d01f10
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import timedelta

class JMAData:
    """
    TODO:
        場所指定できるようにする。
        csvに落とせるようにする。
    """

    def __init__(self, startyear, startmonth, startday, endyear=None, endmonth=None, endday=None):
        self.startDateTime = pd.to_datetime(str(startyear)+'/'+str(startmonth)+'/'+str(startday))
        self.endDateTime = pd.to_datetime(str(endyear)+'/'+str(endmonth)+'/'+str(endday))
        self.header = ['時刻', '現地気圧(hPa)', '海面気圧(hPa)', '降水量(mm)', '気温(℃)', '相対湿度(％)', '平均風速(m/s)', '平均風向', '最大瞬間風速(m/s)', '最大瞬間風向']
        self.jma_df = pd.DataFrame(columns=self.header)
    
    def locationcode(self):
        pass

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

        # 現状は静岡県静岡市限定
        # 昨日の24:00 
        url = f'http://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47656&year={yesterday.year}&month={yesterday.month}&day={yesterday.day}&view='
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
        url = f'http://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47656&year={year}&month={month}&day={day}&view='
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
                
    def dumpcsv(self):
        # jmacsvdumpedディレクトリを作る。 
        # csvファイルの命名規則を考える。
        pass

def main():
    df = JMAData(2021, 7, 1, 2021, 7, 1).constructWeatherData()
    print(df)

if __name__ == '__main__':
    main()

