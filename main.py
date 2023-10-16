import math
import time
from time import sleep

import network
import urequests as requests
from machine import Pin, PWM

from config import config

FETCH_INTERVAL_SECONDS = 600
FETCH_INTERVAL_SECONDS_ON_ERROR = 30
PURPLEAIR_API_URL = "https://api.purpleair.com/v1/sensors/"

GREEN = (0, 65535, 0)
YELLOW = (65535, 65535, 0)
ORANGE = (65535, 32405, 0)
RED = (65535, 0, 0)
BLUE = (0, 0, 65535)

pins = [13, 12, 11]
freq_num = 1000

pwm0 = PWM(Pin(pins[0]))
pwm1 = PWM(Pin(pins[1]))
pwm2 = PWM(Pin(pins[2]))
pwm0.freq(freq_num)
pwm1.freq(freq_num)
pwm2.freq(freq_num)

# Forcing the LED off. Deinit is not doing anything....
pwm0.duty_u16(65535)
pwm1.duty_u16(65535)
pwm2.duty_u16(65535)
# pwm0.deinit()
# pwm1.deinit()
# pwm2.deinit()


def connect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan.active(True)
    wlan.connect(config["WLAN_SSID"], config["WLAN_PASSWORD"])
    print('Connecting to a wireless network...')

    while not wlan.isconnected():
        time.sleep(1)
        print('Connecting to a wireless network...')

    print('Successfully connected to wireless network.')
    # print(wlan.ifconfig())

    return wlan


def pm25_to_aqi(pm25):
    # thanks to Mike Bostock https://observablehq.com/@mbostock/pm25-to-aqi
    def lerp(ylo, yhi, xlo, xhi, x):
        return ((x - xlo) / (xhi - xlo)) * (yhi - ylo) + ylo

    c = math.floor(10 * pm25) / 10
    if c < 0:
        a = 0
    elif c < 12.1:
        a = lerp(0, 50, 0.0, 12.0, c)
    elif c < 35.5:
        a = lerp(51, 100, 12.1, 35.4, c)
    elif c < 55.5:
        a = lerp(101, 150, 35.5, 55.4, c)
    elif c < 150.5:
        a = lerp(151, 200, 55.5, 150.4, c)
    elif c < 250.5:
        a = lerp(201, 300, 150.5, 250.4, c)
    elif c < 350.5:
        a = lerp(301, 400, 250.5, 350.4, c)
    elif c < 500.5:
        a = lerp(401, 500, 350.5, 500.4, c)
    else:
        a = 500

    return round(a)


def fetch_pm25():
    url = PURPLEAIR_API_URL + config["PURPLEAIR_STATION_ID"]

    try:
        res = requests.get(url, headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "X-API-Key": config["PURPLEAIR_API_KEY"]
        })
        data = res.json()
        pm25 = data["sensor"]["pm2.5"]
        res.close()

        return pm25
    except Exception as e:
        print("Error during request: ")
        print(e)
        return None


def set_led_color(r, g, b):
    pwm0.duty_u16(65535 - r)
    pwm1.duty_u16(65535 - g)
    pwm2.duty_u16(65535 - b)


def set_led_from_aqi(aqi):
    if aqi <= 50:
        aqi_color = GREEN
    elif aqi <= 100:
        aqi_color = YELLOW
    elif aqi <= 150:
        aqi_color = ORANGE
    else:
        aqi_color = RED
    set_led_color(aqi_color[0], aqi_color[1], aqi_color[2])


def set_led_error():
    # Change the color to alert there's some type of connection issue.
    set_led_color(BLUE[0], BLUE[1], BLUE[2])


def main_loop():
    wlan = connect_wlan()

    while True:
        if wlan.isconnected():
            pm25 = fetch_pm25()
            if pm25 is not None:
                aqi = pm25_to_aqi(pm25)
                print("PM2.5: " + str(pm25) + ", AQI: " + str(aqi))

                set_led_from_aqi(aqi)

                sleep(FETCH_INTERVAL_SECONDS)
            else:
                set_led_error()
                sleep(FETCH_INTERVAL_SECONDS_ON_ERROR)
        else:
            print("Wireless network disconnected.")
            set_led_error()
            wlan = connect_wlan()


if __name__ == "__main__":
    main_loop()

