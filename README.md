# Indoor Air Quality (IAQ) Monitoring System 🌬️🏢

Sistem pemantauan kualitas udara dalam ruangan berbasis IoT dan Batch Processing. Proyek ini dirancang untuk memantau parameter kesehatan udara kantor seperti CO2, Temperatur, Kelembapan, dan PM2.5 guna menjaga produktivitas dan kesehatan penghuni ruangan.

## Anggota Kelompok
- Muhammad Farkhan Fadillah 235150300111016
- Arbi Yusuf Ramanda 235150300111022
- Alif Eriksandi Agustino 235150300111023
- Maulana Ihsan Maggio 235150301111025

## 📋 Daftar Isi
- [📖 Latar Belakang]
- [🏗 Arsitektur Sistem]
- [🛠 Teknologi yang Digunakan]
- [📂 Struktur Folder]
- [🖥️ Cara Instalasi & Menjalankan]
- [📊 Konfigurasi Grafana]

## 📖 Latar Belakang
Kualitas udara dalam ruangan (IAQ) memiliki dampak besar terhadap kesehatan dan kognitif. Kadar CO2 > 1000 ppm dapat menurunkan fokus kerja. Sistem ini menggunakan pendekatan **Batch Processing** (ETL) karena perubahan kualitas udara kantor cenderung lambat, sehingga streaming real-time tidak diwajibkan, membuat sistem lebih efisien sumber daya.

## 🏗 Arsitektur Sistem
Sistem ini mensimulasikan alur data *End-to-End* dari sensor hingga visualisasi:

1.  **Data Producer (Sensor Dummy):** Python script menghasilkan data dummy untuk beberapa ruangan (`Room_A`, `Room_B`, `Room_C`, `Room_D`, `Room_E`) dan mengirimkannya via protocol **MQTT**.
2.  **Broker (Mosquitto):** Menampung pesan dari sensor.
3.  **Buffer (Subscriber):** Script Python yang "mendengarkan" broker dan menyimpan data sementara ke file CSV (`temp_data.csv`).
4.  **ETL Processor:** Batch job (dijadwalkan tiap 15 menit/1 menit demo) yang melakukan:
    * **Extract:** Ambil data dari CSV.
    * **Transform:** Validasi range, agregasi rata-rata, dan labeling status (misal: "Ventilasi Buruk").
    * **Load:** Simpan data bersih ke Database PostgreSQL.
5.  **Visualization:** **Grafana** membaca data dari PostgreSQL untuk ditampilkan dalam bentuk grafik Time-Series dan status Gauge.

## 🛠 Teknologi yang Digunakan
* **Bahasa:** Python 3.9+
* **Protokol:** MQTT (Paho-MQTT)
* **Containerization:** Docker & Docker Compose
* **Database:** PostgreSQL
* **Dashboard:** Grafana
* **Library:** Pandas, SQLAlchemy, Schedule

## 📂 Struktur Folder
```text
IAQ_Monitoring_System/
│
├── docker-compose.yml         # Konfigurasi Infrastruktur (DB, Broker, Grafana)
├── requirements.txt           # Dependency Python
├── README.md                  # Dokumentasi ini
│
├── scripts/                   # Source Code Python
│   ├── sensor_dummy.py        # Simulasi Sensor IoT
│   ├── mqtt_subscriber.py     # Penampung Data Sementara
│   └── etl_batch.py           # Proses ETL & Scheduler
│
└── mosquitto/                 # Konfigurasi MQTT
    └── config/
        └── mosquitto.conf
```

## 🖥️ installasi
**Prasyarat**
* Python 3.x terinstall.
* Docker & Docker Desktop terinstall dan berjalan.

### 1. Clone & Setup Environment
Clone repository ini dan install library Python yang dibutuhkan:

```
git clone https://github.com/ApricotSch/AirQualityMonitoring.git
cd AirQualityMonitoring
pip install -r requirements.txt
```

### 2. Jalankan Infrastruktur (Docker)
Jalankan Mosquitto, PostgreSQL, dan Grafana dalam container:
```
docker-compose up -d
```
Tunggu beberapa saat hingga semua container berstatus "Running".

### 3. Jalankan Komponen Sistem
Sistem ini membutuhkan 3 terminal terpisah agar berjalan paralel:

#### Terminal 1: Subscriber (Buffer) Menangkap data dari MQTT.
```
python scripts/mqtt_subscriber.py
```

#### Terminal 2: ETL Scheduler Memproses data setiap interval waktu (Default: 1 menit untuk demo).
```
python scripts/etl_batch.py
```

#### Terminal 3: Dummy Sensor Mengirim data simulasi.
```
python scripts/sensor_dummy.py
```

## 📊 Konfigurasi Grafana
1. Koneksi Database
* **Buka browser**: `http://localhost:3000`
* **Login default**: `admin` / `admin`.
* **Masuk ke Connections -> Add Data Source -> PostgreSQL.**
* **Isi konfigurasi berikut (sesuai docker-compose):**
  * **Host**: `postgres:5432` (PENTING: Jangan pakai localhost)
  * **Database**: `iaq_monitoring`
  * **User**: `admin`
  * **Password**: `password123`
  * **TLS/SSL Mode**: `disable`
* klik **Save & Test**.

2. Import Dashboard Otomatis
Agar tidak perlu membuat grafik manual, gunakan file JSON yang sudah disediakan:

* Buka file GrafanaJson.json yang ada di repository ini, lalu Copy seluruh isinya.
* Di Grafana, klik menu Dashboards -> New -> Import.
* Paste kode JSON ke dalam kotak Import via panel json.
* Klik Load.
* Pada bagian Select a PostgreSQL data source, pilih data source yang baru saja dibuat.
* Klik Import.
* Dashboard monitoring siap digunakan! 🚀
