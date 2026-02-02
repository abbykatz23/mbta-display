from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mbta_api_key: str
    pixoo_ip_address: str

    model_config = {
        "env_file": ".env"
    }


settings = Settings()
