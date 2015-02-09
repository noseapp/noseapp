# -*- coding: utf-8 -*-

from copy import deepcopy

from noseapp.ext.selenium_ex import QueryProcessor
from noseapp.ext.selenium_ex.forms.fields import BaseField
from noseapp.ext.selenium_ex.forms.iterators import FieldsIterator
from noseapp.ext.selenium_ex.tools import Container as FormContainer
from noseapp.ext.selenium_ex.forms.iterators import RequiredIterator
from noseapp.ext.selenium_ex.forms.iterators import ReplaceValueIterator
from noseapp.ext.selenium_ex.forms.iterators import ValueToInvalidValueIterator


def make_field(form_class):
    """
    Сделать форму полем другой формы

    :param form_class: класс формы
    """
    if not issubclass(form_class, UIForm):
        raise ValueError('form class is not UIForm subclass')

    return FormContainer(form_class)


class FormStorage(dict):
    """
    Класс реализует объект который
    хранит исходное состояние формы
    """

    def _set_field(self, filed):
        """
        Устанавливает исходные занчения поля

        :param filed: инстанс объекта fields.BaseField
        """
        self[filed] = {
            'value': filed.value,
            'required': filed.required,
            'invalid_value': filed.invalid_value,
        }

    def get_field(self, filed):
        """
        Получить поле из словаря
        """
        return self.get(filed)

    def add_field(self, field):
        """
        Добавить поле в хранимку
        """
        self._set_field(field)

    def restore(self, field_list):
        """
        Восстановить поля формы
        """
        for field in field_list:
            orig = self.get_field(field)

            if orig:
                field.value = orig['value']
                field.required = orig['required']
                field.invalid_value = orig['invalid_value']
            else:
                continue


class UIForm(object):
    """
    Класс реализует интерфейс для работы с формой.
    """

    def __init__(self, driver):
        self._fields = []
        self._fill_memo = set()
        self._storage = FormStorage()
        self._query = QueryProcessor(driver)

        for atr in dir(self):
            val = getattr(self, atr, None)

            if isinstance(val, BaseField):
                new_val = deepcopy(val)
                setattr(self, atr, new_val)
                new_val.init_query(self._query)
                new_val.init_parent(self.wrapper)
                self._fields.append(new_val)
                self._storage.add_field(new_val)
            elif isinstance(val, FormContainer):
                setattr(self, atr, val(driver))

        self._fields.sort(key=lambda f: f.weight)

    @classmethod
    def copy(cls):
        """
        Если класс нужно как-то модифицировать перед
        использованием, то лучше сделать его копию.
        В противном случаи при многопоточной работе
        могут возникнуть проблемы.
        """
        return deepcopy(cls)

    @property
    def is_submit(self):
        """
        Определить признак по которому можно
        понимать отправилась форма или нет
        """
        return False

    @property
    def wrapper(self):
        """
        В этом свойстве можно вернуть объект fields.Parent
        который будет указывать на родительский элемент всем полям
        """
        return None

    def get_wrapper(self):
        """
        Получает WebElement из инструкции в свойстве wrapper
        """
        wrapper = self.wrapper
        if wrapper is not None:
            tag = getattr(self._query, wrapper.tag)
            return tag(**wrapper.selector).first()

        raise ValueError('wrapper property is None')

    @property
    def fields(self):
        """
        Список доступных полей формы.
        Свойство носит информативный характер.
        """
        return [field.name for field in self._fields]

    def submit(self):
        """
        Отправить форму
        """
        pass

    def reload(self):
        """
        Восстанавливает все значениия формы по умолчанию
        """
        self._storage.restore(self._fields)

    def fill(self):
        """
        Заполнить форму
        """
        for field in self._fields:
            if field.name not in self._fill_memo:
                field.fill()

        self._fill_memo.clear()

    def fill_field(self, field, value=None):
        """
        Запонить поле и запомнить действие, чтобы
        не повторять его при полном заполнении

        :param field: объектполя
        :param value: значение для заполнения, если None,
         то дефолтное значение
        """
        field.fill(value)
        self._fill_memo.add(field.name)

    def clear(self):
        """
        Очистить форму
        """
        for field in self._fields:
            field.clear()

    def assert_submit(self):
        """
        Проверет сохранение формы
        """
        assert self.is_submit, 'Form "{}" is not saved'.format(self.__class__.__name__)

    def assert_not_submit(self):
        """
        Проверяет, что форма не сохранилась
        """
        assert not self.is_submit, 'Form "{}" is saved'.format(self.__class__.__name__)

    def each_required(self):
        """
        Возвращает итератор.
        На каждую итерацию возвращается инстанс
        iterators.FieldsIterator в котором исключено обязательное поле.

        Пример использования:

            form = MyForm(driver)
            for fields in form.each_required():
                fields.fill()
                form.submit()
                ...
        """
        return RequiredIterator(self)

    def each_fields(self, exclude=None):
        """
        Возвращает итератор.
        На каждую итерацию возвращается следующий объект поля.

        Пример использования:

            form = MyForm(driver)
            for field in form.each_fields():
                field.fill()
                ...

        :param exclude: список или котеж полей которые нужно исключить
        """
        return FieldsIterator(self, exclude=exclude)

    def each_replace(self, field, values):
        """
        Возвращает итератор. Перебирает values.
        На каждую итерацию меняет значение указанного поля на значение
        из списка, возвращает контекстный менеджер для безопасной работы
        с измененным состоянием текущего инстанса.

        Пример использования:

            form = MyForm(driver)
            for altered_form in form.each_replace(form.title, ('Hello', 'World', '!')):
                with altered_form():
                    form.fill()
                    form.submit()
                    ...

        :param field: поле которое в котором будет меняться значение
        :param values: список или котеж значений для замены
        """
        return ReplaceValueIterator(self, field, values)

    def each_invalid(self, exclude=None):
        """
        Возвращает итератор. Перебирает поля.
        На каждую итерацию меняет value поля на invalid_value.
        Возвращает контекстный менеджер для безопасной работы
        с измененным состоянием текущего инстанса.

        Пример использования:

            form = MyForm(driver)
            for altered_form in form.each_invalid():
                with altered_form():
                    form.fill()
                    form.submit()
                    ...

        :param exclude: список или котеж полей которые нужно исключить
        """
        return ValueToInvalidValueIterator(self, exclude=exclude)
