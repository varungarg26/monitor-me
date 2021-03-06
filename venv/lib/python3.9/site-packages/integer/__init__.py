import sys
if sys.version_info < (3,):
    import weakref

class Integer(int):
    """Base class for custom integer types. The class must be initializable with
    a single argument that is the integer value. The class can be treated as a
    standard int, but arithmetic operations involving the custom integer type
    will by default use the custom integer type as the result type. The exact
    result can be affected by overriding finalize_value, which can be used for
    enforcing values or altering the type of the result.
    """

    INSTANCES = {}

    @classmethod
    def _cls_instances(cls):
        if sys.version_info < (3,):
            default = weakref.WeakValueDictionary()
        else:
            default = {}

        return Integer.INSTANCES.setdefault(cls, default)

    def __new__(cls, val):
        cls_instances = cls._cls_instances()
        return cls_instances.setdefault(val, int.__new__(cls, val))

    def __pow__(self, exponent, mod=None):
        val = int.__pow__(self, exponent, mod)
        # If the second argument is a negative exponent, the result will be a
        # float
        if isinstance(val, int):
            return self.finalize_value(val, '__pow__', exponent, mod)
        return val

    def finalize_value(self, val, fname, *args):
        """Finalizes the value returned from an operation, which can be used for
        enforcing values or altering the type.

        val -- The result value of the operation.
        fname -- The function name of the operation that was performed.
        args -- Any arguments passed to the operation.
        """
        return self.__class__(val)

def _preserve_type(attr):
    fname = '__' + attr + '__'
    f = getattr(int, fname)

    def type_preserver(self, *args):
        val = f(self, *args)
        if val is NotImplemented:
            return val
        return self.finalize_value(val, fname, *args)

    setattr(Integer, fname, type_preserver)

for attr in (
    'add', 'radd',
    'sub', 'rsub',
    'mul', 'rmul',
    'floordiv', 'rfloordiv',
    'mod', 'rmod',
    'divmod', 'rdivmod',
    'and', 'rand',
    'xor', 'rxor',
    'or', 'ror',
    'lshift',
    'rshift',
    'neg',
    'pos',
    'abs',
    'invert',
    ):
    _preserve_type(attr)
