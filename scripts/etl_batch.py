import pandas as pd
import schedule
import time
import os
from sqlalchemy import create_engine, text

# Konfigurasi Database (Sesuai docker-compose.yml)
DB_URI = "postgresql://admin:password123@localhost:5432/iaq_monitoring"
CSV_FILE = "temp_data.csv"

def run_etl_process():
    print("\n--- Memulai Batch ETL Process ---")
    
    if not os.path.exists(CSV_FILE):
        print("Tidak ada data baru (File CSV kosong).")
        return

    try:
        # 1. EXTRACT: Baca data dari buffer CSV
        df = pd.read_csv(CSV_FILE)
        
        if df.empty:
            print("File CSV ada tapi kosong.")
            return

        print(f"Extract: {len(df)} data mentah ditemukan.")

        # 2. TRANSFORM
        # A. Validasi Range & Cleaning (Bab 5.1 & 5.2)
        # Hapus data yang tidak masuk akal (Outlier/Error Sensor)
        df = df[
            (df['co2'].between(300, 5000)) &
            (df['temperature'].between(10, 40)) &
            (df['humidity'].between(0, 100)) &
            (df['pm25'].between(0, 300))
        ]
        
        # Convert timestamp ke datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # B. Agregasi per Ruangan (Rata-rata per Batch)
        # Kita ambil rata-rata parameter numeric, tapi timestamp ambil yang terakhir
        agg_df = df.groupby('room_id').agg({
            'co2': 'mean',
            'temperature': 'mean',
            'humidity': 'mean',
            'pm25': 'mean',
            'timestamp': 'max' # Waktu batch terakhir
        }).reset_index()

        # Pembulatan biar rapi
        agg_df = agg_df.round(2)
        agg_df['co2'] = agg_df['co2'].astype(int)

        # C. Labeling (Bab 4.2 Transform)
        def get_status(row):
            notes = []
            if row['co2'] > 1000:
                notes.append("Ventilasi Buruk")
            if row['humidity'] < 30:
                notes.append("Udara Kering")
            if row['pm25'] > 35:
                notes.append("Tidak Sehat")
            
            return ", ".join(notes) if notes else "Normal"

        agg_df['status_ruangan'] = agg_df.apply(get_status, axis=1)

        print("Transform: Data berhasil diagregasi dan dilabeli.")
        print(agg_df[['room_id', 'co2', 'status_ruangan']].head())

        # 3. LOAD: Masukkan ke Database PostgreSQL
        engine = create_engine(DB_URI)
        
        # Simpan ke tabel 'daily_logs'. 'append' berarti nambah terus.
        agg_df.to_sql('daily_logs', engine, if_exists='append', index=False)
        print("Load: Data berhasil disimpan ke Database.")

        # 4. CLEANUP: Hapus isi CSV agar siap untuk batch berikutnya
        os.remove(CSV_FILE)
        print("Cleanup: Buffer CSV telah dikosongkan.")

    except Exception as e:
        print(f"ETL Error: {e}")

# --- SCHEDULER ---
# Di laporan tiap 15 menit. Untuk demo kita buat tiap 1 menit saja biar cepat kelihatan hasilnya.
# Ganti .minutes.do() jadi .minutes.do() sesuai kebutuhan.
schedule.every(1).minutes.do(run_etl_process)

print("Scheduler Berjalan. Menunggu Job tiap 1 menit (Demo Mode)...")

# Setup Awal: Bikin Tabel di DB kalau belum ada
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