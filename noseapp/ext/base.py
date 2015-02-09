# -*- coding: utf-8 -*-

from abc import ABCMeta
from abc import abstractproperty


class BaseExtension(object):

    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        """
        Имя по которому extension будет установлен
        """
        pass
