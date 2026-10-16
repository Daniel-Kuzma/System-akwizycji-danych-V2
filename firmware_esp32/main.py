# MicroPico: Initialize MicroPico project
from machine import Pin, I2C, deepsleep, reset 
import json
import time 
import network
import sys
import os
import socket

# plik z funkcjami
from main_functions import web_page
# autorska biblioteka do obsługi czujnika
import sht31
from umqtt.simple import MQTTClient

# # implementacja czujników i ustawienie ich stanów
dioda = Pin(15, Pin.OUT) # dioda 
button = Pin(9, Pin.IN, Pin.PULL_UP) # przycisk

# implementacja czujnika i magistrali i2c do odczytu danych
i2c = I2C(scl=Pin(20), sda=Pin(19), freq=400000) 
sensor = sht31.SHT31(i2c, addr=0x44)

#stan początkowy diody na ON
dioda.value(1)



ap = network.WLAN(network.AP_IF)


ap.active(True)
ap.config(essid='ESP32-Moja-Siec', password='mojehaslo123',  security=network.AUTH_WPA2_PSK)
time.sleep(1)
print('Punkt dostępowy aktywny. Nazwa:', ap.config('essid'))
print('Adres IP płytki:', ap.ifconfig()[0])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('',80))
s.listen(5)

while True:
    try:
        conn, addr = s.accept()
        print(f'\nUrządzenie połączyło się ze stroną: {addr}')
        
        request = conn.recv(1024)
        response_html = web_page()
        
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        
        conn.sendall(response_html)
        conn.close()
    except Exception as e:
        print("Wystąpił błąd:", e)
        

# time.sleep(60)
# ap.disconnect(True)

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
# ssid = "ZTE_5D4804"
# haslo = "2LS686RD68"
# 
# while not wifi_connect(ssid, haslo):
#     error_blinking(dioda, 1, 1)
# print("Połączono z wifi ")
# 
# client = MQTTClient("client", "192.168.0.105")
# client.connect()
# print("Połączono z brokerem")
# 
# while True:
#     try:
#         # pobranie temperatury i wilgotność 
#         temp, humi = sensor.get_temp_humi() 
#         # zapisanie do zmiennej
#         data = {
#             "token" : "8e8bf79e-5008-453f-b5cf-b2fb047f7360.6119e5cb3e6014b6",
#             "odczyt_temperatury" : temp,
#             "odczyt_wilgotnosc" : humi,
#         }
#         client.publish("Temperature", json.dumps(data).encode("utf-8"))
#         print("Wysłano dane")
#         time.sleep(60)
#         # deepsleep(120000) # głebokie uspienie na 2 min
#     except Exception as e:
#         print(e)



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

