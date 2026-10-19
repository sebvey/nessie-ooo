"""Central config for the demo, read from the environment that mise exports (`mise.toml` for the URLs, `mise.local.toml` for the secrets): run through mise."""

import sys

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    # Nessie
    nessie_uri: str = Field(validation_alias="NESSIE_URI")
    main_branch: str = "main"

    # Object store (Silo)
    warehouse: str = "s3://iceberg-warehouse"
    s3_endpoint: str = Field(validation_alias="AWS_ENDPOINT_URL")
    s3_access_key: str = Field(validation_alias="AWS_ACCESS_KEY_ID")
    s3_secret_key: str = Field(validation_alias="AWS_SECRET_ACCESS_KEY")
    s3_region: str = Field(validation_alias="AWS_REGION")
    silo_console_url: str = Field(validation_alias="SILO_CONSOLE_URL")

    @property
    def nessie_api_uri(self) -> str:
        return f"{self.nessie_uri}/api/v2"

    @property
    def nessie_iceberg_uri(self) -> str:
        return f"{self.nessie_uri}/iceberg"  # + /<branch>

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


def load() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        missing = ", ".join(str(err["loc"][0]) for err in e.errors())
        sys.exit(f"Missing environment variables: {missing}. Set them in mise.local.toml (secrets) or mise.toml, and run through mise.")


settings = load()
