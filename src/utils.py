import psycopg2
import credentials
import yaml
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def read_yaml(f):
    with open(f, 'r') as file:
        return yaml.safe_load(file.read())


def connect():
    """Creates a connection to the Postgres database specified in the credentials file
    Returns:Psycopg.connection: The database connection"""

    config = {
        'database': credentials.database,
        'user': credentials.user,
        'password': credentials.password,
        'host': credentials.host,
        'port': credentials.port
    }

    return psycopg2.connect(**config)


def timeit(logger):

    def decorator(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start = time.time()
            result = func(self, *args, **kwargs)
            duration = time.time() - start
            logger.info(f"{func.__name__} took: {duration:.4f} sec")
            return result

        return wrapper

    return decorator
