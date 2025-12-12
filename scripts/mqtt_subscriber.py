import paho.mqtt.client as mqtt
import json
import csv
import os

BROKER = "localhost"
TOPIC = "kantor/sensor/+"
CSV_FILE = "temp_data.csv"

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Data diterima: {payload}")
        
        file_exists = os.path.isfile(CSV_FILE)
        
        with open(CSV_FILE, mode='a', newline='') as file:
            fieldnames = ['room_id', 'timestamp', 'co2', 'temperature', 'humidity', 'pm25']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(payload)
            
    except Exception as e:
        print(f"Error processing data: {e}")

client = mqtt.Client("Subscriber_Buffer")
client.on_message = on_message

print("Menghubungkan ke Broker...")
client.connect(BROKER, 1883, 60)

client.subscribe(TOPIC)
print(f"Mendengarkan topic: {TOPIC}...")
print(f"Data akan disimpan sementara di {CSV_FILE}")

client.loop_forever()