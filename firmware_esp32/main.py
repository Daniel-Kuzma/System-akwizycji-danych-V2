# MicroPico: Initialize MicroPico project
from machine import Pin, I2C, deepsleep, reset 
import json
import time 
import network
import sys
import os
import socket
from umqtt.simple import MQTTClient

# plik z funkcjami
from main_functions import web_page, save_config, load_config, file_exists, wifi_connect, error_blinking
# biblioteka do obsługi czujnika
import sht31

# # implementacja czujników i ustawienie ich stanów
dioda = Pin(15, Pin.OUT) # dioda 
button = Pin(9, Pin.IN, Pin.PULL_UP) # przycisk
# button = Pin(4, Pin.IN, Pin.PULL_UP) # przycisk

# implementacja czujnika i magistrali i2c do odczytu danych
i2c = I2C(scl=Pin(20), sda=Pin(19), freq=400000) 
sensor = sht31.SHT31(i2c, addr=0x44)

time.sleep(2)
#stan początkowy diody na ON
dioda.value(0)

# ten fragment kodu służy do resetowania ustawieni płytki przed konfiguracją wifi i url
# jeżeli uzytkownik przytrzyma przycisk przez 3 sekundy płytka sie resetuje
i = 0
if button.value() == 0:
    is_pressed = True
    while is_pressed:
        i+=1
        time.sleep(1)
        if i > 3 or button.value() == 1:
            break    
if i > 3:
    try:
        os.remove("config.json")
        error_blinking(dioda, 0.5, 4)
        reset()            
    except:
        pass


if not file_exists("config.json"):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='Thermometer WIFI', password='admin1234',  security=network.AUTH_WPA2_PSK)
    time.sleep(1)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('',80))
    s.listen(5)
    while True:
        try:
            conn, addr = s.accept()
            print(f'\nUrządzenie połączyło się ze stroną: {addr}')
            
            request = conn.recv(4096)
            response_html = web_page()
            request_str = request.decode("utf-8")
            
            if "POST /" in request_str:
                linie = request_str.split("\r\n")
                dane_post = linie[-1]
                dane_split = dane_post.split("&")
                config_list = []
                for x in dane_split:
                    index = x.find("=")
                    config_list.append(x[index+1:])
                save_config(config_list[0], config_list[1], config_list[2])
                is_contected = wifi_connect(config_list[0], config_list[1])
                if is_contected:
                    ap.disconnect()
                    s.close()
                    break
                
            # 1. Konwersja na bajty PRZED wysłaniem nagłówków, aby poznać rozmiar
            html_bytes = response_html.encode('utf-8')
            
            # 2. Wysyłanie nagłówków z kluczowym parametrem Content-Length
            conn.sendall(b'HTTP/1.1 200 OK\r\n')
            conn.sendall(b'Content-Type: text/html; charset=utf-8\r\n')
            conn.sendall(f'Content-Length: {len(html_bytes)}\r\n'.encode('utf-8'))
            conn.sendall(b'Connection: close\r\n\r\n')
            
            # 3. Wysłanie całego kodu HTML (sendall samo dzieli plik na mniejsze fragmenty)
            conn.sendall(html_bytes)
            
            time.sleep(0.2) 
            conn.close()
        except Exception as e:
            print("Wystąpił błąd:", e)

try_to_read_config = load_config() # próba odczytu ustawieni konfiguracyjnych
if try_to_read_config:
    ssid = try_to_read_config["ssid"]
    haslo = try_to_read_config["haslo"]
    token = try_to_read_config["token"]
else:
    reset()

if wifi_connect(ssid, haslo):
    dioda.value(1)
else:
    reset()

print("Połączono z wifi ")

client = MQTTClient("client", "192.168.0.105")
client.connect()
print("Połączono z brokerem")
time.sleep(2)

try:
    # pobranie temperatury i wilgotność 
    temp, humi = sensor.get_temp_humi() 
    # zapisanie do zmiennej
    data = {
        "token" : token,
        "odczyt_temperatury" : temp,
        "odczyt_wilgotnosc" : humi,
    }
    client.publish("Temperature", json.dumps(data).encode("utf-8"))
    print("Wysłano dane")
    dioda.value(0)
    time.sleep(2) 
    client.disconnect()
except Exception as e:
    print(e)

deepsleep(120000)


