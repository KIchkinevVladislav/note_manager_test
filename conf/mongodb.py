from dotenv import load_dotenv
import environ


load_dotenv()


@environ.config(prefix='MONGO')
class MongoDBConfig:
    host: str = environ.var(default='mongo')
    port: str = environ.var(default='27017')
    database: str = environ.var()


mongodb_config: MongoDBConfig = MongoDBConfig.from_environ()
