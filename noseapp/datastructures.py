# coding: utf-8


class ModifyDict(dict):
    """
    Verb in class name as instruction to usage

    Example:
        from noseapp.datastructures import ModifyDict as Context
    """

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(
                '"{}" does not have "{}" attribute.'.format(self.__class__.__name__, item),
            )

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError:
            raise AttributeError(
                '"{}" does not have "{}" attribute.'.format(self.__class__.__name__, item),
            )


class Context(ModifyDict):
    """
    Class for creating context object.

    Usage:

        >>> ctx = Context(a=1, b=2)
        >>> ctx.a
        >>> 1
        >>> ctx.ab = 3
        >>> ctx.ab
        >>> 3
        >>> ctx['a']
        >>> 1
        >>> ctx.get('c')
        >>> None
    """
    pass
