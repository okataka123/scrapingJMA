#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import sys

class Location:
    def __init__(self, prec_str, block_str, fromcsv=True, fromweb=False):
        """
        Args:
            prec_str(str): 気象情報を取得したい場所の都道府県・地方情報
            block_str(str): 気象情報を取得したい場所の地点情報
            fromcsv(bool): Trueのとき、csvファイルから位置コード情報を取得する。デフォルトはこちら。
            fromweb(bool): Trueのとき、気象庁HPから位置コード情報を取得する。
        """
        self.prec_str = prec_str
        self.block_str = block_str
        self.columns = ['prec', 'prec_no', 'block', 'block_no']
        self.locations_df = pd.DataFrame([], columns=self.columns)
        if fromcsv:
            self.import_prec_block_no_fromCsv()
        else:
            self.import_prec_block_no_fromWeb()
        self.prec_no, self.block_no = self.extract()

    def import_prec_block_no_fromCsv(self):
        filename = 'locationsTable.csv'
        self.locations_df = pd.read_csv(filename)

    def import_prec_block_no_fromWeb(self):
        """
        気象庁HPから全て地域の位置コード情報を引っ張り、テーブル(self.locations_df)を作る。
        """
        # prec
        precs_table = []
        url = 'https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00'
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'html.parser')
        rows = soup.findAll('area')
        for row in rows:
            prec = row['alt']
            m = re.search(r'.*prec_no=(\d+)', row['href'])
            prec_no = m.group(1)
            precs_table.append((prec, prec_no))
        # block
        for (prec, prec_no) in precs_table:
            blocks_table = []
            rural_url = f'https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture.php?prec_no={prec_no}&block_no=&year=&month=&day=&view='
            rural_html = requests.get(rural_url)
            soup = BeautifulSoup(rural_html.content, 'html.parser')
            rows = soup.findAll('area')
            for row in rows:
                block = row['alt']
                if block[-2:] == '地方' or block[-2:] == '地点' or block[-1:] == '都' \
                    or block[-1:] == '府' or block[-1:] == '県' or block[-5:] == 'へのリンク':
                    continue
                m = re.search(r'.*block_no=(\d+)', row['href'])
                block_no = m.group(1)
                blocks_table.append((block, block_no))
            blocks_table = set(list(blocks_table))
            blocks_table = sorted(blocks_table, key=lambda x: x[0])
            for (block, block_no) in blocks_table:
                data = [prec, prec_no, block, block_no]
                tmp_df = pd.DataFrame([data], columns=self.columns)
                self.locations_df = pd.concat([self.locations_df, tmp_df])
        self.locations_df.reset_index(inplace=True, drop=True)

    def extract(self):
        """
        気象情報を取得したい地域について、位置コード番号を引く。
        """
        df = self.locations_df
        cond = df.loc[(df['prec'] == self.prec_str) & (df['block'] == self.block_str)].index
        if cond.size == 0:
            sys.exit('指定された地域の気象データは取得できません。')
        prec_no = df.loc[cond, 'prec_no'].values[0]
        block_no = df.loc[cond, 'block_no'].values[0]
        return prec_no, block_no

    def csvdump(self):
        """
        self.locations_dfに格納された全国の位置コード情報をcsvにdumpする。
        """
        filename = 'locationsTable.csv'
        self.locations_df.to_csv(filename, index=False)

    def verify(self):
        """
        T.B.D.
        HPの情報と、現在持っているテーブルの内容が一致しているか確認する。
        """
        pass

def main():
    pass

if __name__ == '__main__':
    main()
