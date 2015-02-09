# -*- coding: utf-8 -*-

from contextlib import contextmanager

from sqlalchemy.pool import NullPool

from noseapp.ext.base import BaseExtension
from noseapp.ext.alchemy_ex.config import Config
from noseapp.ext.alchemy_ex.base import create_engine


DEFAULT_PORT = 3306
DEFAULT_HOST = '127.0.0.1'
DEFAULT_POOL_CLASS = NullPool
DEFAULT_PROTOCOL = 'mysql+mysqlconnector'

DEFAULT_USE_UNICODE = 1
DEFAULT_CHARSET = 'utf8'

DEFAULT_DNS_PARAMS = dict(
    charset=DEFAULT_CHARSET,
    use_unicode=DEFAULT_USE_UNICODE,
)


class MySQLEx(BaseExtension):
    """
    Расширение для работы с MySQL
    """

    name = 'mysql'

    def __init__(self,
                 db=None,
                 user=None,
                 password='',
                 host=DEFAULT_HOST,
                 port=DEFAULT_PORT,
                 protocol=DEFAULT_PROTOCOL,
                 pool_class=DEFAULT_POOL_CLASS,
                 dns_params=DEFAULT_DNS_PARAMS,
                 **engine_options
                 ):
        self._engine = create_engine(
            host=host,
            port=port,
            db=db,
            user=user,
            password=password,
            protocol=protocol,
            pool_class=pool_class,
            dns_params=dns_params,
            **engine_options
        )

    @contextmanager
    def read(self):
        """
        Выполнить sql на чтение
        """
        yield self._engine.connect().execute

    @contextmanager
    def write(self):
        """
        Выполнить sql на запись
        """
        connection = self._engine.connect()
        trans = connection.begin()
        try:
            yield connection.execute
            trans.commit()
        except:
            trans.rollback()
            raise


def make_config():
    """
    Создать скелет конфигурации
    """
    return Config(
        db=None,
        user=None,
        password=None,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        protocol=DEFAULT_PROTOCOL,
        pool_class=DEFAULT_POOL_CLASS,
        dns_params=DEFAULT_DNS_PARAMS,
    )
