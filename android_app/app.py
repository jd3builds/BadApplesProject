import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy import utils
from android_app.utilities import SwipeListener, Produce
from operator import itemgetter, attrgetter, methodcaller
from db.database import *

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
    produce_list = []

    # queries all produce from the database and appends them to produce_list
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        all_items = query_all_user_item()

        for item in all_items:
            self.produce_list.append(Produce(item))

    def on_enter(self, *args):
        self.ids.nav_bar.ids.pantry_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')
        self.reset_list()
        # if len(self.produce_list) > len(self.ids.scrollable_menu.ids.grid_layout.children):
        #      self.reset_list()

    def manual_entry_pressed(self):
        into = ('blueberries', 457, 'fruit', 'berries', 'fridge', False, 1, 4, 'days')
        if not insert_user_table(into):
            print("Unable to add. Item with id already exists")
        else:
            self.produce_list.append(Produce(into))
            self.reset_list()

    # sorts produce_list, clears the scroll_menu, then adds all items from produce_list to scroll_menu+
    def reset_list(self):
        self.produce_list = sorted(self.produce_list, key=itemgetter(6), reverse=False)
        self.ids.scroll_menu.ids.grid_layout.clear_widgets()
        for item in self.produce_list:

            self.ids.scroll_menu.add_to_menu(str(item.itemName), (str(item.expirationLowerBound) + " " + str(item.expirationUnitType)), item.id)


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

    def remove(self, *args):
        calc_index = len(self.parent.children) - 1 - self.parent.children.index(self)
        delete_user_item(self.parent.parent.parent.parent.produce_list[calc_index].id)
        self.parent.parent.parent.parent.produce_list.pop(calc_index)  # removes item at calc_index from produce_list
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
