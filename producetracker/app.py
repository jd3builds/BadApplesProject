import re

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy import utils
from producetracker.utilities import SwipeListener, Produce, valid_string
# from producetracker.installer import installer
from producetracker.database import *
import os
import os.path
import sys

import kivy.resources
kivy.resources.resource_add_path(os.path.join(os.path.dirname(__file__), 'resources'))

from PIL import Image

import pytesseract

pytesseract.tesseract_cmd = r'../pytesseract/tesseract'

kivy.require('1.11.1')


class Manager(ScreenManager):

    swipe_listener = SwipeListener(5)

    def on_touch_down(self, touch):
        if self.current != 'input':
            self.swipe_listener.set_initial(touch.x)
        super(Manager, self).on_touch_down(touch)  # Completes other on_touch_down arguments (buttons)

    def on_touch_up(self, touch, *args):
        swipe_direction = None
        if self.current != 'input':
            swipe_direction = self.swipe_listener.get_swipe_direction(touch.x)
        if swipe_direction == 'left':
            self.current = self.next()
            if self.current == 'input':
                self.current = self.next()
        elif swipe_direction == 'right':
            self.current = self.previous()
            if self.current == 'input':
                self.current = self.previous()


class LandingPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def capture(self):
        camera = self.ids['camera']
        camera.export_to_png("IMG_SCANNED.png")


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

    # sorts produce_list, clears the scroll_menu, then adds all items from produce_list to scroll_menu+
    def reset_list(self):
        self.produce_list = sorted(self.produce_list,
                                   key=lambda x: int((dt.fromisoformat(x.expirationDate) - dt.today()).days),
                                   reverse=False)
        self.ids.scroll_menu.ids.grid_layout.clear_widgets()
        for item in self.produce_list:
            self.ids.scroll_menu.add_to_menu(str(item.itemName), (
                    str((dt.fromisoformat(item.expirationDate) - dt.today()).days + 1) + ' day(s)'), item.id)

    def reset_title(self, *args):
        self.ids.title_text.text = 'Pantry'
        self.ids.title_text.color = utils.get_color_from_hex('#000000')

    def read_image(self):
        ret_str = pytesseract.image_to_string(Image.open('IMG_SCANNED.png'))
        ret_str = ret_str.lower()
        ret_str = ret_str.lower()

        re.sub(r'[^A-Za-z ]+', '', ret_str)
        list_entries = ret_str.splitlines()
        list_entries = list(filter(lambda item: valid_string(item), list_entries))
        if len(list_entries) == 0:
            self.ids.title_text.text = 'Scan Failed!'
            self.ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)
        for item in list_entries:
            self.text_passed(text=item)

    def text_passed(self, text=None):
        if text is None:
            ret_item = match_item(self.ids.produce_input.text)
        else:
            ret_item = match_item(text)
        if ret_item is not None:
            id_ret = insert_user_table(ret_item)
            self.produce_list.append(Produce(query_user_item_by_id(id_ret)[0]))
            self.reset_list()
            self.ids.title_text.text = 'Produce Added Successfully!'
            self.ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)
        else:
            self.ids.title_text.text = 'Failed to Add Produce!'
            self.ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)


class IdeasPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.ideas_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


class SettingsPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.settings_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


class AboutPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.about_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


class InputPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def read_image(self):
        ret_str = pytesseract.image_to_string(Image.open('IMG_SCANNED.png'))
        ret_str.split()
        re.sub(r'[^A-Za-z ]+', '', ret_str)
        list_entries = ret_str.splitlines()
        list_entries = list(filter(lambda item: valid_string(item), list_entries))
        for item in list_entries:
            self.text_entered(text=item)

    def text_entered(self, text=None):
        if text is None:
            ret_item = match_item(self.ids.produce_input.text)
        else:
            ret_item = match_item(text)
        if ret_item is not None:
            id_ret = insert_user_table(ret_item)
            self.parent.children[0].produce_list.append(Produce(query_user_item_by_id(id_ret)[0]))
            self.parent.children[0].reset_list()
            self.parent.children[0].ids.title_text.text = 'Produce Added Successfully!'
            self.parent.children[0].ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)
        else:
            self.parent.children[0].ids.title_text.text = 'Failed to Add Produce!'
            self.parent.children[0].ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)


class MenuItem(BoxLayout):
    def __init__(self, name, time_remaining, quantity=1, **kwargs):
        super().__init__(**kwargs)
        self.ids.produce_label.text = name
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

        # Change text color to red if expiration below threshold
        if int(time_remaining.split()[0]) <= 3:
            self.ids.grid_layout.children[0].ids.produce_label.color = utils.get_color_from_hex("#C40233")
            self.ids.grid_layout.children[0].ids.expiration_label.color = utils.get_color_from_hex("#C40233")


class BadApplesApp(App):
    def build(self):
        root = Builder.load_file(os.path.join(os.path.dirname(__file__), 'style.kv'))
        return root

def main():
    os.system("sudo apt-get install xclip xsel")
    os.system("sudo apt install tesseract-ocr")
    os.system("sudo apt-get remove gstreamer1.0-alsa gstreamer1.0-libav gstreamer1.0-plugins-bad gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-pulseaudio libgstreamer-plugins-bad1.0-0 libgstreamer-plugins-base1.0-0 libgstreamer-plugins-good1.0-0 libgstreamer1.0-0")

    BadApplesApp().run()

if __name__ == "__main__":
    main()
