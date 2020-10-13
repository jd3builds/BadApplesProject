import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy import utils
from android_app.utilities import SwipeListener


kivy.require('1.11.1')


class Manager(ScreenManager):
    swipe_listener = SwipeListener(5)

    def on_touch_down(self, touch):
        self.swipe_listener.set_initial(touch.x)
        super(Manager, self).on_touch_down(touch)  # Completes other on_touch_down arguments (buttons)

    def on_touch_up(self, touch, *args):
        swipe_direction = self.swipe_listener.get_swipe_direction(touch.x)
        if swipe_direction == 'left':
            self.current = self.next()
        elif swipe_direction == 'right':
            self.current = self.previous()


class LandingPage(Screen):
    pass


class PantryPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.pantry_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')
        self.ids.scroll_menu.add_to_menu('Apple', '2 Weeks', 4)  # TODO TEST ONLY


class IdeasPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.ideas_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


class SettingsPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.settings_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


class AboutPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.about_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


class MenuItem(BoxLayout):
    def __init__(self, name, time_remaining, quantity=1, **kwargs):
        super().__init__(**kwargs)
        self.ids.produce_label.text = name + ' (' + str(quantity) + ')'
        self.ids.expiration_label.text = time_remaining

    #   Decreases the quantity of the MenuItem by one or deletes MenuItem if quantity is only one
    # TODO Decrement by one
    def decrement_quantity(self, *args):
        self.parent.remove_widget(self)


class ScrollMenu(ScrollView):

    # Adds a MenuItem to the ScrollMenu
    def add_to_menu(self, name, time_remaining, quantity=1):
        new_menu_item = MenuItem(name, time_remaining, quantity)
        self.ids.grid_layout.add_widget(new_menu_item)


class BadApplesApp(App):
    def build(self):
        root = Builder.load_file('style.kv')
        return root


if __name__ == "__main__":
    BadApplesApp().run()
