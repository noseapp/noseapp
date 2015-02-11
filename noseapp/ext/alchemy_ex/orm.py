# -*- coding: utf-8 -*-


"""
Модуль для работы с ORM sql alchemy
"""

import logging
from copy import copy
from contextlib import contextmanager

from wtforms import Form
from sqlalchemy.ext.declarative import declarative_base
from wtforms.ext.sqlalchemy.orm import model_form as wtf_model_form

from noseapp.ext.alchemy_ex import session
from noseapp.ext.alchemy_ex.exc import NotFound
from noseapp.ext.alchemy_ex.exc import ValidationError


logger = logging.getLogger(__name__)


Session = session.get()


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


class BaseForm(Form):
    """Базовый класс формы созданной от модели"""

    model = None  # Класс модели
    _save_data = None  # Данные после сохранения

    def __init__(self, *args, **kwargs):
        """
        Переопределяем конструктор с целью валидации
        формы на момент создания инстанса
        """
        super(BaseForm, self).__init__(*args, **kwargs)
        if not self.validate():
            raise ValidationError(self.errors)

    @property
    def save_data(self):
        """Возвращает результат сохранения"""
        return self._save_data

    def save(self):
        """Сохранение формы"""
        self._save_data = self.model.create(**self.data)

    def save_update_by(self, **by):
        """Обновление данных по параметрам"""
        self._save_data = self.model.update_by(by, **self.data)

    def save_update(self, _id):
        """Сохранение обновленных данных для id"""
        self._save_data = self.model.update(_id, **self.data)


def model_form(model, only=None,
               exclude=None, field_args=None, converter=None,
               exclude_pk=True, exclude_fk=False, type_name=None):
    """Создает форму на базе модели"""
    form = wtf_model_form(model, db_session=Session, base_class=BaseForm,
                          only=only, exclude=exclude, field_args=field_args,
                          converter=converter, exclude_pk=exclude_pk,
                          exclude_fk=exclude_fk, type_name=type_name)
    form.model = model
    return form


def dict_info(params):
    """
    Переводит словарь параметров в строковое представоение

    :param params(dict): словарь с параметрами
    """
    return u', '.join([u'%s=%s' % p for p in params.items()])


class ModelCRUD(object):
    """
    Миксин для упрощения раоты с CRUD операциями
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
            obj = copy(obj)
        return obj

    @classmethod
    def get(cls, id):
        """
        Получение объекта по id
        """
        with session_scope(rollback=False) as session:
            obj = session.query(cls).get(id)
        if obj:
            return obj
        raise NotFound(u'object id={} not found'.format(id))

    @classmethod
    def get_by(cls, **params):
        """
        Получение объекта по фильтрам
        """
        with session_scope(rollback=False) as session:
            obj = session.query(cls).filter_by(**params).first()
        if obj:
            return obj
        raise NotFound(u'object {} not found'.format(dict_info(params)))

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
                raise NotFound(u'object id={} not found'.format(_id))
            for k, v in params.items():
                setattr(obj, k, v)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            obj = copy(obj)
        return obj

    @classmethod
    def update_by(cls, by, **params):
        """
        Обновление объекта по параметрам
        """
        with session_scope() as session:
            obj = session.query(cls).filter_by(**by).first()
            if not obj:
                raise NotFound(u'object {} not found'.format(dict_info(by)))
            for k, v in params.items():
                setattr(obj, k, v)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            obj = copy(obj)
        return obj

    @classmethod
    def remove(cls, id):
        """
        Удаление объекта по id
        """
        with session_scope() as session:
            obj = session.query(cls).get(id)
            if not obj:
                raise NotFound(u'object id={} not found'.format(id))
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
                raise NotFound(u'object {} not found'.format(dict_info(params)))
            session.delete(obj)
            session.commit()
        return u'object {} is removed'.format(dict_info(params))

    def __str__(self):
        if hasattr(self, 'id'):
            return '<{} id={}>'.format(self.__class__.__name__, self.id or 'NULL')
        return '<{}>'.format(self.__class__.__name__)


BaseModel = declarative_base(cls=ModelCRUD)
