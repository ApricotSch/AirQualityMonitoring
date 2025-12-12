import pandas as pd
import schedule
import time
import os
from sqlalchemy import create_engine, text


DB_URI = "postgresql://admin:password123@localhost:5432/iaq_monitoring"
CSV_FILE = "temp_data.csv"

def run_etl_process():
    print("\n--- Memulai Batch ETL Process ---")
    
    if not os.path.exists(CSV_FILE):
        print("Tidak ada data baru (File CSV kosong).")
        return

    try:

        df = pd.read_csv(CSV_FILE)
        
        if df.empty:
            print("File CSV ada tapi kosong.")
            return

        print(f"Extract: {len(df)} data mentah ditemukan.")

        df = df[
            (df['co2'].between(300, 5000)) &
            (df['temperature'].between(10, 40)) &
            (df['humidity'].between(0, 100)) &
            (df['pm25'].between(0, 300))
        ]
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        agg_df = df.groupby('room_id').agg({
            'co2': 'mean',
            'temperature': 'mean',
            'humidity': 'mean',
            'pm25': 'mean',
            'timestamp': 'max'
        }).reset_index()

        agg_df = agg_df.round(2)
        agg_df['co2'] = agg_df['co2'].astype(int)

        def get_status(row):
            notes = []
            if row['co2'] > 1000:
                notes.append("Ventilasi Buruk")
            if row['humidity'] < 30:
                notes.append("Udara Kering")
            if row['pm25'] > 15:
                notes.append("Tidak Sehat")
            
            return ", ".join(notes) if notes else "Normal"

        agg_df['status_ruangan'] = agg_df.apply(get_status, axis=1)

        print("Transform: Data berhasil diagregasi dan dilabeli.")
        print(agg_df[['room_id', 'co2', 'status_ruangan']].head())

        engine = create_engine(DB_URI)
        
        agg_df.to_sql('daily_logs', engine, if_exists='append', index=False)
        print("Load: Data berhasil disimpan ke Database.")

        os.remove(CSV_FILE)
        print("Cleanup: Buffer CSV telah dikosongkan.")

    except Exception as e:
        print(f"ETL Error: {e}")

schedule.every(1).minutes.do(run_etl_process)

print("Scheduler Berjalan. Menunggu Job tiap 1 menit (Demo Mode)...")

engine = create_engine(DB_URI)
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            room_id VARCHAR(50),
            timestamp TIMESTAMP,
            co2 INTEGER,
            temperature FLOAT,
            humidity FLOAT,
            pm25 FLOAT,
            status_ruangan TEXT
        );
    """))
    print("Database check: Tabel 'daily_logs' siap.")

while True:
    schedule.run_pending()
    time.sleep(1)