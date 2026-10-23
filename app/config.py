from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_secret: str = "change-me-phase1"
    app_base_url: str = "http://localhost:8000"
    lan_base_url: str = "http://192.168.1.10:8080"
    db_path: str = "./data/hergrade.sqlite3"
    serial_port: str = "/dev/ttyUSB0"
    serial_baud: int = 115200
    thresh_version: str = "v0.1-0.75"
    cam_index: int = 0


settings = Settings()
