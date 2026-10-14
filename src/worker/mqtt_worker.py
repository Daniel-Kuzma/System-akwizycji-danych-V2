import time
import paho.mqtt.client as mqtt

mqtt_broker = "localhost" # Adres brokera. Ponieważ skrypt działa tam gdzie Mosquitto, localhost jest ok.

# Funkcja wywoływana za każdym razem, gdy przyjdzie nowa wiadomość
def on_message(client, userdata, msg):
    temat = msg.topic
    # Payload jest w postaci bajtów (b"11"), trzeba to zdekodować do zwykłego tekstu
    wartosc = msg.payload.decode('utf-8') 
    print(f"Otrzymano: {temat} -> {wartosc}")

client = mqtt.Client(client_id="User_PC")
client.on_message = on_message # Przypisanie funkcji do klienta

client.connect(mqtt_broker)
print("Server is up, nasłuchuje...")

client.loop_start()
client.subscribe("Temperature")


while True:
    time.sleep(1)
