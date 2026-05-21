# 🚖 NYC Taxi Trip Data Pipeline 2025

## 📝 Deskripsi Proyek
Pipeline analisis data NYC TLC Trip Record Dataset (Jan–Jun 2025)
untuk mengidentifikasi zona operasi paling menguntungkan dan 
pengaruh jam sibuk terhadap durasi perjalanan.

## 🏗️ Arsitektur Sistem
Raw Data → Ingestion → Preprocessing → Analysis → Prediction → Dashboard

## 📂 Struktur Folder Proyek
```bash
.
├── data/
│   └── nyc-taxi.db
├── orchestration/          # Prefect flows & deployment
├── pipeline/
│   ├── 01_ingestion/       # Script wget/fetching
│   ├── 02_preprocessing/   # Cleaning & transformation
│   ├── 03_storage/         # Database schema & loading
│   ├── 04_analysis/        # Business logic & KPIs
│   └── 05_dashboard/       # Streamlit dashboard
├── requirements.txt
└── .env.example            # Template untuk environment variables
```
___

## 🚀 Cara Menjalankan

Ikuti langkah-langkah di bawah ini untuk menyiapkan lingkungan pengembangan dan menjalankan pipeline data.

### 1. Persiapan Awal
Pastikan kamu sudah meng-clone repository ini ke komputer lokal:
`git clone [https://github.com/clarestarahma/nyc-taxi.git]`
`cd nyc-taxi`

### 2. Instalasi Tools Prasyarat
- Install `uv` `(https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)`
- Install `just` `(https://github.com/casey/just)`

### 3. Masuk ke direktori proyek
`cd nyc-taxi`

### 4. Install Dependensi
Gunakan perintah `uv sync` untuk menginstall seluruh dependensi pada proyek ini

### 5. Setup & Ingestion
Gunakan perintah `just setup` untuk setup virtual environment dan install dependencies
Gunakan perintah `just run-all` untuk menjalankan seluruh proses
Setelah serluruh proses dijalankan, gunakan perintah `just run` atau `just dashboard run` untuk menjalankan dashboard

## Proyek ini telah di deploy dan dapat dibuka pada link berikut:
### [Proyek-Akhir-RDV-5](https://nyc-taxi-rdv5.streamlit.app/)

___

## 👥 Struktur Tim & Tanggung Jawab 
| Nama | Tugas |
|------|-------|
| A    | Ingestion |
| B    | Preprocessing |
| C    | Analisis & Dashboard |
| D    | Prediksi & Dashboard |
---
## 💡 Strategi Branch
Supaya tidak bentrok antar anggota tim:
```
main          ← branch utama, hanya merge kalau sudah selesai
├── dev       ← branch development bersama
│   ├── feature/ingestion
│   ├── feature/preprocessing
│   ├── feature/storage
│   ├── feature/dashboard
│   └── feature/clustering  ← branch ML, dikerjakan belakangan
```

## 👩‍💻👨‍💻 Cara Kerja
1. `git checkout dev` -> pindah ke branch dev
2. `git checkout -b feature/ingestion` -> buat branch untuk fitur yang mau dibuat
3. `git push origin feature/ingestion` -> push ke branch di github untuk di review


## 📋 Pembagian Tugas & Struktur Proyek
| Anggota | Branch | Folder / Komponen | Tanggung Jawab Utama |
| :--- | :--- | :--- | :--- |
| **👑 A (Lead)** | `dev` | `orchestration/`<br>`README.md` | Arsitektur & Review PR |
| **📥 B** | `feature/ingestion` | `pipeline/01_ingestion/` | Automasi Ingestion |
| **🛠️ C** | `feature/preprocessing` | `pipeline/02_preprocessing/`<br>`pipeline/03_storage/` | ETL & Database |
| **📊 D** | `feature/dashboard` | `pipeline/04_analysis/`<br>`pipeline/05_dashboard/` | Analisis & Visualisasi |