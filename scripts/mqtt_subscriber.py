import paho.mqtt.client as mqtt
import json
import csv
import os

# Konfigurasi
BROKER = "localhost"
TOPIC = "kantor/sensor/+"  # Tanda '+' berarti terima dari semua ruangan
CSV_FILE = "temp_data.csv"

# Fungsi saat ada pesan masuk
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Data diterima: {payload}")
        
        # Simpan ke CSV
        file_exists = os.path.isfile(CSV_FILE)
        
        with open(CSV_FILE, mode='a', newline='') as file:
            fieldnames = ['room_id', 'timestamp', 'co2', 'temperature', 'humidity', 'pm25']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Tulis header jika file baru dibuat
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(payload)
            
    except Exception as e:
        print(f"Error processing data: {e}")

# Setup MQTT
client = mqtt.Client("Subscriber_Buffer")
client.on_message = on_message

print("Menghubungkan ke Broker...")
client.connect(BROKER, 1883, 60)

# Subscribe
client.subscribe(TOPIC)
print(f"Mendengarkan topic: {TOPIC}...")
print(f"Data akan disimpan sementara di {CSV_FILE}")

client.loop_forever()