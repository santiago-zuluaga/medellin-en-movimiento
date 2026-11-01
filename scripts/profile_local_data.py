#!/usr/bin/env python3
"""Perfilado inicial de archivos CSV, Parquet y GeoJSON locales.

Uso:
  python scripts/profile_local_data.py data/raw/archivo.csv
  python scripts/profile_local_data.py data/raw/
"""
from pathlib import Path
import sys, json, hashlib
import pandas as pd

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load(path):
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, low_memory=False)
    if suffix in (".parquet", ".pq"):
        return pd.read_parquet(path)
    if suffix in (".json", ".geojson"):
        obj = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(obj, dict) and obj.get("type") == "FeatureCollection":
            rows = []
            for feat in obj.get("features", []):
                row = dict(feat.get("properties") or {})
                row["_geometry_type"] = (feat.get("geometry") or {}).get("type")
                rows.append(row)
            return pd.DataFrame(rows)
        return pd.json_normalize(obj)
    raise ValueError(f"Formato no soportado: {suffix}")

def profile(path):
    try:
        df = load(path)
    except Exception as e:
        print(f"\n## {path}\nERROR de lectura: {e}")
        return
    print(f"\n## {path}")
    print(f"Filas: {len(df):,} | Columnas: {len(df.columns)}")
    print(f"SHA256: {sha256(path)}")
    print("\nTipos:")
    print(df.dtypes.to_string())
    print("\nNulos (%):")
    print((df.isna().mean().mul(100).round(2)).sort_values(ascending=False).to_string())
    print(f"\nDuplicados exactos: {df.duplicated().sum():,}")
    print("\nCardinalidad:")
    print(df.nunique(dropna=True).sort_values(ascending=False).to_string())
    print("\nMuestra:")
    print(df.head(5).to_string(index=False, max_cols=30))
    date_cols = [c for c in df.columns if any(k in c.lower() for k in ("fecha", "date"))]
    for col in date_cols:
        parsed = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
        valid = parsed.dropna()
        if len(valid):
            print(f"\nRango parseable {col}: {valid.min()} — {valid.max()} ({len(valid):,}/{len(df):,} parseables)")

def main(arg):
    p = Path(arg)
    paths = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.suffix.lower() in (".csv", ".parquet", ".pq", ".json", ".geojson"))
    if not paths:
        print("No se encontraron archivos compatibles.")
    for item in paths:
        profile(item)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python scripts/profile_local_data.py <archivo-o-directorio>")
    main(sys.argv[1])
