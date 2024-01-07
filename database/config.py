from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    postgresql_url: SecretStr
    db_host: SecretStr
    db_port: int
    db_user: SecretStr
    db_password: SecretStr
    db_name: SecretStr
    model_config = SettingsConfigDict(env_file='.env.database', 
                                      env_file_encoding='utf-8', 
                                      extra='allow')

    
settings = Settings()