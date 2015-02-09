# -*- coding: utf-8 -*-

"""
Модуль описывает поля формы html документа.

Принцып построения объектов:

- Каждый объект описывающий html сущность мапится на тег
- Имеет набор базовых параметров описывающих поле(
значениие для заполнения, обязательность заполнения,
невалидное значение и т.д.).
- Каждый объект поля должен иметь базовый набор действий, таких как:
заполнение значением, очистка поля.
"""

from selenium.common.exceptions import NoSuchElementException

from noseapp.ext.selenium_ex.tools import make_object


def selector(**kwargs):
    """
    proxy для атрибутов тега.
    необходим исключительно для украшения api.
    """
    return kwargs


class FieldError(BaseException):
    pass


class Parent(object):
    """
    Объект ханит данные по которым нужно
    вытащить родительский элемент
    """

    def __init__(self, tag, **selector):
        self.tag = tag
        self.selector = selector


class BaseField(object):
    """
    Базовый класс для всех типов полей

    :name: имя поля
    :value: значение для заполнения поля
    :required: является ли поле обязательным для заполнения
    :selector: fields.selector
    :invalid_value: невалидное значение поля
    :query: selenium_ex.query.QueryProcessor
    """

    class Meta:
        tag = None

    def __init__(self,
                 name,
                 value=None,
                 required=False,
                 selector=None,
                 invalid_value=None,
                 query=None,
                 parent=None,
                 weight=None):

        self.name = name

        if not isinstance(selector, dict):
            raise ValueError('incorrect selector')

        self._query = query
        self._weight = weight
        self._parent = parent
        self._selector = selector

        self.value = value
        self.required = required
        self.invalid_value = invalid_value

    @property
    def weight(self):
        return self._weight

    def init_query(self, query):
        """
        Инициализирет query объект в проперти.
        Делает это только один раз, если query
        уже инициализировано, то выкинет исключение.
        Делается для того, чтобы нельзя было привязать
        поля к разным оканм браузера, подобные алгоритмы
        могут очень сильно запутать сценарии тест кейсов.
        """
        if self._query is not None:
            raise FieldError('query object already initialize')

        self._query = query

    def init_parent(self, parent):
        """
        Инициализирует контенер с настройками для
        получения доступа к родительскому элементу поля
        """
        if self._parent is None and parent is None:
            return

        if not isinstance(parent, Parent):
            raise ValueError('wrapper object is not instance Wrapper')

        self._parent = parent

    def get_web_element(self):
        """
        Возвращает объект WebElement
        """
        if self._parent is not None:
            parent = getattr(self._query, self._parent.tag)(**self._parent.selector).first()
            tag = getattr(self._query(parent), self.Meta.tag)
            return tag(**self._selector).first()

        tag = getattr(self._query, self.Meta.tag)
        return tag(**self._selector).first()

    @property
    def obj(self):
        """
        Возвращает сконвертированный WebElement в объект
        """
        return make_object(self.get_web_element())

    def fill(self, value=None):
        """
        Заполнить поле. Если значение None, то
        берется self.value иначе переданное в метод
        """
        raise NotImplementedError

    def clear(self):
        """
        Очистить поле
        """
        raise NotImplementedError


class Input(BaseField):
    """
    Поле типа <input>
    """

    class Meta:
        tag = 'input'

    def fill(self, value=None):
        if value is None:
            value = self.value

        self.get_web_element().send_keys(*value)

    def clear(self):
        self.get_web_element().clear()


class TextArea(Input):
    """
    Поле типа <textarea>
    """

    class Meta:
        tag = 'textarea'


class Checkbox(BaseField):
    """
    Поле типа <input type="checkbox">
    """

    class Meta:
        tag = 'input'

    def fill(self, value=None):
        if value is None:
            value = self.value

        el = self.get_web_element()
        current_value = el.is_selected()

        if current_value and value:
            raise FieldError('checkbox already selected')

        elif not current_value and not value:
            raise FieldError('checkbox already unselected')

        el.click()

    def clear(self):
        el = self.get_web_element()

        if el.is_selected():
            el.click()


class RadioButton(Checkbox):
    """
    Поле типа <input type="radio">
    Работа с полем radio аналогична checkbox,
    поэтому этот класс просто "сахар", для улучшения
    читабельности.
    """
    pass


class Select(BaseField):
    """
    Поле типа <select>
    """

    class Meta:
        tag = 'select'

    def fill(self, value=None):
        if value is None:
            value = self.value

        select = self.get_web_element()

        options = filter(
            lambda opt: opt.get_attribute('value') == value,
            select.find_elements_by_tag_name('option'),
        )

        if options:
            options[0].click()
        else:
            raise NoSuchElementException(
                u'select field "{}", selector "{}", option "{}"'.format(
                    self.name, str(self._selector), value
                ),
            )

    def clear(self):
        """
        Поле select невозможно очистить
        каким-либо шаблонным сценрием
        """
        pass
