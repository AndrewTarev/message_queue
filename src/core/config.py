import os

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# abs_path_env = os.path.abspath("../../.env")
# env_template = os.path.abspath("../../.env.template")
load_dotenv()


class BaseServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )


class RabbitConfig(BaseServiceSettings):
    RMQ_HOST: str
    RMQ_PORT: int
    RMQ_USER: str
    RMQ_PASSWORD: str
    RMQ_QUEUE: str = "your-queue-name"

    @property
    def url(self) -> str:
        return (
            f"amqp://{self.RMQ_USER}:"
            f"{self.RMQ_PASSWORD}@"
            f"{self.RMQ_HOST}:"
            f"{self.RMQ_PORT}/"
        )


class Settings(BaseModel):
    rabbit_config: RabbitConfig = RabbitConfig()
    logging: str = "DEBUG"


settings = Settings()

if __name__ == "__main__":
    print(settings.rabbit_config.url)
