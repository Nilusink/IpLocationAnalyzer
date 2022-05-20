"""
File:
objects.py

3d objects for rendering in ursina

Author:
Nilusink
"""
from ursina import Vec3 as UVec3, Vec4, Entity, Mesh, load_model
from global_land_mask import globe
from traceback import print_exc
from threading import Timer
import typing as tp
import numpy as np
import time

# "local" imports
from .shapes import line, connection
from .math import Vec2, Vec3
from .ip_tools import *


MARKER: str = "./assets/server.obj"


def print_traceback(func: tp.Callable) -> tp.Callable:
    def wrapper(*args, **kwargs) -> tp.Any:
        try:
            return func(*args, **kwargs)

        except Exception:
            print_exc()
            raise
    return wrapper


class Globe(Entity):
    server_distance_mult: float = 1.4
    view_distance: float = 40
    max_distance: float = 20
    resolution: float = 10
    size: float = 1
    origin: Vec3
    u_lat: float
    u_lon: float

    __globe_done: bool = False

    def __init__(self, size: float = ..., resolution: float = ..., origin: Vec3 = ...) -> None:
        super().__init__(
            model=Mesh(vertices=[], mode="point", static=False, render_points_in_3d=True, thickness=.05)
        )

        self._sub_globes: list[Vec3] = []
        self._sub_globes_colors: list[Vec4] = []
        self._servers: dict[str, Server] = {}
        self._server_pos = []

        if resolution is not ...:
            self.resolution = resolution

        if size is not ...:
            self.size = size

        self._sphere_size = (2 * np.pi * self.size) / (360 / resolution)

        if origin is not ...:
            self.origin = origin

        else:
            self.origin = Vec3()

        self.timer = ...

        self._generate_globe()
        self.draw_current_servers()

    def _generate_globe(self) -> None:
        # equally spaced
        for lat in np.arange(-90, 90 + self.resolution, self.resolution):
            tmp = Vec3.from_lat_lon(lat, lon=0)
            tmp.length = self.size

            r = abs(tmp.x)
            u = 2 * np.pi * r
            n = int(u / (self.resolution * (self.size / (360/(2 * np.pi)))))

            for lon in np.linspace(-180, 180, n):
                if globe.is_land(lat, lon):
                    pos = Vec3.from_lat_lon(lat, lon)
                    pos.length = self.size * 1.5

                    col = .2 + np.random.randint(0, 60) / 100
                    color = Vec4(*([col] * 3), 1)

                    self._sub_globes.append(pos)
                    self._sub_globes_colors.append(color)
        self.__globe_done = True
        # for lat in np.arange(-90, 90 + self.resolution, self.resolution):
        #     for lon in np.arange(-180, 180+self.resolution, self.resolution):
        #         if globe.is_land(lat, lon):
        #             pos = Vec3.from_lat_lon(lat, lon)
        #             pos.length = self.size
        #
        #             col = .2 + np.random.randint(0, 60) / 100
        #             color = Vec4(*([col] * 3), 1)
        #
        #             self._sub_globes.append(pos)
        #             self._sub_globes_colors.append(color)

    def update(self) -> None:
        tmp: list[UVec3] = []
        colors = self._sub_globes_colors.copy()
        tmp_colors: list[Vec4] = []
        # removed because of performance issues
        # cam_p = Vec3.from_cartesian(camera.world_x, camera.world_z, camera.world_y)   # for shader

        for point, color in zip(self._sub_globes.copy(), colors):
            if point.length > self.size:
                point.length -= .05

            # if self.__globe_done:
            #     delta = point - cam_p
            #
            #     vis = (self.max_distance - (delta.length - self.view_distance)) / self.max_distance
            #     vis = vis if vis > 0 else 0
            #     vis = vis if vis < 1 else 1
            #
            #     tmp_colors.append(Vec4(
            #         color[0] * vis,
            #         color[1] * vis,
            #         color[2] * vis,
            #         color[3] * vis
            #     ))
            #
            # else:
            tmp_colors.append(color)

            tmp.append(UVec3(
                point.x,
                point.z,
                point.y
            ))

        self.model.vertices = tmp
        self.model.colors = tmp_colors
        self.model.generate()

    @print_traceback
    def draw_current_servers(self) -> None:
        # user position
        loc = ip_geolocation(get_external_ip())
        self.u_lat, self.u_lon = loc["latitude"], loc["longitude"]

        # draw user
        self.draw_server(self.u_lat, self.u_lon, (0, 1, 0, 1), draw_line=True)

        # draw server
        addresses = get_foreign_addresses()
        for ip, address in addresses:
            print(ip)
            if ip:
                self._servers[ip] = Server(
                    ip, address,
                    size=self._sphere_size,
                    distance=self.size * self.server_distance_mult,
                    world_size=self.size,
                    origin=Vec2.from_cartesian(self.u_lat, self.u_lon)
                )

        for ip, address in addresses:
            if ip:
                self.trace_connection(ip)

        self.timer = Timer(function=self._update_servers, interval=2)
        self.timer.start()

    def _update_servers(self) -> None:
        addresses = get_foreign_addresses()
        for ip, address in addresses:
            if ip:
                if ip not in self._servers:
                    self._servers[ip] = Server(
                        ip, address, size=self._sphere_size, distance=1.4 * self.size,
                        origin=Vec2.from_cartesian(self.u_lat, self.u_lon),
                        world_size=self.size
                    )
                    continue
                self._servers[ip].data = address
                self.timer.cancel()
                self.timer = Timer(function=self._update_servers, interval=5)
                self.timer.start()

    def draw_server(self,
                    lat: float,
                    lon: float,
                    color: tuple[float, float, float, float] = ...,
                    draw_line: bool = False) -> None:

        if color is ...:
            color = (.8, .8, 1, 1)

        pos = Vec3.from_lat_lon(lat, lon)
        pos.length = self.size * 1.3
        self._server_pos.append(pos.draw(
            model="sphere",
            color=color,
            scale=self._sphere_size,
        ))

        if draw_line:
            line([
                pos,
                pos * (self.size / pos.length),
            ],
                thickness=2,
                colors=[(1, 0, 0, 1), (1, 0, 0, 1)]
            )

    @print_traceback
    def trace_connection(self, orig_ip: str) -> None:
        print(f"tracing {orig_ip}")
        process = subprocess.Popen(["traceroute", orig_ip], stdout=subprocess.PIPE)

        i = -1
        last = self.u_lat, self.u_lon
        ip = orig_ip
        for output_line in iter(process.stdout.readline, b""):
            i += 1
            # skip headline
            if i == 0:
                continue

            # get ip in braces
            output_line = output_line.decode()

            if "*" not in output_line:
                ip = output_line.split("(")[1].split(")")[0]
                if ip == orig_ip:
                    break

                print(f"hop: {ip}")

                try:
                    tmp = Server(
                        ip,
                        address={
                            "ip": ip,
                            "state": "traceroute",
                            "traces": orig_ip,
                        },
                        size=self._sphere_size,
                        distance=self.size * self.server_distance_mult,
                        origin=Vec2.from_cartesian(*last),
                        world_size=self.size,
                    )
                    last = tmp.geolocation["latitude"], tmp.geolocation["longitude"]

                except ValueError:
                    print(f"no location for {ip}")

        Server(
            ip,
            address={
                "ip": ip,
                "state": "traceroute target",
            },
            size=self._sphere_size,
            distance=self.size * self.server_distance_mult,
            origin=Vec2.from_cartesian(*last),
            world_size=self.size,
        )

        print(f"done tracing")

    def end(self) -> None:
        self.timer.cancel()


class Server(Entity):
    origin_position: Vec2
    line_speed: float = 10
    geolocation: dict
    distance: float
    line: Entity
    size: float
    pos: Vec3
    ip: str

    def __init__(self, ip: str, address: dict, size: float, distance: float, origin: Vec2, world_size: float) -> None:
        self._init_done = False
        self._time = time.perf_counter()

        self.ip = ip
        self._data = address
        self.size = size
        self.distance = distance
        self.origin_position = origin
        self.geolocation = ip_geolocation(self.ip)

        if self.geolocation["latitude"] == "Not found":
            raise ValueError("Couldn't find ip location")

        self.pos = Vec3.from_lat_lon(
            self.geolocation["latitude"],
            self.geolocation["longitude"],
        )

        lat, lon = self.pos.lat_lon.xy
        rot = (
            lat,
            -90 - lon,
            0
        )

        self.pos.length = distance

        super().__init__(
            model=load_model(MARKER, use_deepcopy=True),
            collider="sphere",
            position=(self.pos.x, self.pos.z, self.pos.y),
            scale=size,
            color=(.8, .8, 1, 1),
            rotation=rot,
            origin=(0, 0, 0)
        )

        self.line = connection(self.pos.lat_lon, origin, distance=distance)
        self._vertices = self.line.model.vertices
        self._colors = len(self._vertices) * [(1, 1, 1, .5)]

        self._ground_line = line([
            self.pos,
            self.pos * (world_size / self.pos.length),
        ], thickness=2)

        self._init_done = True

    @property
    def data(self) -> dict:
        return self._data.copy()

    @data.setter
    def data(self, value: dict) -> None:
        self._data = value

    def update(self) -> None:
        if self._init_done:
            lat, lon = self.pos.lat_lon.xy
            rot = (
                lat,
                -90 - lon,
                time.perf_counter() * 40
            )
            self.rotation = rot

            match self.data["state"]:
                case "ESTABLISHED":
                    now = time.perf_counter()
                    now_colors = self._colors.copy()

                    for i, color in enumerate(now_colors.copy()):
                        g = np.sin(((now + i * 100) - self._time) * self.line_speed)

                        now_colors[-i+1] = (0, g, 0, g**4)

                case "TIME_WAIT":
                    now = time.perf_counter()
                    now_colors = self._colors.copy()

                    for i, color in enumerate(now_colors.copy()):
                        g = np.sin(now * 2) * .5

                        now_colors[i] = (g, g, g, g)

                case "traceroute":
                    now = time.perf_counter()
                    now_colors = self._colors.copy()

                    for i, color in enumerate(now_colors.copy()):
                        r = np.sin(((now + i * 100) - self._time) * self.line_speed)
                        m = abs(np.tan((now + 2) / 2))

                        # normalize g
                        m = 1 if m > 1 else m

                        now_colors[i] = (m * r, .1 * m, .1 * m, m)

                case "traceroute target":
                    now = time.perf_counter()
                    now_colors = self._colors.copy()

                    for i, color in enumerate(now_colors.copy()):
                        r = np.sin(((now + i * 100) - self._time) * self.line_speed)
                        m = abs(np.tan((now + 2) / 2))

                        # normalize g
                        m = 1 if m > 1 else m

                        now_colors[i] = (r * m, r * m, .1 * m, m)

                case _:
                    now_colors = [(0, 0, 0, 0)] * len(self._colors)

            self.line.model.colors = now_colors
            self.line.model.generate()
