from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import uvicorn
import logging
from decouple import config
from telegram import Bot
import asyncio
import pygame  # Import the pygame library

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Load your environment variables using config from decouple
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")
BLYNK_AUTH_TOKEN = config("BLYNK_AUTH_TOKEN")

# Create a Telegram bot instance
bot = Bot(token=TELEGRAM_BOT_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pygame.mixer.init()

async def send_telegram_notification(message, lat, lon):
    try:
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        notification = f"ALERT AT LOCATION: Latitude {lat}, Longitude {lon}\n{message}\nMaps: {maps_link}"
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=notification)
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {str(e)}")

VIBRATION_THRESHOLD = 100
GAS_THRESHOLD = 1000

def fetch_gps_coordinates():
    lat = 20.94960681830769
    lon = 79.02687197225588
    return lat, lon

def fetch_sensor_data(pin, token=BLYNK_AUTH_TOKEN):
    blynk_server = "https://blynk.cloud/external/api/get"
    params = {
        "token": token,
        f"v{pin}": pin
    }

    try:
        response = requests.get(blynk_server, params=params)

        if response.status_code == 200:
            return response.text
        else:
            raise HTTPException(status_code=500, detail=f"Failed to fetch data from Blynk. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making an HTTP request to Blynk: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to make an HTTP request to Blynk: {str(e)}")

@app.get("/")
async def get_page(request: Request, response: HTMLResponse):
    lat, lon = fetch_gps_coordinates()
    context = {"request": request, "lat": lat, "lon": lon}
    return templates.TemplateResponse("index.html", {"request": request, "context": context})

@app.get("/vibration_sensor_data")
async def get_vibration_sensor_data():
    vibration_data = fetch_sensor_data(1)

    if int(vibration_data) > VIBRATION_THRESHOLD:
        lat, lon = fetch_gps_coordinates()
        await send_telegram_notification(f"Vibration sensor reading is above {VIBRATION_THRESHOLD}: {vibration_data}", lat, lon)

        # Play an MP3 file (replace 'alert_sound.mp3' with the path to your MP3 file)
        pygame.mixer.music.load('alert.mp3')
        pygame.mixer.music.play()

    return vibration_data

@app.get("/gas_sensor_data")
async def get_gas_sensor_data():
    gas_data = fetch_sensor_data(2)

    if int(gas_data) > GAS_THRESHOLD:
        lat, lon = fetch_gps_coordinates()
        await send_telegram_notification(f"Gas sensor reading is above {GAS_THRESHOLD}: {gas_data}", lat, lon)

        # Play an MP3 file (replace 'alert_sound.mp3' with the path to your MP3 file)
        pygame.mixer.music.load('alert.mp3')
        pygame.mixer.music.play()

    return gas_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # Initialize the pygame mixer

