# -*- coding: utf-8 -*-

"""
Пакет помогает оптимизировать операции по работе с web формами в selenium


Пример испоьзования:

    from . import fields
    from . import form

    class MyForm(form.UIForm):

        title = fields.Input(u'Заголовок',
            value='Hello World',
            selector=fields.selector(id='title'),
        )
        description = fields.TextArea(u'Описание',
            required=True,
            value='Hello, my name is Tester',
            selector=fields.selector(_class='desc'),
        )

        @property
        def is_save(self):
            wrapper = self._query.div(id='form-wrapper').first()
            text = wrapper.text
            return u'Сохранено' in text

        def submit(self):
            button = self._query.input(name='submit-button).first()
            button.click()

    form = MyForm(driver)
    form.fill()
    form.submit()
    form.assert_save()

    Можно заполнять поля по отдельности, к примеру:

    form.title.fill()
    # Если хочется не дефолтное значение, то можно поступить так
    form.title.fill('Title')
    # при этом дефолтное значение не будет изменено

    Как работать с объектами типа Field смотрите в модуле fields текущего пакета
"""

from noseapp.ext.selenium_ex.forms import fields
from noseapp.ext.selenium_ex.forms.form import UIForm
from noseapp.ext.selenium_ex.forms.form import make_field



__all__ = (
    fields,
    UIForm,
    make_field,
)
