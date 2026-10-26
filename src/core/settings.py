from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url : str
    secret_key : str
    mqtt_broker : str
    frontend_url : str
    smtp_server : str
    smtp_port : int
    username : str
    password : str
    
    model_config = SettingsConfigDict(env_file = ".env")

settings = Settings() # type: ignore