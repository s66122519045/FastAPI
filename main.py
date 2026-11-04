import csv
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Zoo Visitors API",
    description="สถิติผู้เข้าชมสวนสัตว์จากไฟล์ CSV ของ Data.go.th ปีงบประมาณ 2569",
    version="1.0.0",
)

DATASET_URL = "https://data.go.th/dataset/zoo-visitors2569"
CSV_CANDIDATES = [
    Path(__file__).with_name("zoo_visitors_january_2569.csv"),
    Path(__file__).parent / "outputs" / "zoo_visitors_january_2569.csv",
]


def load_records() -> list[dict[str, Any]]:
    csv_path = next((path for path in CSV_CANDIDATES if path.is_file()), None)
    if csv_path is None:
        raise HTTPException(
            status_code=500,
            detail="ไม่พบไฟล์ zoo_visitors_january_2569.csv ให้วางไฟล์ไว้ข้าง main.py",
        )

    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            records = []
            for row in reader:
                cleaned: dict[str, Any] = {}
                for key, value in row.items():
                    if key is None or not key.strip():
                        continue
                    value = (value or "").strip()
                    normalized = value.replace(",", "")
                    if normalized.isdigit():
                        cleaned[key.strip()] = int(normalized)
                    else:
                        cleaned[key.strip()] = value or None
                if any(value is not None for value in cleaned.values()):
                    records.append(cleaned)
            return records
    except (OSError, UnicodeError, csv.Error) as exc:
        raise HTTPException(status_code=500, detail=f"อ่านไฟล์ CSV ไม่สำเร็จ: {exc}") from exc


@app.get("/api/zoo-visitors", tags=["Zoo visitors"])
def get_zoo_visitors() -> dict[str, Any]:
    records = load_records()
    return {
        "source": "Data.go.th - Open Government Data of Thailand",
        "dataset": "ข้อมูลรายงานสถิติจำนวนผู้เข้าชมสวนสัตว์ ปีงบประมาณ 2569",
        "dataset_url": DATASET_URL,
        "fiscal_year": 2569,
        "resource": "ข้อมูลรายงานสถิติจำนวนผู้เข้าชมสวนสัตว์ อสส มกราคม 2569",
        "records_count": len(records),
        "records": records,
    }


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "Zoo Visitors API", "docs": "/docs", "data": "/api/zoo-visitors"}
