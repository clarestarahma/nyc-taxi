# NYC Taxi Trip Data Pipeline

## Deskripsi
Pipeline analisis data NYC TLC Trip Record Dataset (Jan–Jun 2025)
untuk mengidentifikasi zona operasi paling menguntungkan dan 
pengaruh jam sibuk terhadap durasi perjalanan.

## Arsitektur
Raw Data → Ingestion → Preprocessing → DuckDB/Parquet → Dashboard

## Cara Menjalankan
1. Install dependencies: `pip install -r requirements.txt`
2. Jalankan pipeline: `python orchestration/prefect_flow.py`
3. Jalankan dashboard: `streamlit run pipeline/05_dashboard/app.py`

## Tim
| Nama | Tugas |
|------|-------|
| A    | Ingestion |
| B    | Preprocessing & Storage |
| C    | Analisis & Dashboard |
```

---

## 4. Strategi Branch

Supaya tidak bentrok antar anggota tim:
```
main          ← branch utama, hanya merge kalau sudah selesai
├── dev       ← branch development bersama
│   ├── feature/ingestion
│   ├── feature/preprocessing
│   ├── feature/storage
│   ├── feature/dashboard
│   └── feature/clustering  ← branch ML, dikerjakan belakangan