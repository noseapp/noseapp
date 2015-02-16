# -*- coding: utf-8 -*-


"""
Модуль для работы с ORM sql alchemy
"""

import logging
from copy import copy
from contextlib import contextmanager

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.declarative import declarative_base

from noseapp.ext.alchemy_ex import registry
from noseapp.ext.alchemy_ex.exc import NotFound


logger = logging.getLogger(__name__)


Session = registry.get_session()


@contextmanager
def session_scope(rollback=True):
    """
    Контекстный менеджер для работы с сессией
    """
    session = Session()
    try:
        yield session
    except:
        if rollback:
            session.rollback()
        raise
    finally:
        session.close()


def dict_info(params):
    """
    Переводит словарь параметров в строковое представоение

    :param params(dict): словарь с параметрами
    """
    return u', '.join([u'%s=%s' % p for p in params.items()])


class ModelCRUD(object):
    """
    Класс расширяет возможности BaseModel
    для упрощения раоты с CRUD операциями
    """

    query = Session.query_property()

    def __init__(self, **params):
        """
        Инициализатор нового объекта модели
        """
        logger.debug('create new model object {}'.format(self.__class__.__name__))

        for k, v in params:
            setattr(self, k, v)

    @classmethod
    def create(cls, **params):
        """
        Созадение нового объекта
        """
        with session_scope() as session:
            obj = cls(**params)

            session.add(obj)
            session.commit()
            session.refresh(obj)

        return copy(obj)

    @classmethod
    def get(cls, id):
        """
        Получение объекта по id
        """
        with session_scope(rollback=False) as session:
            obj = session.query(cls).get(id)

        if obj:
            return obj

        raise NotFound(
            u'object <{} id={}> not found'.format(cls.__name__, id),
        )

    @classmethod
    def get_by(cls, **params):
        """
        Получение объекта по фильтрам
        """
        with session_scope(rollback=False) as session:
            obj = session.query(cls).filter_by(**params).first()

        if obj:
            return obj

        raise NotFound(
            u'object <{} {}> not found'.format(cls.__name__, dict_info(params)),
        )

    @classmethod
    def getlist(cls):
        """
        Получение списка всех объектов
        """
        with session_scope(rollback=False) as session:
            result = session.query(cls).all()

        return result

    @classmethod
    def getlist_by(cls, **params):
        """
        Получение списка по фильтрам
        """
        with session_scope(rollback=False) as session:
            result = session.query(cls).filter_by(**params).all()

        return result

    @classmethod
    def update(cls, _id, **params):
        """
        Обновление объекта по id
        """
        with session_scope() as session:
            obj = session.query(cls).get(_id)

            if not obj:
                raise NotFound(
                    u'object <{} id={}> not found'.format(cls.__name__, _id),
                )

            for k, v in params.items():
                setattr(obj, k, v)

            session.add(obj)
            session.commit()
            session.refresh(obj)

        return copy(obj)

    @classmethod
    def update_by(cls, by, **params):
        """
        Обновление объекта по параметрам
        """
        with session_scope() as session:
            obj = session.query(cls).filter_by(**by).first()

            if not obj:
                raise NotFound(
                    u'object <{} {}> not found'.format(cls.__name__, dict_info(by)),
                )

            for k, v in params.items():
                setattr(obj, k, v)

            session.add(obj)
            session.commit()
            session.refresh(obj)

        return copy(obj)

    @classmethod
    def remove(cls, id):
        """
        Удаление объекта по id
        """
        with session_scope() as session:
            obj = session.query(cls).get(id)

            if not obj:
                raise NotFound(
                    u'object <{} id={}> not found'.format(cls.__name__, id),
                )

            session.delete(obj)
            session.commit()

        return u'object {} is removed'.format(id)

    @classmethod
    def remove_by(cls, **params):
        """
        Удаление объекта по параметрам
        """
        with session_scope() as session:
            obj = session.query(cls).filter_by(**params).first()

            if not obj:
                raise NotFound(
                    u'object <{} {}> not found'.format(cls.__name__, dict_info(params)),
                )

            session.delete(obj)
            session.commit()

        return u'object <{} {}> is removed'.format(cls.__name__, dict_info(params))

    def __repr__(self):
        if hasattr(self, 'id'):
            return '<{} id={}>'.format(self.__class__.__name__, self.id or 'NULL')

        return '<{}>'.format(self.__class__.__name__)


def mount_meta(meta, cls):
    """
    Монтирует свойства из класса Meta в класс
    модели, как это привычно видеть алхимии
    """
    model_cls = cls.__mro__[0]

    table_name = getattr(meta, 'table', None)

    if table_name is not None:
        setattr(model_cls, '__tablename__', table_name)


class BoundDeclarativeMeta(DeclarativeMeta):
    """
    Расширяет конфигурацию модели дополняя ее классом Meta
    """

    def __init__(self, name, bases, d):
        meta = d.pop('Meta', None)

        if meta is not None:
            bind_key = getattr(meta, 'bind', 'default')
            mount_meta(meta, self)
        else:
            bind_key = 'default'

        DeclarativeMeta.__init__(self, name, bases, d)

        try:
            self.__table__.info['bind_key'] = bind_key
        except AttributeError:  # при создании декларативного
            # класса еще не будет атрибута __table__, поэтому эта
            # ситация является нормальной
            pass


BaseModel = declarative_base(cls=ModelCRUD, metaclass=BoundDeclarativeMeta)
