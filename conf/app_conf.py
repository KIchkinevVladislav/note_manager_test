import environ
from dotenv import load_dotenv

load_dotenv()


@environ.config(prefix="TOKEN")
class AccessTokenConfig:
    secret_key: str = environ.var(default="secret_key")
    algorithm: str = environ.var(default="HS256")
    access_token_expire_minutes: int = environ.var(default=240, converter=int)


access_token_config: AccessTokenConfig = AccessTokenConfig.from_environ()
