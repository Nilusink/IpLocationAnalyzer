"""
File:
math.py

defines mathematical functions used for the program

Author:
Nilusink
"""
from ursina import Entity
import typing as tp
import numpy as np


class Vec3:
    """
    Simple 3D vector class
    """
    x: float
    y: float
    z: float
    angle_xy: float
    angle_xz: float
    length_xy: float
    length: float

    def __init__(self):
        self.__x: float = 0
        self.__y: float = 0
        self.__z: float = 0
        self.__angle_xy: float = 0
        self.__angle_xz: float = 0
        self.__length_xy: float = 0
        self.__length: float = 0

    @property
    def x(self) -> float:
        return self.__x

    @x.setter
    def x(self, value: float) -> None:
        self.__x = value
        self.__update("c")

    @property
    def y(self) -> float:
        return self.__y

    @y.setter
    def y(self, value: float) -> None:
        self.__y = value
        self.__update("c")

    @property
    def z(self) -> float:
        return self.__z

    @z.setter
    def z(self, value: float) -> None:
        self.__z = value
        self.__update("c")

    @property
    def cartesian(self) -> tp.Tuple[float, float, float]:
        """
        :return: x, y, z
        """
        return self.x, self.y, self.z

    @cartesian.setter
    def cartesian(self, value: tp.Tuple[float, float, float]) -> None:
        """
        :param value: (x, y, z)
        """
        self.__x, self.__y, self.__z = value
        self.__update("c")

    @property
    def angle_xy(self) -> float:
        return self.__angle_xy

    @angle_xy.setter
    def angle_xy(self, value: float) -> None:
        self.__angle_xy = self.normalize_angle(value)
        self.__update("p")

    @property
    def angle_xz(self) -> float:
        return self.__angle_xz

    @angle_xz.setter
    def angle_xz(self, value: float) -> None:
        self.__angle_xz = self.normalize_angle(value)
        self.__update("p")

    @property
    def length_xy(self) -> float:
        """
        can't be set
        """
        return self.__length_xy

    @property
    def length(self) -> float:
        return self.__length

    @length.setter
    def length(self, value: float) -> None:
        self.__length = value
        self.__update("p")

    @property
    def polar(self) -> tp.Tuple[float, float, float]:
        """
        :return: angle_xy, angle_xz, length
        """
        return self.angle_xy, self.angle_xz, self.length

    @polar.setter
    def polar(self, value: tp.Tuple[float, float, float]) -> None:
        """
        :param value: (angle_xy, angle_xz, length)
        """
        self.__angle_xy = self.normalize_angle(value[0])
        self.__angle_xz = self.normalize_angle(value[1])
        self.__length = value[2]
        self.__update("p")

    @property
    def lat_lon(self) -> "Vec2":
        return Vec2.from_cartesian(self.angle_xz * (180/np.pi), self.angle_xy * (180/np.pi))

    @classmethod
    def from_polar(cls, angle_xy: float, angle_xz: float, length: float) -> "Vec3":
        """
        create a Vec3 from polar form
        """
        v = cls()
        v.polar = angle_xy, angle_xz, length
        return v

    @classmethod
    def from_cartesian(cls, x: float, y: float, z: float) -> "Vec3":
        """
        create a Vec3 from cartesian form
        """
        v = cls()
        v.cartesian = x, y, z
        return v

    @classmethod
    def from_lat_lon(cls, lat: float, lon: float, length: float = 1) -> "Vec3":
        return cls.from_polar(lon * (np.pi / 180), lat * (np.pi / 180), length=length)

    @classmethod
    def from_xy_map(cls, x: float, y: float) -> "Vec3":
        print(f"from: {x, y}\nto: {90 * np.sin(y * np.pi / 2), 180 * x}")
        return cls.from_lat_lon(
            lat=90 * np.sin(y * np.pi / 2),
            lon=180 * x
        )

    def split(self, direction: "Vec3") -> tp.Tuple["Vec3", "Vec3", "Vec3"]:
        """
        calculate the x, y and z components of length facing (angle1, angle2)
        """
        a = direction.angle_xy - self.angle_xy
        b = direction.angle_xz - self.angle_xz
        tmp = np.cos(a) * self.length
        z = np.sin(a) * self.length
        x = np.cos(b) * tmp
        y = np.sin(b) * tmp

        now_collision = Vec3.from_polar(
            angle_xy=direction.angle_xy,
            angle_xz=direction.angle_xz,
            length=x
        )

        now_carry1 = Vec3.from_polar(
            angle_xy=direction.angle_xy - np.pi / 2,
            angle_xz=direction.angle_xz,
            length=y
        )

        now_carry2 = Vec3.from_polar(
            angle_xy=direction.angle_xy,
            angle_xz=direction.angle_xz - np.pi / 2,
            length=z
        )

        return now_collision, now_carry1, now_carry2

    def cross(self, other: "Vec3") -> "Vec3":
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x

        return Vec3.from_cartesian(x, y, z)

    @staticmethod
    def normalize_angle(angle: float) -> float:
        """
        removes "overflow" from an angle
        """
        while angle > 2 * np.pi:
            angle -= 2 * np.pi

        while angle < -2 * np.pi:
            angle += 2 * np.pi

        return angle

    # maths
    def __neg__(self) -> "Vec3":
        self.cartesian = [-el for el in self.cartesian]
        return self

    def __add__(self, other) -> "Vec3":
        if type(other) == Vec3:
            return Vec3.from_cartesian(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

        return Vec3.from_cartesian(x=self.x + other, y=self.y + other, z=self.z + other)

    def __sub__(self, other) -> "Vec3":
        if type(other) == Vec3:
            return Vec3.from_cartesian(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

        return Vec3.from_cartesian(x=self.x - other, y=self.y - other, z=self.z - other)

    def __mul__(self, other) -> "Vec3":
        if type(other) == Vec3:
            return Vec3.from_polar(
                angle_xy=self.angle_xy + other.angle_xy,
                angle_xz=self.angle_xz + other.angle_xz,
                length=self.length * other.length
            )

        return Vec3.from_cartesian(x=self.x * other, y=self.y * other, z=self.z * other)

    def __truediv__(self, other) -> "Vec3":
        return Vec3.from_cartesian(x=self.x / other, y=self.y / other, z=self.z / other)

    # internal functions
    def __update(self, calc_from: str) -> None:
        match calc_from:
            case "p":
                self.__length_xy = np.cos(self.angle_xz) * self.length
                z = np.sin(self.angle_xz) * self.length
                x = np.cos(self.angle_xy) * self.__length_xy
                y = np.sin(self.angle_xy) * self.__length_xy
                self.__x = x
                self.__y = y
                self.__z = z

            case "c":
                self.__length_xy = np.sqrt(self.y**2 + self.x**2)
                self.__angle_xy = np.arctan2(self.y, self.x)
                self.__angle_xz = np.arctan2(self.z, self.x)
                self.__length = np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __repr__(self) -> str:
        return f"<\n" \
               f"\tVec3:\n" \
               f"\tx:{self.x}\ty:{self.y}\tz:{self.z}\n" \
               f"\tangle_xy:{self.angle_xy}\tangle_xz:{self.__angle_xz}\tlength:{self.length}\n" \
               f">"

    # ursina
    def draw(self, *args, **kwargs) -> Entity:
        return Entity(
            *args,
            position=(self.x, self.z, self.y),
            origin=(0, 0, 0),
            **kwargs,
        )


class Vec2:
    x: float
    y: float
    angle: float
    length: float

    def __init__(self) -> None:
        self.__x: float = 0
        self.__y: float = 0
        self.__angle: float = 0
        self.__length: float = 0

    # variable getters / setters
    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value
        self.__update("c")

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value
        self.__update("c")

    @property
    def xy(self):
        return self.__x, self.__y

    @xy.setter
    def xy(self, xy):
        self.__x = xy[0]
        self.__y = xy[1]
        self.__update("c")

    @property
    def angle(self):
        """
        value in radian
        """
        return self.__angle

    @angle.setter
    def angle(self, value):
        """
        value in radian
        """
        value = self.normalize_angle(value)

        self.__angle = value
        self.__update("p")

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value
        self.__update("p")

    @property
    def polar(self):
        return self.__angle, self.__length

    @polar.setter
    def polar(self, polar):
        self.__angle = polar[0]
        self.__length = polar[1]
        self.__update("p")

    # interaction
    def split_vector(self, direction):
        """
        :param direction: A vector facing in the wanted direction
        :return: tuple[Vector in only that direction, everything else]
        """
        a = (direction.angle - self.angle)
        facing = Vec2.from_polar(angle=direction.angle, length=self.length * np.cos(a))
        other = Vec2.from_polar(angle=direction.angle - np.pi / 2, length=self.length * np.sin(a))

        return facing, other

    def copy(self):
        return Vec2().from_cartesian(x=self.x, y=self.y)

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "length": self.length,
        }

    # maths
    def __add__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_cartesian(x=self.x + other.x, y=self.y + other.y)

        return Vec2.from_cartesian(x=self.x + other, y=self.y + other)

    def __sub__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_cartesian(x=self.x - other.x, y=self.y - other.y)

        return Vec2.from_cartesian(x=self.x - other, y=self.y - other)

    def __mul__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_polar(angle=self.angle + other.angle, length=self.length * other.length)

        return Vec2.from_cartesian(x=self.x * other, y=self.y * other)

    def __truediv__(self, other):
        return Vec2.from_cartesian(x=self.x / other, y=self.y / other)

    # internal functions
    def __update(self, calc_from):
        """
        :param calc_from: polar (p) | cartesian (c)
        """
        if calc_from in ("p", "polar"):
            self.__x = np.cos(self.angle) * self.length
            self.__y = np.sin(self.angle) * self.length

        elif calc_from in ("c", "cartesian"):
            self.__length = np.sqrt(self.x**2 + self.y**2)
            self.__angle = np.arctan2(self.y, self.x)

        else:
            raise ValueError("Invalid value for \"calc_from\"")

    def __abs__(self):
        return np.sqrt(self.x**2 + self.y**2)

    def __repr__(self):
        return f"<\n" \
               f"\tVec2:\n" \
               f"\tx:{self.x}\ty:{self.y}\n" \
               f"\tangle:{self.angle}\tlength:{self.length}\n" \
               f">"

    # static methods.
    # creation of new instances
    @staticmethod
    def from_cartesian(x, y) -> "Vec2":
        p = Vec2()
        p.xy = x, y

        return p

    @staticmethod
    def from_polar(angle, length) -> "Vec2":
        p = Vec2()
        p.polar = angle, length

        return p

    @staticmethod
    def from_dict(dictionary: dict) -> "Vec2":
        if "x" in dictionary and "y" in dictionary:
            return Vec2.from_cartesian(x=dictionary["x"], y=dictionary["y"])

        elif "angle" in dictionary and "length" in dictionary:
            return Vec2.from_polar(angle=dictionary["angle"], length=dictionary["length"])

        else:
            raise KeyError("either (x & y) or (angle & length) must be in dict!")

    @staticmethod
    def normalize_angle(value: float) -> float:
        while value > 2 * np.pi:
            value -= 2 * np.pi

        while value < -2 * np.pi:
            value += 2 * np.pi
        return value
