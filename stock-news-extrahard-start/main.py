import datetime
import requests
from twilio.rest import Client
import config

STOCK = "RICK"
COMPANY_NAME = "RCI Hospitality Holdings"
# Holding company for Rick's Cabaret and other strip clubs c:

# Replace all below with relevant API keys, phone numbers, etc.
twilio_account_sid = config.twilio_account_sid
twilio_auth_token = config.twilio_auth_token
twilio_phone = config.twilio_phone
target_phone = config.target_phone
alpha_vantage_api_key = config.alpha_vantage_api_key
news_api_key = config.news_api_key

alpha_vantage_url = 'https://www.alphavantage.co/query'
alpha_vantage_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": alpha_vantage_api_key,
}

relevant_news_dates = datetime.date.today() - datetime.timedelta(30)
news_api_url = "https://newsapi.org/v2/everything"
news_api_params = {
    "q": COMPANY_NAME,
    "from": relevant_news_dates,
    "language": "en",
    "pageSize": 3,
    "apiKey": news_api_key
}

alpha_vantage_response = requests.get(url=alpha_vantage_url, params=alpha_vantage_params)
alpha_vantage_response.raise_for_status()
stock_data = alpha_vantage_response.json()

price_yesterday = float(stock_data["Time Series (Daily)"][list(stock_data["Time Series (Daily)"])[1]]["4. close"])
price_ereyesterday = float(stock_data["Time Series (Daily)"][list(stock_data["Time Series (Daily)"])[2]]["4. close"])
price_dif_percentage = round(((price_yesterday - price_ereyesterday) / price_ereyesterday) * 100, 2)

if abs(price_dif_percentage) >= 5:
    news_api_response = requests.get(url=news_api_url, params=news_api_params)
    news_api_response.raise_for_status()
    news_data = news_api_response.json()

    if price_dif_percentage > 0:
        inc_dec_symbol = "🔺"
    else:
        inc_dec_symbol = "🔻"

    for article in news_data["articles"]:
        client = Client(twilio_account_sid, twilio_auth_token)
        message = client.messages.create(
            body=f"{STOCK}: {inc_dec_symbol}{abs(price_dif_percentage)}%\n"
                 f"Headline: {article['title']}\n"
                 f"Brief: {article['description']}",
            from_=twilio_phone,
            to=target_phone
        )
