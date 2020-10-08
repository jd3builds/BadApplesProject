import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from android_app.utilities import SwipeListener

kivy.require('1.11.1')


class Manager(ScreenManager):
    """
    swipe_listener = SwipeListener()

    def on_touch_down(self, touch):
        self.swipe_listener.set_initial(touch.x)

    def on_touch_up(self, touch, *args):
        direction = self.swipe_listener.get_swipe_direction(touch.x)
        if direction == 'right':
    """
    pass


class LandingPage(Screen):
    pass


class PantryPage(Screen):
    pass


class IdeasPage(Screen):
    pass


class SettingsPage(Screen):
    pass


class AboutPage(Screen):
    pass


style = Builder.load_file('pages.kv')


class BadApplesApp(App):
    def build(self):
        return style


if __name__ == "__main__":
    BadApplesApp().run()
