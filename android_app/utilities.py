import kivy
from kivy.core.window import Window


class SwipeListener:
    def __init__(self, threshold=10):
        self._threshold = threshold
        self.__x1 = None

    def set_initial(self, x1):
        self.__x1 = x1

    def get_swipe_direction(self, x2):
        # Check initial position has been set
        if self.__x1 is None:
            return None

        if abs(x2 - self.__x1) > Window.size[0] / self._threshold:
            if x2 - self.__x1 > 0:
                return 'right'
            return 'left'
        return None
