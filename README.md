# scrapingJMA
scrapingJMAとは、気象庁のHPから過去の10分間隔気象データを取得し、
pandasのDataFrameやcsvファイルに落とすためのツールです。

# 気象データについて

[気象庁](https://www.jma.go.jp/jma/index.html)による過去の気象データ(10分間隔)を取得し、pandasのDataFrameやcsvファイルに落とすことができます。取得できるデータ項目は、
- `現地気圧(hPa)`
- `海面気圧(hPa)`
- `降水量(mm)`
- `気温(℃)`
- `相対湿度(%)`
- `平均風速(m/s)`
- `平均風向`
- `最大瞬間風速(m/s)`
- `最大瞬間風向`

です。

過去の気象データは[気象庁のこのページ](https://www.data.jma.go.jp/obd/stats/etrn/index.php?prec_no=&block_no=&year=&month=&day=&view=)で検索してcsvのダウンロードができますが、
- 10分間隔データについてはcsvのダウンロードができない。
- 連続した数日間の気象データをいっぺんに取ったりすることができない。
- データ取得のためのAPIが公開されていない。

等の理由により、webスクレイピングにより過去の気象データを取ってこれるようにしたツールになっています。
~~本当はｽｸﾚｲﾋﾟﾝｸﾞなんてﾔﾝｷｰな事はやりたくなかった...(´･\_･\`) APIがあれば良かったのにｨ!!(´･\_･\`)~~

# requirements
あまり多くの外部ライブラリを必要としません。必要なのは
```
- pandas
- BeautifulSoup
```

くらい。

# How to use
### pandas.DataFrameに落とす
例えば、神奈川県横浜市の2021/07/01〜2021/07/05の気象データを取得する場合、
```python
from scrapingJMA import *

jma = JMAData('神奈川県', '横浜', 2021, 7, 1, 2021, 7, 5)
df = jma.constructWeatherData()
```
として、`display(df)`などで確認すると下のような感じで取ってこれます。
![df_yokohama](https://user-images.githubusercontent.com/41262277/126608699-fcf8664c-a57c-4a4f-8341-7cd4dd34b229.png)

また、ある1日の気象データのみを取得する場合は、以下のように終了日時を省略できます。
```python
jma = JMAData('神奈川県', '横浜', 2021, 7, 1) # 2021/07/01 の気象データを取得する。
df = jma.constructWeatherData()
```

### 地域の指定方法について
気象データが取得可能な地域は`locationsTable.csv`の中に記載のある`prec`と`block`の組み合わせ限定となっています。
`prec`の地域の文字列を`JMAData()`の第一引数に、`block`の地点の文字列を`JMAData()`の第二引数に指定すればOK！

### csvファイルへのdump方法について
```python
jma.dumpcsv()
```
とすると直下に`csvout`ディレクトリが作成され、その中に気象データのDataFrameがdumpされたcsvファイルが保存されます。神奈川県横浜市の2021/07/01〜2021/07/05の気象データの場合だと、`jmaData_神奈川県_横浜_20210701_20210705.csv`が保存されます。
また、1日ごとに別のcsvファイルにして保存したい場合は、
```python
jma.dumpcsv(everydays=True)
```
とするとOK。今回の場合だと、
```
jmaData_静岡県_静岡_20210701_20210701.csv
jmaData_静岡県_静岡_20210701_20210705.csv
jmaData_静岡県_静岡_20210702_20210702.csv
jmaData_静岡県_静岡_20210703_20210703.csv
jmaData_静岡県_静岡_20210704_20210704.csv
jmaData_静岡県_静岡_20210705_20210705.csv
```
が保存されます。
