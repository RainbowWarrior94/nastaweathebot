import os
import requests
import telebot
from flask import Flask, request

BOT_TOKEN = os.environ['BOT_TOKEN']
API_KEY = os.environ['API_KEY']
WEBHOOK_URL = os.environ['WEBHOOK_URL']

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "ok", 200

def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    resp = requests.get(url).json()

    if resp.get("cod") != 200:
        return f"Error: {resp.get('message', 'could not get the data')}"

    temp = resp["main"]["temp"]
    feels_like = resp["main"]["feels_like"]
    desc = resp["weather"][0]["description"]
    rain_1h = resp.get("rain", {}).get("1h", 0)
    if rain_1h == 0:
        rain = "no rain"
    elif rain_1h <= 10:
        rain = "light rain / drizzle"
    else:
        rain = "heavy rain"

    answer = f"Current weather in {city_name}: {temp}°C (feels like: {feels_like}°C)\nWeather conditions: {desc}\nRain: {rain}"
    return answer

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Please enter the name of the city to get the weather data.")

@bot.message_handler(content_types=['text'])
def send_weather(message):
    city = message.text
    try:
        weather_info = get_weather(city)
    except Exception as e:
        weather_info = f"Error: {e}"
    bot.send_message(message.chat.id, weather_info)

@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
