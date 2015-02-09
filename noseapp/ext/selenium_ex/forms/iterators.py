# -*- coding: utf-8 -*-

from collections import Iterator
from contextlib import contextmanager


@contextmanager
def preserve_original(form, ignore_exc=None):
    """
    Функция помогает работать с формой меняя
    значения полей, и не беспокоится о том, что
    исходные данне значений полей будут утеряны

    :param form: инстанс объекта UIForm
    :param ignore_exc: исключение которое нужно
     игнорировать или картеж исключений
    """
    try:
        if ignore_exc:
            try:
                yield
            except ignore_exc:
                pass
        else:
            yield
    finally:
        form.reload()


def altered_form(form):
    """
    Возвращает контекстный менеджер который позволяет
    безопастно работать с измененным состоянием формы

    :param form: инстанс формы
    """
    def wrapper(ignore_exc=None):
        """
        :param ignore_exc: исключение или картеж
         исключений которые нужно игнорировать
        """
        return preserve_original(form, ignore_exc=ignore_exc)

    return wrapper


class FieldsIterator(Iterator):
    """
    Итератор который перебирает поля формы
    """

    def __init__(self, form, exclude=None):
        exclude = exclude or tuple()

        self.__current_index = 0
        self.__fields = [field for field in form._fields if field not in exclude]

    def fill(self):
        """
        Заполнить все поля
        """
        for field in self.__fields:
            field.fill()

    def clear(self):
        """
        Очистить поля
        """
        for field in self.__fields:
            field.clear()

    def next(self):
        try:
            field = self.__fields[self.__current_index]
        except IndexError:
            raise StopIteration

        self.__current_index += 1

        return field


class ValueToInvalidValueIterator(Iterator):
    """
    Итератор который на каждой новой итерации
    изменяет состояние формы меняя меняя value
    значение поля на invalid_value
    """

    def __init__(self, form, exclude=None):
        exclude = exclude or tuple()

        self.__form = form
        self.__current_index = 0
        self.__fields = [field for field in form._fields if field not in exclude]

    def _make_next(self):
        """
        Рукрисвный метод, поменяет value на invalid_value,
        если invalid_value установлен для поля
        """
        try:
            field = self.__fields[self.__current_index]
        except IndexError:
            raise StopIteration

        self.__current_index += 1

        invalid_value = field.invalid_value

        if invalid_value is not None:
            field.value = invalid_value
        else:
            self._make_next()

    def next(self):
        self._make_next()
        return altered_form(self.__form)


class RequiredIterator(Iterator):
    """
    Итератор который возвращает на каждой итерации
    FieldsIterator объект с исключенным полем required = True
    """

    def __init__(self, form):
        self.__form = form
        self.__current_index = 0
        self.__required_fields = [field for field in form._fields if field.required]

    def next(self):
        try:
            it = FieldsIterator(
                self.__form,
                exclude=(self.__required_fields[self.__current_index],),
            )
        except IndexError:
            raise StopIteration

        self.__current_index += 1

        return it


class ReplaceValueIterator(Iterator):
    """
    Итератор который при каждой итерации меняет значение
    указанного поля на значение из указанного списка
    поля на значение из списка на каждой новой итерации.
    """

    def __init__(self, form, field, values):
        if not isinstance(values, (list, tuple)):
            raise ValueError('values mast be list or tuple')

        self.__form = form
        self.__field = field
        self.__values = values
        self.__current_index = 0

    def next(self):
        try:
            self.__field.value = self.__values[self.__current_index]
        except IndexError:
            raise StopIteration

        self.__current_index += 1

        return altered_form(self.__form)
