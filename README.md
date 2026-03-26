# 🚖 NYC Taxi Trip Data Pipeline 2025

## 📝 Deskripsi Proyek
Pipeline analisis data NYC TLC Trip Record Dataset (Jan–Jun 2025)
untuk mengidentifikasi zona operasi paling menguntungkan dan 
pengaruh jam sibuk terhadap durasi perjalanan.

## 🏗️ Arsitektur Sistem
Raw Data → Ingestion → Preprocessing → DuckDB/Parquet → Dashboard

## 📂 Struktur Folder Proyek
```bash
.
├── data/
│   ├── raw/                # Bronze Layer
│   ├── processed/          # Silver Layer
│   └── gold/               # Gold Layer (DuckDB files)
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

## 🚀 Cara Menjalankan
1. Install dependencies: `pip install -r requirements.txt`
2. ??
3. ??

## 👥 Struktur Tim & Tanggung Jawab 
| Nama | Tugas |
|------|-------|
| A    | Ingestion |
| B    | Preprocessing & Storage |
| C    | Analisis & Dashboard |
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