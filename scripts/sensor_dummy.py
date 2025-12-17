import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime


BROKER = "localhost"
PORT = 1883

ROOMS = ["Room_A", "Room_B", "Room_C", "Room_D", "Room_E"] 

def generate_sensor_data(room_name):

    temp_base = 18.0 if room_name == "Room_A" else 23.0
    
    data = {
        "room_id": room_name,
        "timestamp": datetime.now().isoformat(),
        "co2": random.randint(400, 1400),
        "temperature": round(random.uniform(temp_base - 2, temp_base + 2), 4),
        "humidity": round(random.uniform(10.0, 80.0), 2),
        "pm25": round(random.uniform(0.0, 25.0), 2)
    }
    return data


client = mqtt.Client("Dummy_Multi_Sensor")

try:
    print("Menghubungkan ke Broker...")
    client.connect(BROKER, PORT, 60)
    
    print(f"Memulai simulasi untuk ruangan: {ROOMS}")
    
    while True:

        for room in ROOMS:
            topic = f"kantor/sensor/{room.lower()}" 
            

            payload = generate_sensor_data(room)
            

            client.publish(topic, json.dumps(payload))
            print(f"[{room}] Data Terkirim: {payload['co2']} ppm, {payload['temperature']} C")
        
        print("--- Menunggu siklus berikutnya ---")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nSimulasi dihentikan.")
    client.disconnect()