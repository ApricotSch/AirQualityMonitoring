import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime

# --- KONFIGURASI ---
BROKER = "localhost"
PORT = 1883
# Kita ubah jadi List agar bisa banyak ruangan
ROOMS = ["Room_A", "Room_B"] 

# --- FUNGSI GENERATE DATA DUMMY ---
def generate_sensor_data(room_name):
    # Kita bikin sedikit variasi biar datanya gak kembar identik
    # Misal: Room B ceritanya lebih panas dikit
    temp_base = 25.0 if room_name == "Room_A" else 28.0
    
    data = {
        "room_id": room_name,
        "timestamp": datetime.now().isoformat(),
        "co2": random.randint(300, 1200),
        "temperature": round(random.uniform(temp_base - 2, temp_base + 2), 2),
        "humidity": round(random.uniform(40.0, 80.0), 2),
        "pm25": round(random.uniform(0.0, 50.0), 2)
    }
    return data

# --- MQTT SETUP ---
client = mqtt.Client("Dummy_Multi_Sensor")

try:
    print("Menghubungkan ke Broker...")
    client.connect(BROKER, PORT, 60)
    
    print(f"Memulai simulasi untuk ruangan: {ROOMS}")
    
    while True:
        # Loop untuk mengirim data setiap ruangan satu per satu
        for room in ROOMS:
            topic = f"kantor/sensor/{room.lower()}" # misal: kantor/sensor/room_a
            
            # 1. Generate data
            payload = generate_sensor_data(room)
            
            # 2. Kirim ke MQTT
            client.publish(topic, json.dumps(payload))
            print(f"[{room}] Data Terkirim: {payload['co2']} ppm, {payload['temperature']} C")
        
        print("--- Menunggu siklus berikutnya ---")
        # Tunggu 5 detik sebelum kirim paket data berikutnya
        time.sleep(5)

except KeyboardInterrupt:
    print("\nSimulasi dihentikan.")
    client.disconnect()