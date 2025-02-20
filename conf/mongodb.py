import environ
from dotenv import load_dotenv

load_dotenv()


@environ.config(prefix='MONGO')
class MongoDBConfig:
    host: str = environ.var(default='localhost')
    port: str = environ.var(default='27017')
    database: str = environ.var()


mongodb_config: MongoDBConfig = MongoDBConfig.from_environ()
