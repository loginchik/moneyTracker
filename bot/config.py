from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    app_name: str = 'Spendings Manager'
    bot_token: SecretStr
    postgresql_url: SecretStr
    db_host: SecretStr
    db_port: int
    db_user: SecretStr
    db_password: SecretStr
    db_name: SecretStr

    db_url: SecretStr
    db_apikey: SecretStr
    model_config = SettingsConfigDict(env_file='.env', 
                                      env_file_encoding='utf-8', 
                                      extra='allow')

    
settings = Settings()