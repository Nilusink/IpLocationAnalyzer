"""
File:
shapes.py

used to create simple meshes with ursina

Author:
Nilusink
"""
from ursina import Entity, Mesh, Vec3 as UVec3
from .math import Vec3, Vec2


def line(points: list[Vec3], **kwargs) -> Entity:
    points = [UVec3(p.x, p.z, p.y) for p in points]
    return Entity(model=Mesh(vertices=points, mode='line', **kwargs))


def connection(pos1: Vec2, pos2: Vec2, resolution: float = 2, distance: float = 1.4) -> Entity:
    delta = pos2 - pos1
    n = int(delta.length / resolution)
    n = 1 if not n else n
    delta.length /= n

    points: list[Vec3] = [Vec3.from_lat_lon(*pos1.xy, length=distance)]

    last = pos1
    for _ in range(n):
        last = last + delta
        points.append(Vec3.from_lat_lon(*last.xy, length=distance))

    points.append(Vec3.from_lat_lon(*pos2.xy, length=distance))
    return line(points)
