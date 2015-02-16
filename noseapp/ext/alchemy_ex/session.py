# -*- coding: utf-8 -*-


from sqlalchemy.orm.session import Session as BaseSession

from noseapp.ext.alchemy_ex import registry
from noseapp.ext.alchemy_ex.exc import InvalidBindKey


class Session(BaseSession):
    """
    Класс позволяет мапить модели на установленные движки
    """

    def get_bind(self, mapper=None, clause=None):
        if mapper is not None:
            info = getattr(mapper.mapped_table, 'info', {})
            engine_key = info.get('bind_key')

            if engine_key is not None:
                engine = registry.get_engine(engine_key)

                if not engine:
                    raise InvalidBindKey(engine_key)

                return engine

        return BaseSession.get_bind(self, mapper, clause)
