from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    app_name: str = 'Spendings Manager'
    bot_token: SecretStr
    db_url: SecretStr
    db_apikey: SecretStr
    webhook_token: SecretStr
    webhook_base_url: SecretStr
    webhook_server_port: int
    model_config = SettingsConfigDict(env_file='.env', 
                                      env_file_encoding='utf-8', 
                                      extra='allow')

    
settings = Settings()