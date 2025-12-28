# Spark + Nessie + Iceberg ingestion walkthrough

This guide uses PySpark to write an Iceberg table tracked by Nessie. You can choose local filesystem storage or MinIO (S3-compatible).

## 1) Python environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pyspark requests
```

## 2) Choose your warehouse location
- Local disk (default): `file:/tmp/iceberg-warehouse`
- MinIO (S3-style): `s3a://iceberg-warehouse` (requires MinIO section from `03-local-stack`)

## 3) Start a Spark session with Nessie + Iceberg
Key pieces:
- `spark.sql.extensions` loads Iceberg extensions.
- `spark.sql.catalog.nessie` defines a catalog named `nessie` using the Nessie Iceberg catalog implementation.
- `spark.sql.catalog.nessie.uri` points to the Nessie REST endpoint.
- `spark.sql.catalog.nessie.ref` selects the active branch (`main` by default).
- `spark.sql.catalog.nessie.warehouse` points Iceberg to where data/metadata files go (filesystem or MinIO).

```python
from pyspark.sql import SparkSession

NESSIE_URI = "http://localhost:19120/api/v2"
WAREHOUSE = "file:/tmp/iceberg-warehouse"  # or "s3a://iceberg-warehouse"

spark = (
    SparkSession.builder.appName("nessie-iceberg-demo")
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.nessie.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog")
    .config("spark.sql.catalog.nessie.uri", NESSIE_URI)
    .config("spark.sql.catalog.nessie.ref", "main")
    .config("spark.sql.catalog.nessie.authentication.type", "NONE")
    .config("spark.sql.catalog.nessie.warehouse", WAREHOUSE)
    .config(
        "spark.jars.packages",
        ",".join([
            "org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.4.3",
            "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.4_2.12:0.79.0",
        ]),
    )
    # Only if using MinIO/S3A:
    # .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
    # .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
    # .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
    # .config("spark.hadoop.fs.s3a.path.style.access", "true")
    # .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .getOrCreate()
)
```

### Switching branches/tags in Spark
- Set at session build time: `.config("spark.sql.catalog.nessie.ref", "feature/my-branch")`
- Or change in-session: `spark.conf.set("spark.sql.catalog.nessie.ref", "feature/my-branch")`
- Tags work the same way: set the ref to the tag name to read a pinned snapshot.
- Every read/write through the `nessie` catalog uses the currently set `ref`.

## 4) Ingest data from an open API (Open-Meteo)
This example fetches current weather for a few cities and writes to an Iceberg table.

```python
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

spark = SparkSession.getActiveSession()

cities = {
    "paris": (48.8566, 2.3522),
    "new_york": (40.7128, -74.0060),
    "singapore": (1.3521, 103.8198),
}

rows = []
for name, (lat, lon) in cities.items():
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": lat, "longitude": lon, "current_weather": True},
        timeout=10,
    )
    resp.raise_for_status()
    current = resp.json()["current_weather"]
    rows.append((name, lat, lon, float(current["temperature"]), float(current["windspeed"]), current["time"]))

df = spark.createDataFrame(
    rows,
    schema="city string, lat double, lon double, temperature_c double, windspeed_kmh double, obs_time string",
).withColumn("ingest_ts", lit(spark.sql("select current_timestamp()").collect()[0][0]))

# Create table (if missing) and append rows
spark.sql("""
CREATE TABLE IF NOT EXISTS nessie.demo_weather (
  city string,
  lat double,
  lon double,
  temperature_c double,
  windspeed_kmh double,
  obs_time string,
  ingest_ts timestamp
) USING ICEBERG
""")

df.writeTo("nessie.demo_weather").append()
spark.sql("SELECT * FROM nessie.demo_weather").show()
```

What happens here:
- Iceberg writes data/metadata files to your warehouse (local FS or MinIO).
- Nessie records the new Iceberg metadata pointer as a commit on branch `main`.
- You can now branch/tag with the `pynessie` CLI or Spark config (`spark.sql.catalog.nessie.ref`).

## 5) Quick Nessie operations
- List branches: `nessie branch list`
- Create a feature branch: `nessie branch create feature/test -r main`
- Point Spark to that branch: set `spark.sql.catalog.nessie.ref=feature/test`
- Merge back to main: `nessie merge feature/test -b main`

## 6) Troubleshooting
- Spark cannot load catalog: ensure `spark.jars.packages` versions match your Spark version (examples are for Spark 3.4, Scala 2.12).
- Connection errors: check Nessie port 19120 and your `NESSIE_URI`.
- MinIO issues: verify bucket exists, endpoint is `http://localhost:9000`, and `spark.hadoop.fs.s3a.*` settings are present.
- Inspect table history: `spark.sql("CALL nessie.system.snapshot_history('nessie.demo_weather')").show(truncate=False)`

## 7) Cleanup
- Stop services: `docker stop nessie` (and `docker compose down` for MinIO).
- Delete local state if you want a clean slate: `docker volume rm nessie_data minio_data` and remove the warehouse directory or MinIO bucket.
