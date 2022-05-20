"""
File:
main.py

Main Program, creates Ursina window

Author:
Nilusink
"""
from threading import Thread
from core.objects import *
from ursina import *


class Window(Ursina):
    def __init__(self) -> None:

        super().__init__()
        self.cam = EditorCamera()

        self.__loaded = False
        self.last_time: dict = deepcopy(held_keys)

        self.__fullscreen = False

        # configure window
        window.windowed_size = window.fullscreen_size
        window.update_aspect_ratio()

        window.title = 'Stuff'
        window.borderless = False
        # window.fullscreen = True
        window.exit_button.visible = True
        window.fps_counter.enabled = True
        window.color = (0, 0, 0, 0)

        Entity(
            model="sphere",
            scale=20 * .99,
            color=(0, 0, 0, .9),
        )

        # set camera position
        camera.x = 0
        camera.y = 0
        camera.z = -20

        self.globe = ...

    def update(self):
        """
        Ursina update function
        """
        if not self.__loaded:
            def tmp():
                self.globe = Globe(size=10, resolution=1.5)
            Thread(target=tmp).start()
            self.__loaded = True

        now = mouse.hovered_entity
        if issubclass(type(now), Server):
            print(now.geolocation)
            print(now.data)

    def end(self) -> None:
        if self.globe is not ...:
            self.globe.end()


if __name__ == "__main__":
    def update() -> None:
        w.update()

    w = Window()
    w.run()
    w.end()
