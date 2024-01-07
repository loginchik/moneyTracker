from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    app_name: str = 'Spendings Manager'
    bot_token: SecretStr
    db_url: SecretStr
    db_apikey: SecretStr
    model_config = SettingsConfigDict(env_file='.env', 
                                      env_file_encoding='utf-8', 
                                      extra='allow')

    
settings = Settings()