import pathlib
from os import getenv
from dotenv import load_dotenv
from dataclasses import dataclass

assert load_dotenv(), '.env not found'


@dataclass
class DatabaseSettings:
    user: str
    password: str
    host: str
    port: str
    name: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{settings.database.user}:{settings.database.password}@{settings.database.host}:{settings.database.port}/{settings.database.name}"


class AuthSettings:
    def __init__(
            self,
            secret_key: str | None = None,
            access_token_life_time: float | None = None,
            refresh_token_life_time: float | None = None,
            algorithm: str | None = None,
            max_enter_attempts: int | None = None
    ) -> None:
        """
        :param secret_key: str Secret key for jwt
        :param access_token_life_time: float Lifetime in hours
        :param refresh_token_life_time: float Lifetime in hours
        """
        self.secret_key: str = secret_key or getenv('SECRET_KEY')
        self.access_token_life_time: float = access_token_life_time or float(getenv('ACCESS_TOKEN_LIFETIME'))
        self.refresh_token_life_time: float = refresh_token_life_time or float(getenv('REFRESH_TOKEN_LIFETIME'))
        self.algorithm: str = algorithm or getenv('ALGORITHM')
        self.max_enter_attempts: int = max_enter_attempts or int(getenv('MAX_ENTER_ATTEMPTS'))




@dataclass(frozen=True)
class Settings:
    base_dir: pathlib.Path
    host: str
    port: int
    protocol: str
    database: DatabaseSettings
    auth: AuthSettings


settings = Settings(
    base_dir=pathlib.Path(__file__).parent.absolute(),
    host=getenv('DOMAIN'),
    port=int(getenv('PORT')),
    protocol=getenv('PROTOCOL'),
    database=DatabaseSettings(
        user=getenv('POSTGRES_USER'),
        password=getenv('POSTGRES_PASSWORD'),
        host=getenv('DATABASE_HOST'),
        port=getenv('DATABASE_PORT'),
        name=getenv('POSTGRES_DB'),
    ),
    auth=AuthSettings()
)
