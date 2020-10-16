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


def valid_string(str):
    if not str:
        return False
    not_empty = False
    # print(str)
    for c in str:
        if (c <= 'z' and c >= 'a') or (c <= 'Z' and c >= 'A'):
            not_empty = True
    return not_empty


class Produce:

    def __init__(self, item):
        self.__itemName, self.__id, self.__category, self.__subcategory, self.__storageType, self.__unopened, \
        self.__expirationLowerBound, self.__expirationUpperBound, self.__expirationUnitType, self.__expirationDate = item

    def __getitem__(self, item):
        return getattr(self, 'expirationLowerBound')

    @property
    def itemName(self):
        return self.__itemName

    @property
    def expirationLowerBound(self):
        return self.__expirationLowerBound

    @property
    def expirationUnitType(self):
        return self.__expirationUnitType

    @property
    def expirationDate(self):
        return self.__expirationDate

    @property
    def id(self):
        return self.__id

    def return_as_tuple(self):
        return (self.__itemName, self.__id, self.__category, self.__subcategory, self.__storageType, self.__unopened, \
        self.__expirationLowerBound, self.__expirationUpperBound, self.__expirationUnitType, self.__expirationDate)