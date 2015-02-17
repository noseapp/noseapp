# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms.ext.sqlalchemy.orm import model_form as wtf_model_form

from noseapp.ext.alchemy_ex.orm import Session
from noseapp.ext.alchemy_ex.exc import ValidationError


class BaseForm(Form):
    """
    Базовый класс формы созданной от модели
    """

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
        """
        Возвращает результат сохранения
        """
        return self._save_data

    def save(self):
        """
        Сохранение формы
        """
        self._save_data = self.model.create(**self.data)

    def save_update_by(self, **by):
        """
        Обновление данных по параметрам
        """
        self._save_data = self.model.update_by(by, **self.data)

    def save_update(self, id):
        """
        Сохранение обновленных данных для id
        """
        self._save_data = self.model.update(id, **self.data)


def model_form(model, only=None,
               exclude=None, field_args=None, converter=None,
               exclude_pk=True, exclude_fk=False, type_name=None):
    """
    Создает форму на базе модели
    """
    form = wtf_model_form(model, db_session=Session, base_class=BaseForm,
                          only=only, exclude=exclude, field_args=field_args,
                          converter=converter, exclude_pk=exclude_pk,
                          exclude_fk=exclude_fk, type_name=type_name)
    form.model = model
    return form
