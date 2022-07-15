# Importation des librairies
import streamlit as st
from pandas_datareader.data import DataReader
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.express as px
import plotly.tools as tls
from plotly.offline import iplot

# En-tête de l'application
st.title('Stratégie de Trading avec la technique de moyenne mobile')
st.markdown("*Cette application a été réalisée par Josué AFOUDA*")

############################ Web Scraping des marchés boursiers #########################################################""
url_sp500 = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies" # USA
url_cac40 = "https://en.wikipedia.org/wiki/CAC_40" # Paris
url_ftse100 = "https://en.wikipedia.org/wiki/FTSE_100_Index" # Londres
url_nikkei = "https://topforeignstocks.com/indices/the-components-of-the-nikkei-225-index/" # Tokyo
url_dax = "https://en.wikipedia.org/wiki/DAX" # Berlin

dax = pd.read_html(url_dax)[3]
dax['NameofStock'] = dax['Company'] + "_" + dax['Ticker symbol']

nikkei = pd.read_html(url_nikkei)[0]
nikkei['Company Name'] = nikkei['Company Name'].replace(",", "")
nikkei['NameOfStock'] = nikkei['Company Name'] + "_" + nikkei['Code'].map(str) + ".T"

sp500 = pd.read_html(url_sp500)[0]
sp500['NameOfStock'] = sp500['Security'] + "_" + sp500['Symbol']

cac40 = pd.read_html(url_cac40)[3]
cac40['NameOfStock'] = cac40['Company'] + "_" + cac40['Ticker']

ftse100 = pd.read_html(url_ftse100)[3]
ftse100['NameOfStock'] = ftse100['Company'] + "_" + ftse100["EPIC"]

def load_data(symbol, start_date, end_date):
	stock_data = DataReader(symbol, data_source = "yahoo", start = start_date, end = end_date)
	return stock_data

def list_of_stocks(market_name):
	if market_name == "SP500 (USA)":
		stocks = sp500['NameOfStock'].to_list()
	elif market_name == "CAC 40 (France)":
		stocks = cac40['NameOfStock'].to_list()
	elif market_name == "FTSE 100 (Angleterre)":
		stocks = ftse100['NameOfStock'].to_list()
	elif market_name == "NIKKEI (Japon)":
		stocks = nikkei['NameOfStock'].to_list()
	else:
		stocks = dax['NameofStock'].to_list()
	return stocks

######################################################################################################
market = st.sidebar.selectbox('Choose a Stock Market', ["SP500 (USA)", "CAC 40 (France)", "FTSE 100 (Angleterre)", "NIKKEI (Japon)", "DAX (Allemagne)"])
stocks_list = list_of_stocks(market_name = market)

stock = st.sidebar.selectbox('Choose a Stock to analyse', stocks_list) 

st.sidebar.write('Choose a period of analysis:')
date1 = st.sidebar.date_input("Start Date", value = date(2017, 1, 1))
date2 = st.sidebar.date_input("End Date", value = date(2022, 1, 1))

short = st.sidebar.slider("Short Moving Average", min_value = 0, max_value = 200, value = 20)
long = st.sidebar.slider("Long Moving Average", min_value = 0, max_value = 200, value = 100)
	
# Get the stock price data of a particular company from the Yahoo website
df = load_data(symbol = stock.split("_")[1], start_date = date1, end_date = date2)

if st.sidebar.checkbox("Données brutes",False):
	st.subheader(str(stock.split("_")[0]) + str(" Data"))
	st.write(df)

# Boxplot of prices and Volume plot
col1, col2 = st.columns(2)
with col1:
	box = px.box(df, y = "Close", title = str(stock.split("_")[1]) + ' Closing Price')
	st.plotly_chart(box)

# Volume Price
with col2:
	ch = px.line(df.reset_index(), x = "Date", y = "Volume", title = str(stock.split("_")[1]) + " Volume Price")
	st.plotly_chart(ch)
	
# Calculate the 20 and 100 days moving averages
short_rolling = df['Close'].rolling(window = 20).mean()
long_rolling = df['Close'].rolling(window = 100).mean()

# Calculate the "buy" and "sell" signals and positions
df['Signal'] = 0.0
df['Signal'] = np.where(short_rolling > long_rolling, 1.0, 0.0)
df['Position'] = df['Signal'].diff()

	# Plot the data
fig, ax = plt.subplots(figsize=(12,5))
ax.plot(df['Close'].index, df['Close'], label = str(stock.split("_")[0]))
ax.plot(short_rolling.index, short_rolling, label = str(short) + ' days rolling')
ax.plot(long_rolling.index, long_rolling, label = str(long) + ' days rolling')

# plot 'buy' signals
plt.plot(df[df['Position'] == 1].index, short_rolling[df['Position'] == 1], '^', markersize = 15, color = 'black', label = 'buy')
# plot 'sell' signals
plt.plot(df[df['Position'] == -1].index, short_rolling[df['Position'] == -1], 'v', markersize = 15, color = 'r', label = 'sell')
ax.set_xlabel('Date')
ax.set_ylabel('Closing price ($)')
ax.legend()

## convert and plot in plotly
plotly_fig = tls.mpl_to_plotly(fig)
st.plotly_chart(plotly_fig)
