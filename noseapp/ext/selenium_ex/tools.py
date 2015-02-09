# -*- coding: utf8 -*-


def make_object(web_element):
    """
    Функция конвертирует WebElement в объект

    Пример:

        input = driver.find_element...
        value = make_object(input).value

    :param web_element: объект WebElement
    """
    class WebElementToObject(object):

        def __init__(self, web_element):
            self._web_element = web_element

        def __getattr__(self, item):
            atr = self._web_element.get_attribute(item)

            if atr:
                return atr

            raise AttributeError('{}: {}'.format(repr(self._web_element), item))

    return WebElementToObject(web_element)


class Container(object):
    """
    Класс реализует контенер для для другого класса.
    Основная задача - обеспечить отложенную инициализацию объекта.
    """

    def __init__(self, _class):
        self.__class = _class

    def __call__(self, *args, **kwargs):
        return self.__class(*args, **kwargs)
