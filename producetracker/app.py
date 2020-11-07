import re
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy import utils
from producetracker.utilities import *
from producetracker.database import *
import os
import os.path
import kivy.resources
from PIL import Image
import pytesseract

kivy.require('1.11.1')
kivy.resources.resource_add_path(os.path.join(os.path.dirname(__file__), 'resources'))
pytesseract.pytesseract.tesseract_cmd = r'../pytesseract/tesseract'


# ----------------- Screen Classes ----------------- #

# Screen manager class that serves as the parent of all the other screen classes.
# Facilitates the transition between screens, as well as any functions that should be
# executed across all screens.
class Manager(ScreenManager):
    swipe_listener = SwipeListener(5)

    # Executed when user presses within display window.
    # Called implicitly by many built-in widgets, such as buttons.
    # Sets the initial coordinates of the SwipeListener.
    # Parameter touch contains the coordinates and angle of the press.
    def on_touch_down(self, touch):
        if self.current != 'input':
            self.swipe_listener.set_initial(touch.x)
        super(Manager, self).on_touch_down(touch)  # completes other on_touch_down arguments (i.e. buttons)

    # Executed when user releases from within display window.
    # Handles the swipe direction, and sets new screen if applicable.
    # Parameter touch contains the coordinates and angle of the release.
    def on_touch_up(self, touch, *args):
        swipe_direction = None
        if self.current != 'input':
            swipe_direction = self.swipe_listener.get_swipe_direction(touch.x)

        if swipe_direction == 'left':
            self.current = self.next()
            if self.current == 'input':  # skip input page
                self.current = self.next()

        elif swipe_direction == 'right':
            self.current = self.previous()
            if self.current == 'input':  # skip input page
                self.current = self.previous()


class LandingPage(Screen):

    # Captures the camera display and saves it as a png to the local directory.
    def capture(self):
        camera = self.ids['camera']
        camera.export_to_png("IMG_SCANNED.png")


class PantryPage(Screen):
    produce_list = []   # list of type Produce, containing all items from useritems.db

    # Queries all produce from the database and appends them to produce_list on launch.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        all_items = query_all_user_item()
        for item in all_items:
            self.produce_list.append(Produce(item))

    # Event function called when pantry page is entered.
    # Highlights relevant nav bar buttons and calls functions that build pantry menu items.
    def on_enter(self, *args):
        self.ids.nav_bar.ids.pantry_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')
        self.build_pantry_menu()

    # Sorts the produce_list in ascending order of expiration. The scroll menu is then cleared, and a new
    # menu item is added to the scroll menu for each item in produce_list.
    def build_pantry_menu(self):
        self.produce_list = sorted(self.produce_list,
                                   key=lambda x: int((dt.fromisoformat(x.expirationDate) - dt.today()).days),
                                   reverse=False)

        self.ids.scroll_menu.ids.grid_layout.clear_widgets()

        for item in self.produce_list:
            self.ids.scroll_menu.add_to_menu(str(item.itemName), (
                    str((dt.fromisoformat(item.expirationDate) - dt.today()).days + 1) + ' day(s)'))

    # Changes the text at the top of the screen back to the default title.
    def reset_title(self, *args):
        self.ids.title_text.text = 'Pantry'
        self.ids.title_text.color = utils.get_color_from_hex('#000000')

    # Passes IMG_SCANNED.png from the local directory to pytesseract, which returns a string.
    # Basic string formatting is then applied, and the validity of the string is verified.
    # Validity in this context refers to the characteristics of the string, not the produce (or anything else)
    # it refers to. Valid text is then passed to consider_produce.
    def read_image(self):
        image_text = pytesseract.image_to_string(Image.open('IMG_SCANNED.png'))

        ret_str = image_text.lower()
        re.sub(r'[^a-z ]+', '', image_text)

        list_entries = image_text.splitlines()
        list_entries = list(filter(lambda item: valid_string(item), list_entries))

        if len(list_entries) == 0:
            self.ids.title_text.text = 'Scan Failed!'
            self.ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)

        for item in list_entries:
            self.consider_produce(text=item)

    # Matches text with an item in the database. If match found, item is added to the produce_list, database, and then
    # the pantry page is rebuilt. Feedback is displayed at top of page to indicate success or failure to user.
    # Parameter text is a candidate for a produce item.
    def consider_produce(self, text):
        if text is None:
            return

        match = match_item(text)
        if match is not None:
            match_id = insert_user_table(match)
            self.produce_list.append(Produce(query_user_item_by_id(match_id)[0]))
            self.build_pantry_menu()
            self.ids.title_text.text = 'Produce Added Successfully!'
            self.ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)

        else:
            self.ids.title_text.text = 'Failed to Add Produce!'
            self.ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)


class IdeasPage(Screen):
    history_list = []

    # Event function called when user navigates to ideas page. Clears all of the menu items from history_list and
    # the scroll menu. All recent expirations are then queried from the database and added to the scroll menu.
    def on_enter(self, *args):
        self.ids.nav_bar.ids.ideas_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')

        self.history_list = query_all_recent_expiration_items()
        self.ids.ideas_scroll_menu.ids.grid_layout.clear_widgets()

        for item in self.history_list:
            self.ids.ideas_scroll_menu.add_to_menu(item)


class SettingsPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.settings_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


class AboutPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.about_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


# TODO continue from here -- fix dupe code
class InputPage(Screen):

    def read_image(self):
        ret_str = pytesseract.image_to_string(Image.open('IMG_SCANNED.png'))
        ret_str.split()
        re.sub(r'[^A-Za-z ]+', '', ret_str)
        list_entries = ret_str.splitlines()
        list_entries = list(filter(lambda item: valid_string(item), list_entries))
        for item in list_entries:
            self.text_entered(text=item)

    # todo compare with consider produce
    def text_entered(self, text=None):
        if text is None:
            self.ids.produce_input.text = self.ids.produce_input.text.strip()

            # Exits function if empty string passed from input page
            if len(self.ids.produce_input.text) == 0:
                return

            ret_item = match_item(self.ids.produce_input.text)
        else:
            ret_item = match_item(text)
        if ret_item is not None:
            id_ret = insert_user_table(ret_item)
            self.parent.children[0].produce_list.append(Produce(query_user_item_by_id(id_ret)[0]))
            self.parent.children[0].build_pantry_menu()
            self.parent.children[0].ids.title_text.text = 'Produce Added Successfully!'
            self.parent.children[0].ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)
        else:
            self.parent.children[0].ids.title_text.text = 'Failed to Add Produce!'
            self.parent.children[0].ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)


# ----------------- Widget Classes ----------------- #

# Pantry ScrollMenu
class PantryScrollMenu(ScrollView):

    # Adds a MenuItem to the ScrollMenu
    def add_to_menu(self, name, time_remaining, quantity=1):
        new_menu_item = PantryMenuItem(name, time_remaining, quantity)
        self.ids.grid_layout.add_widget(new_menu_item)

        # Change text color to red if expiration below threshold
        if int(time_remaining.split()[0]) <= 3:
            self.ids.grid_layout.children[0].ids.produce_label.color = utils.get_color_from_hex("#C40233")
            self.ids.grid_layout.children[0].ids.expiration_label.color = utils.get_color_from_hex("#C40233")


# Pantry ScrollMenu Item
class PantryMenuItem(BoxLayout):
    def __init__(self, name, time_remaining, quantity=1, **kwargs):
        super().__init__(**kwargs)
        self.ids.produce_label.text = name
        self.ids.expiration_label.text = time_remaining

    # if not exist yet, add
    # if exists, update
    def remove(self, *args):
        calc_index = len(self.parent.children) - 1 - self.parent.children.index(self)
        holder = query_recent_expiration_item_by_name(
            self.parent.parent.parent.parent.produce_list[calc_index].itemName)
        if len(holder) != 0:
            # update
            update_recent_expirations_table(holder[0], args[0])
        else:
            # add TODO: Figure out how to create second param
            insert_recent_expirations_table(self.parent.parent.parent.parent.produce_list[calc_index], args[0])

        delete_user_item(self.parent.parent.parent.parent.produce_list[calc_index].id)
        self.parent.parent.parent.parent.produce_list.pop(calc_index)  # removes item at calc_index from produce_list
        self.parent.remove_widget(self)


# Ideas Page Scroll Menu
class IdeasScrollMenu(ScrollView):
    def add_to_menu(self, item):
        new_menu_item = IdeasMenuItem(item)  # id name 10t trend
        self.ids.grid_layout.add_widget(new_menu_item)


# Menu Item of Ideas Page Scroll Menu
class IdeasMenuItem(BoxLayout):
    def __init__(self, item, **kwargs):
        super().__init__(**kwargs)
        self.ids.produce_label.text = item[1]
        self.ids.lifetime_trend_label.text = "+" + str(item[3]) if item[3] > 0 else str(item[3])
        count = item[2].count("1")
        count -= (10 - count)
        if count > 5:
            self.ids.suggestion_label.text = "Buy more!"
            self.ids.suggestion_label.color = utils.get_color_from_hex('#216628')
        elif count > 2:
            self.ids.suggestion_label.text = "Buy a little more"
        elif count > -3:
            self.ids.suggestion_label.text = "Keep it up!"
        elif count > -6:
            self.ids.suggestion_label.text = "Buy a little less"
        else:
            self.ids.suggestion_label.text = "Buy less!"
            self.ids.suggestion_label.color = utils.get_color_from_hex("#C40233")
        self.ids.recent_trend_label.text = "+" + str(count) if count > 0 else str(count)


# ----------------- Driver Functions ----------------- #

class BadApplesApp(App):
    def build(self):
        root = Builder.load_file(os.path.join(os.path.dirname(__file__), 'style.kv'))
        return root


def main():
    # TODO Uncomment the following function calls when preparing final package
    # os.system("sudo apt-get install xclip xsel")
    # os.system("sudo apt install tesseract-ocr")
    # os.system("sudo apt-get remove gstreamer1.0-alsa gstreamer1.0-libav gstreamer1.0-plugins-bad gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-pulseaudio libgstreamer-plugins-bad1.0-0 libgstreamer-plugins-base1.0-0 libgstreamer-plugins-good1.0-0 libgstreamer1.0-0")

    BadApplesApp().run()


if __name__ == "__main__":
    main()
