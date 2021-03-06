##    Copyright 2012 Garrett Beaty
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Function for declaring enumerations."""

import inspect
import warnings

from . import Integer

def __str__(self):
    try:
        return self._ENUM_MAP[self]
    except KeyError:
        return int.__str__(self)

def __repr__(self):
    try:
        return self._ENUM_MAP[self]
    except KeyError:
        return '%s(%s)' % (self.__class__.__name__,
                           self.OPTIONS.get('numeric_repr', int.__repr__)(self))

def enum(classname, options={}, **kwargs):
    """Declare an enumeration.

    classname -- The name of the enum type.
    options -- A dictionary containing options that affect the behavior of the
    enum type.
    Supported options are:
        numeric_repr -- A callable object that takes an integer argument and
        returns a string representation, used for values that have no associated
        enum variable.
    kwargs -- Each keyword is the name of an enum variable, with its value being
    its associated integer value. The enum variables are defined in the global
    scope of the calling module. The string representation of an enum object
    will be the keyword associated with the value. Any repeated values or values
    that cannot be converted to an integer will result in warnings without
    declaring the associated enum variable. Arbitrary objects of the type can
    be created, with the string representation using the keyword name if it has
    the associated value or just the numeric value of the object otherwise.
    """
    module_globals = inspect.currentframe().f_back.f_globals

    cls = type(classname, (Integer,),
               dict(_ENUM_MAP={},
                    OPTIONS=options,
                    __str__=__str__,
                    __repr__=__repr__,
                    ))
    module_globals[classname] = cls

    for name, value in kwargs.iteritems():
        try:
            v = int(value)
            if value != v:
                raise ValueError
            value = v
        except ValueError:
            warnings.warn(
                'Non-integer enum value %r provided for enum variable %s'
                % (value, name), SyntaxWarning, 2)
            continue

        if value in cls._ENUM_MAP:
            warnings.warn(
                'Enum value %s repeated at enum variable %s'
                % (value, name), SyntaxWarning, 2)
            continue

        module_globals[name] = cls(value)
        cls._ENUM_MAP[value] = name
