"""Central config for the demo. Sensible local defaults so `mise run stack-up` + `mise run pipeline-ok` just works."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    # Nessie
    nessie_api_uri: str = "http://localhost:19120/api/v2"
    nessie_iceberg_uri: str = "http://localhost:19120/iceberg"  # + /<branch>
    main_branch: str = "main"

    # Object store (MinIO)
    warehouse: str = "s3://iceberg-warehouse"
    s3_endpoint: str = "http://localhost:29000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "8qqR90Az"
    s3_region: str = "us-east-1"

    def pyiceberg_props(self, branch: str) -> dict:
        """kwargs for pyiceberg.catalog.load_catalog targeting a Nessie branch."""
        return {
            "type": "rest",
            "uri": f"{self.nessie_iceberg_uri}/{branch}",
            "s3.endpoint": self.s3_endpoint,
            "s3.access-key-id": self.s3_access_key,
            "s3.secret-access-key": self.s3_secret_key,
            "s3.region": self.s3_region,
            "s3.path-style-access": "true",
        }


settings = Settings()
