import array
import math
from numbers import Number
NUMERICAL = Number

class VecBase:
    """
    Base class for vectors
    """
    __slots__ = tuple()
    def __eq__(self, other):
        try:
            if len(self) != len(other):
                return False

            for x, y in zip(self, other):
                if x != y:
                    return False
            return True
        except Exception:
            return False

    def __str__(self):
        return ", ".join(map(str, self))

    def __repr__(self):
        return "Vec(" + ", ".join(map(str, self)) + ")"

    def map_by_verticle(self, other, function: callable):
        assert len(self) == len(other), "wrong dimensions"
        return self.__class__(*[function(x, y) for x, y in zip(self, other)])

    def dot(self, other: "VecBase"):
        """
        Vector dot product
        """
        return sum((v1 * v2 for v1, v2 in zip(self, other)))

    def __add__(self, other):
        #return self.map_by_verticle(other, lambda x, y: x + y)
        try:
            return self.__class__(*[v1+v2 for v1, v2 in zip(self, other)])
        except Exception as e:
            raise ValueError(f"Could not add {repr(self)} to {repr(other)}") from e

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        try:
            return self.map_by_verticle(other, lambda x, y: x - y)
        except Exception as e:
            raise ValueError(f"Could not substract {other} from {self}") from e

    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        if isinstance(other, VecBase):
            return self.map_by_verticle(other, lambda x, y: x * y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(*map(lambda x: x * other, self))
        else:
            return NotImplemented

    def __imul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, VecBase):
            return self.map_by_verticle(other, lambda x, y: x / y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(*map(lambda x: x / other, self))
        else:
            raise TypeError("Cannot true divide vector by " + str(type(other)))

    def __itruediv__(self, other):
        return self.__truediv__(other)

    def __floordiv__(self, other):
        if isinstance(other, VecBase):
            return self.map_by_verticle(other, lambda x, y: x / y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(*map(lambda x: x // other, self))
        else:
            raise TypeError("Cannot floor divide vector by " + str(type(other)))

    def __ifloordiv__(self, other):
        return self.__floordiv__(other)

    def __pos__(self):
        return self.__class__(*self)

    def __neg__(self):
        return self.__class__(*map(lambda x: -x, self))

    def __abs__(self):
        return self.__class__(*map(abs, self))

    def normalized(self):
        """
        Returns a normalized copy of vector.
        """
        ln = self.len()
        if ln != 0:
            return self.__class__(*map(lambda x: x / ln, self))
        else:
            return self.copy()

    def len_sqr(self):
        """
        Returns vector length, squared.
        """
        return math.fsum(map(lambda x: x ** 2, self))

    def len(self):
        """
        Returns vector length.
        """
        return math.sqrt(self.len_sqr())

    def to_tuple(self):
        return tuple(self._v)

    def bytes(self, dtype="f"):
        return array("f", self).tobytes()

    def normalize(self):
        """
        Normalizes vector in-place.
        """
        ln = self.len()
        if ln != 0:
            for i, e in enumerate(self):
                self[i] = e / ln
        return ln

    def as_n_d(self, n):
        if n <= len(self):
            return self.__class__(self._v[:n])
        else:
            return self.__class__(self._v + ([0] * (n - len(self))))

    def in_box(self, a, b):
        return all(av <= v <= bv for v, av, bv in zip(self, a, b))

    def clamped(self, max_ln):
        ln = self.len()
        if ln > max_ln:
            return self / ln * max_ln
        else:
            return self.copy()


class Vec2(VecBase):
    """
    2-dimensional vector. Faster than **Vec**. Inherits **VecBase**.
    """
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __len__(self):
        return 2

    def __iter__(self):
        return iter((self.x, self.y))

    def __reversed__(self):
        return [self.y, self.x]

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise KeyError("Index can be one of 0, 1 for vec2 (%s passed)" % key)

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
            return
        if key == 1:
            self.y = value
            return
        raise KeyError("Index can be one of 0, 1 for vec2 (%s passed)" % key)

    def __add__(self, oth):
        return Vec2(self.x+oth.x, self.y+oth.y)

    def __neg__(self):
        return self.__class__(-self.x, -self.y)

    @property
    def angle(self) -> float:
        return math.atan2(self.y, self.x)

    @angle.setter
    def angle(self, value):
        l = self.len()
        self.x, self.y = math.cos(value)*l, math.sin(value)*l

    def rotate(self, angle) -> "Vec2":
        """
        Rotate vector by *angle* degrees
        """
        c = self.angle + angle
        l = self.len()
        return Vec2(math.cos(c)*l, math.sin(c)*l)

    def perpendicular(self):
        y = self.x
        x = self.y
        return Vec2(-x, y)

    def copy(self):
        return Vec2(self.x, self.y)