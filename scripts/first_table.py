"""
Create a demo Iceberg table tracked by Nessie, writing data into MinIO (or another S3A endpoint).

Configuration is read from environment variables (see .env.example). Requires:
  - pyspark 4.1.0 (already installed)
  - pydantic + pydantic-settings
  - Java 8+ available to Spark
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    nessie_uri: str = Field(default="http://localhost:19120/api/v2")
    nessie_branch: str = Field(default="main")
    warehouse: str = Field(default="s3a://iceberg-warehouse")
    s3_endpoint: str = Field(default="http://localhost:9000")
    s3_access_key: str = Field(default="minioadmin")
    s3_secret_key: str = Field(default="minioadmin")

    iceberg_pkg: str = Field(
        default="org.apache.iceberg:iceberg-spark-runtime-4.1_2.12:1.6.1"
    )
    nessie_pkg: str = Field(
        default="org.projectnessie.nessie-integrations:nessie-spark-extensions-4.1_2.12:0.79.0"
    )


def build_spark(settings: Settings) -> SparkSession:
    return (
        SparkSession.builder.appName("nessie-demo")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")
        .config(
            "spark.sql.catalog.nessie.catalog-impl",
            "org.apache.iceberg.nessie.NessieCatalog",
        )
        .config("spark.sql.catalog.nessie.uri", settings.nessie_uri)
        .config("spark.sql.catalog.nessie.ref", settings.nessie_branch)
        .config("spark.sql.catalog.nessie.authentication.type", "NONE")
        .config("spark.sql.catalog.nessie.warehouse", settings.warehouse)
        .config(
            "spark.jars.packages", f"{settings.iceberg_pkg},{settings.nessie_pkg}"
        )
        .config("spark.hadoop.fs.s3a.endpoint", settings.s3_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", settings.s3_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", settings.s3_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )


def main() -> None:
    settings = Settings()
    spark = build_spark(settings)

    data = [(1, "alice", 42.5), (2, "bob", 36.1), (3, "carol", 50.0)]
    df = (
        spark.createDataFrame(data, schema="id int, name string, score double")
        .withColumn("ingest_ts", current_timestamp())
    )

    spark.sql(
        """
        CREATE TABLE IF NOT EXISTS nessie.demo_users (
          id int,
          name string,
          score double,
          ingest_ts timestamp
        ) USING ICEBERG
        """
    )

    df.writeTo("nessie.demo_users").append()
    spark.sql("SELECT * FROM nessie.demo_users").show()
    spark.stop()


if __name__ == "__main__":
    main()
