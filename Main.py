import pandas as pd
import requests
import datetime
import time
import yfinance as yf
from bs4 import BeautifulSoup

# There there is only one html table on this page

url = 'http://www.etnet.com.hk/www/tc/stocks/indexes_detail.php?subtype=HSI'
header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

tickers_rsi = []
tickers_percent_chg = []
tickers_close_price = []
tickers_pe          = []
tickers_dividend    = []
r = requests.get(url, headers=header)
payload = pd.read_html(r.text)

table_0 = payload[0]
df = table_0.drop([0])
df[0] = df[0].str[1:]
df[0] = df[0] + '.HK'
df.loc[df.shape[0] + 1] = ['2800.HK', '盈富基金', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
tickers = df[0].values.tolist()
names = df[1].values.tolist()
print(tickers)
print(names)


def prRed(skk): print("\033[91m {}\033[00m".format(skk))


def prGreen(skk): print("\033[92m {}\033[00m".format(skk))


def get_stock_data(ticker, rsi_period, i):
    # getting rsi

    end_time = datetime.datetime.now().date().isoformat()
    now = datetime.datetime.now().date()
    start_time = now.replace(year=(now.year - 1))

    ticker_object = yf.Ticker(ticker)
    ticker_df = ticker_object.history(period="100d")
    print(ticker_df)
    ticker_df = ticker_df.reset_index()
    df = ticker_df[['Date', 'Close']]
    chg = df['Close'].diff(1)
    gain = chg.mask(chg < 0, 0)
    loss = chg.mask(chg > 0, 0)
    avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    rs = abs(avg_gain / avg_loss)
    rsi = 100 - (100 / (1 + rs))
    percent_chg = df["Close"].pct_change()
    # getting pe and dividend
    tickers_for_aastock = "0" + ticker.strip('.HK')
    url = 'http://www.aastocks.com/tc/stocks/quote/quick-quote.aspx?symbol={}'.format(tickers_for_aastock)
    sess = requests.session()
    time.sleep(1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Referer": "http://www.aastocks.com/tc/default.aspx"
    }
    req = sess.get(url, headers=headers)

    soup = BeautifulSoup(req.text, features="lxml")

    try:
        pe = soup.find_all(class_='ss2 abs lbl_r font-num cls')[4].text
    except:
        pe = None

    try:
        dividend = soup.find_all(class_='ss2 abs lbl_r font-num cls')[5].text
    except:
        dividend = None

    return rsi.iloc[-1], percent_chg[len(percent_chg) - 1], ticker_df.iloc[-1]["Close"], pe, dividend


for i in range(len(tickers)):
    rsi, percent_chg, close_price, pe, dividend = get_stock_data(tickers[i], 14, i)
    tickers_rsi.append(rsi)
    tickers_percent_chg.append(percent_chg)
    tickers_close_price.append(close_price)
    tickers_pe.append(pe)
    tickers_dividend.append(dividend)



df_with_rsi_pe_dividend = pd.DataFrame(list(zip(tickers, names,tickers_rsi,tickers_percent_chg, tickers_close_price, tickers_pe, tickers_dividend)),
               columns = ['Tickers', 'Names', 'RSI', 'Percent_Chg', 'Close', 'Trailing PE', 'Forward Dividend'])



df_with_rsi_pe_dividend = df_with_rsi_pe_dividend.sort_values(by=['RSI'])

print(df_with_rsi_pe_dividend)
df_with_rsi_pe_dividend.to_excel("output.xlsx")

df_with_rsi_pe_dividend = df_with_rsi_pe_dividend.reset_index(drop=True)

for j in range(df_with_rsi_pe_dividend.shape[0]):
    print(df_with_rsi_pe_dividend.iloc[j]['Tickers'], df_with_rsi_pe_dividend.iloc[j]['Names'], ':')

    if df_with_rsi_pe_dividend.iloc[j]['RSI'] >= 70:
        prRed(round(df_with_rsi_pe_dividend.iloc[j]['RSI'], 2))

    elif df_with_rsi_pe_dividend.iloc[j]['RSI'] < 40:
        prGreen(round(df_with_rsi_pe_dividend.iloc[j]['RSI'], 2))

    else:
        print(round(df_with_rsi_pe_dividend.iloc[j]['RSI'], 2))

    print("$", round(df_with_rsi_pe_dividend.iloc[j]["Close"], 3))

    if df_with_rsi_pe_dividend.iloc[j]["Percent_Chg"] < 0:
        prRed(round(df_with_rsi_pe_dividend.iloc[j]["Percent_Chg"]  * 100, 2))

    elif df_with_rsi_pe_dividend.iloc[j]["Percent_Chg"] > 0:
        prGreen(round(df_with_rsi_pe_dividend.iloc[j]["Percent_Chg"] * 100, 2))

    else:
        print(round(df_with_rsi_pe_dividend.iloc[j]["Percent_Chg"] * 100, 2))

    print(" ")

