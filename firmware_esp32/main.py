# MicroPico: Initialize MicroPico project
from machine import Pin, unique_id, I2C, deepsleep, reset 
import json
import time 
# autorska biblioteka do obsługi czujnika
import sht31
import ubinascii
import network
import sys
import urequests
import os

from umqtt.simple import MQTTClient

# # implementacja czujników i ustawienie ich stanów
dioda = Pin(15, Pin.OUT) # dioda 
button = Pin(9, Pin.IN, Pin.PULL_UP) # przycisk

# implementacja czujnika i magistrali i2c do odczytu danych
i2c = I2C(scl=Pin(20), sda=Pin(19), freq=400000) 
sensor = sht31.SHT31(i2c, addr=0x44)

#stan początkowy diody na ON
dioda.value(1)

# funkcja do obsługi migania diodą na płytce 
def error_blinking(diode, blinking_frequency, how_many_cycle ):
    for x in range(how_many_cycle):
        diode.value(1)
        time.sleep(blinking_frequency)
        diode.value(0)
        time.sleep(blinking_frequency)
    diode.value(1)

# # funkcja do zapisu uzyskanego ssid, hasła, url i tokena gdzie maja byc postowane wyniki z czujnika (w pamieci)
# def save_config(ssid, haslo, url, token):
#     data = {
#         "ssid" : ssid,
#         "haslo" : haslo,
#         "url" : url,
#         "token" : token,
#     }
#     with open("config.json", "w") as config:
#         json.dump(data, config)

# funkcja do wczytywanie danych di konfiguracji (ssid, password, url) jeżeli istnieją w pamięci
# def load_config():
#     try:
#         with open("config.json", "r") as config:
#             return json.load(config)
#     except:
#         return None

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


# ##########
# # ten fragment kodu służy do resetowania ustawieni płytki przed konfiguracją wifi i url
# # jeżeli uzytkownik przytrzyma przycisk przez 3 sekundy płytka sie resetuje
# time.sleep(2)
# i = 0
# if button.value() == 0:

#     is_pressed = True
#     while is_pressed:
#         i+=1
#         time.sleep(1)
#         if i > 3 or button.value() == 1:
#             break      
        
# if i > 3:
#     try: 
#         os.remove("config.json")
#         error_blinking(dioda, 0.5, 4)
#         reset()            
#     except:
#         pass
#########

# try_to_read_config = load_config() # próba odczytu ustawieni konfiguracyjnych 
# if try_to_read_config == None: # jezeli jest brak ustawieni w pamieci przechodzi w tryb konfiguracji
#     pass
# else: # jeżeli nie to pobiera parametry ustawieni z pamięci
#     ssid = try_to_read_config["ssid"]
#     haslo = try_to_read_config["haslo"]
#     url = try_to_read_config["url"]
#     token = try_to_read_config["token"]



# łączeni sie płytki z wifi
ssid = "ZTE_5D4804"
haslo = "2LS686RD68"
while not wifi_connect(ssid, haslo):
    error_blinking(dioda, 1, 1)
print("Połączono z wifi ")

client = MQTTClient("client", "192.168.0.105")
client.connect()
print("Połączono z brokerem")

while True:
    temp, humi = sensor.get_temp_humi() # pobranie temperatury i wilgotność 
        
    # zapisanie do zmiennej
    data = {
        "token" : "8e8bf79e-5008-453f-b5cf-b2fb047f7360.6119e5cb3e6014b6",
        "odczyt_temperatury" : temp,
        "odczyt_wilgotnosc" : humi,
    }
    client.publish("Temperature", json.dumps(data).encode("utf-8"))
    print("Wysłano dane")
    time.sleep(60)



# funkcja do wysyłania pobranych danych 
# while True:
#     try:
#         temp, humi = sensor.get_temp_humi() # pobranie temperatury i wilgotność 
        
#         # zapisanie do zmiennej
#         data = {
#             "odczyt_temperatury" : temp,
#             "odczyt_wilgotnosc" : humi,
#             "token" : token, 
#         }

#         json_data = json.dumps(data) # zapisanie zmiennych w formacie JSON  
#         naglowki = {'Content-Type': 'application/json'}
#         urequests.post(url, json=data, headers=naglowki) # POST na API 

#     except Exception as e:
#         print(e)
    
#     time.sleep(1)
#     deepsleep(120000) # głebokie uspienie na 2 min 


