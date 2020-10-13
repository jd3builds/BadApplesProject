import kivy
from kivy.core.window import Window


# Determines direction of user swipe
# set_initial must be called before get_swipe_direction
# 1 / threshold represents the fraction of your window's width that must dragged over to justify a swipe
class SwipeListener:
    def __init__(self, threshold=10):
        self._threshold = threshold
        self.__x1 = None

    def set_initial(self, x1):
        self.__x1 = x1

    # Returns 'left', 'right' if the absolute difference between x1 and x2 are >= threshold,
    # otherwise None is returned
    def get_swipe_direction(self, x2):
        if self.__x1 is None:
            return None

        if abs(x2 - self.__x1) > Window.size[0] / self._threshold:
            if x2 - self.__x1 > 0:
                return 'right'
            return 'left'
        return None
