import ccxt
import pandas as pd
import requests
import time

exchange = ccxt.binance({'rateLimit': 1200, 'enableRateLimit': True})

# setting up the telegram bot
bot_token = 'paste your bot token here'
chat_ids =['']

# Symbols to monitor, it can be any crypto you want
symbols = ['BTC/USDT', 'ETH/USDT']

def fetch_data(symbol, timeframe='15m'): #You can modify the timeframe as you like
    try:
        print(f"Fetching data for {symbol} with timeframe {timeframe}")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_convert('UTC')
        print(f"Data fetched and prepared for {symbol}")
        return df
    except Exception as e:
        print(f"Failed to fetch data for {symbol}: {str(e)}")
        return None

def send_telegram_message(message):
    for chat_id in chat_ids:
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            pass



# For this video I will do the calculation for RSI and stochastic oscillator. But you can do any indicator.
def calculate_rsi(data, period=10):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_stochastic_oscillator(data, k_period=12, d_period = 3, slowing = 3):
    low_min = data['low'].rolling(window=k_period).min()
    high_max = data['high'].rolling(window=k_period).max()
    K = 100 * ((data['close'] - low_min) / (high_max - low_min))
    K = K.rolling(window=slowing).mean()
    D = K.rolling(window=d_period).mean()
    return K, D
def manage_trades(symbol):
    timeframes = ['15m', '30m'] #just an example
    signals = []
    
    for timeframe in timeframes:
        data = fetch_data(symbol, timeframe)
        if data is None:
            continue

        rsi = calculate_rsi(data)
        K, D = calculate_stochastic_oscillator(data)

        if rsi.iloc[-1] < 30 and K.iloc[-1] < 20 and D.iloc[-1] < 20:
            signals.append(True)
        else:
            signals.append(False)
    if all(signals):
        message = f"Strong oversold signal for {symbol} across multiple timeframes"
        send_telegram_message(message)
def automate_trading():
    while True:
        for symbol in symbols:
            try:
                manage_trades(symbol)
            except Exception as e:
                time.sleep(60) #you can modify the refreshing rate as needed.
automate_trading()
#THIS IS JUST AN EXAMPLE OF A TRADING STRATEGY. This strategy might not work, this is not financial advice. You should do backtesting before trying it out!!



