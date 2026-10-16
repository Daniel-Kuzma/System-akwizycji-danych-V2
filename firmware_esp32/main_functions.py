import json
import time
import network


# funkcja do obsługi migania diodą na płytce 
def error_blinking(diode, blinking_frequency, how_many_cycle ):
    for x in range(how_many_cycle):
        diode.value(1)
        time.sleep(blinking_frequency)
        diode.value(0)
        time.sleep(blinking_frequency)
    diode.value(1)
    
# funkcja do łączenia sie z wifi
def wifi_connect(ssid, password):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, password)
    timeout = 10
    while not wifi.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
    if wifi.isconnected():
        return True
    else:
        return False
    
# funkcja do zapisu uzyskanego ssid, hasła, url i tokena gdzie maja byc postowane wyniki z czujnika (w pamieci)
def save_config(ssid, haslo, url, token):
    data = {
        "ssid" : ssid,
        "haslo" : haslo,
        "url" : url,
        "token" : token,
     }
    with open("config.json", "w") as config:
        json.dump(data, config)

#  funkcja do wczytywanie danych di konfiguracji (ssid, password, url) jeżeli istnieją w pamięci
def load_config():
    try:
        with open("config.json", "r") as config:
            return json.load(config)
    except:
        return None
    
    
def web_page():
    html = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>ESP32 MicroPython AP</title>
    </head>
    <body>
        <h1>Hello z sieci ESP32!</h1>
    </body>
    </html>
    """
    return html