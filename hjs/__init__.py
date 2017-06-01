# coding: utf-8
"""
A thin wrapper around [hjson](http://github.com/hjson/hjson-py).
>>> from __future__ import unicode_literals
>>> from hjs import hjs, dumps, loads, dump, load
>>> da = hjs('''
... {
...    a: 1
...    b: are you ok with it ?
...    t: {
...        a: you get the point, now :-)
...    },
...    values: 42
... }
... ''')
>>> assert da['values'] == 42
>>> assert da.t.a == "you get the point, now :-)"

>>> "hum, what if i put an é in this ?"
'hum, what if i put an é in this ?'
"""
from __future__ import unicode_literals
from functools import wraps
from collections import OrderedDict
import hjson
import six
from .version import __version__  # noqa: F401


class hjs(OrderedDict):
    """
    TODO ;-)
    """
    def __init__(self, *args, **kwargs):
        try:
            super(hjs, self).__init__(*args, **kwargs)
        except ValueError:
            if args and isinstance(args[0], six.string_types):
                super(hjs, self).__init__()
                base = hjson.loads(args[0], object_pairs_hook=self.__class__)
                self.update(base)
                self.update(kwargs)
            else:
                raise

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
            self.__setitem__(name, value)

    def __dir__(self):
        return self.keys()

    def __repr__(self):
        return 'hjs("""\n%s""")' % hjson.dumps(self).encode('utf-8')

    def _repr_pretty_(self, p, cycle):
        p.text(repr(self))


def adapt_loader(fun):

    @wraps(fun)
    def with_my_object_pairs_hook(*args, **kwds):
        hook = kwds.get('object_pairs_hook')
        if hook is None or hook is OrderedDict:
            kwds['object_pairs_hook'] = hjs
        return fun(*args, **kwds)

    return with_my_object_pairs_hook


loads = adapt_loader(hjson.loads)  # noqa: F401
load = adapt_loader(hjson.load)    # noqa: F401


def dumps(obj, human=False, **kw):
    if human:
        return hjson.dumps(obj, **kw)
    else:
        return hjson.dumpsJSON(obj, **kw)


def dump(obj, fp, human=False, **kw):
    if human:
        return hjson.dump(obj, fp, **kw)
    else:
        return hjson.dumpsJSON(obj, fp, **kw)
