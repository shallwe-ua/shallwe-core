from functools import lru_cache
from typing import Tuple, Optional, Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode


class EnvSettings(BaseSettings):
    SHALLWE_GLOBAL_SITE_URL_EXTERNAL: str
    SHALLWE_GLOBAL_SITE_URL_INTERNAL: str
    SHALLWE_GLOBAL_MEDIA_STORAGE_URL_EXTERNAL: Optional[str] = None
    SHALLWE_GLOBAL_OAUTH_CLIENT_ID: str
    SHALLWE_GLOBAL_OAUTH_CLIENT_SECRET: str
    SHALLWE_GLOBAL_ENV_MODE: str
    SHALLWE_GLOBAL_OAUTH_REDIRECT_URI: str
    SHALLWE_BACKEND_SECRET_KEY: str
    SHALLWE_BACKEND_DEBUG_ON: bool
    SHALLWE_BACKEND_REST_BROWSABLE: bool
    SHALLWE_BACKEND_DB_NAME: str
    SHALLWE_BACKEND_TEST_DB_NAME: str
    SHALLWE_BACKEND_DB_USER: str
    SHALLWE_BACKEND_DB_PASS: str
    SHALLWE_BACKEND_DB_HOST: str
    SHALLWE_BACKEND_DB_PORT: int
    SHALLWE_BACKEND_ALLOWED_HOSTS: Annotated[Tuple[str, ...], NoDecode]
    SHALLWE_BACKEND_ALLOWED_CIDR_NETS: Optional[Annotated[Tuple[str, ...], NoDecode]] = None
    SHALLWE_BACKEND_CSRF_TRUSTED_ORIGINS: Annotated[Tuple[str, ...], NoDecode]
    SHALLWE_BACKEND_CORS_ALLOWED_ORIGINS: Annotated[Tuple[str, ...], NoDecode]
    SHALLWE_BACKEND_CREDENTIALS_COOKIE_DOMAIN: Optional[str] = None
    SHALLWE_BACKEND_CREDENTIALS_COOKIE_SAMESITE: Optional[str] = None
    SHALLWE_BACKEND_CREDENTIALS_COOKIE_SECURE: bool = False
    SHALLWE_BACKEND_DEEPFACE_MODELS: Annotated[Tuple[str, ...], NoDecode]

    # noinspection PyNestedDecorators
    @field_validator(
        "SHALLWE_BACKEND_ALLOWED_HOSTS",
        "SHALLWE_BACKEND_ALLOWED_CIDR_NETS",
        "SHALLWE_BACKEND_CSRF_TRUSTED_ORIGINS",
        "SHALLWE_BACKEND_CORS_ALLOWED_ORIGINS",
        "SHALLWE_BACKEND_DEEPFACE_MODELS",
        mode="before"
    )
    @classmethod
    def split_csv(cls, v):
        if isinstance(v, str):
            return tuple(item.strip() for item in v.split(",") if item.strip())
        return tuple()    # Empty tuple for compatibility with star-syntax ([*PARAM])


    model_config = {
        "env_file": ".env",  # reads .env if present in cwd, otherwise shell-loaded variables (preferred with autoenv)
        "env_file_encoding": "utf-8",
        "env_ignore_empty": True,  # treat empty ("") strings as no value provided
        "env_parse_none_str": "None",  # treats "None" string as actual None
    }


@lru_cache
def env_settings() -> EnvSettings:
    return EnvSettings()
