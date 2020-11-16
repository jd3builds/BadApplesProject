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


# ---------------------------------- Screen Classes ---------------------------------- #

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
    produce_list = []  # list of type Produce, containing all items from useritems.db
    title_widgets = []  # list of all default title bar widgets

    # Sorting variables
    sort_method = None  # sort function most recently called (or default)
    last_search = None  # the last text searched by user

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Query all produce from the database and append them to the produce list.
        all_items = query_all_user_item()
        for item in all_items:
            self.produce_list.append(Produce(item))

        # Query settings database for default sort option TODo
        pantrySort = query_settings()[0][1]
        if pantrySort == 0:
            self.sort_method = self.sort_by_expiration
            self.exp_sort_ascend = True
            self.title_sort_ascend = True
        elif pantrySort == 1:
            self.sort_method = self.sort_by_expiration
            self.exp_sort_ascend = False
            self.title_sort_ascend = True
        elif pantrySort == 2:
            self.sort_method = self.sort_by_title
            self.title_sort_ascend = True
            self.exp_sort_ascend = True
        else:
            self.sort_method = self.sort_by_title
            self.title_sort_ascend = False
            self.exp_sort_ascend = True

    # Event function called just before pantry page is entered.
    def on_pre_enter(self, *args):
        self.ids.nav_bar.ids.pantry_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')

        # Reset title bar if search bar is on screen
        if type(self.ids.title_bar.children[0]) == SearchBar:
            self.reset_title_bar()

        # TODO sort by currently selected sorting option
        self.sort_method() if self.sort_method != self.sort_by_search else self.sort_method(self.last_search)

        # self.build_pantry_menu()

    # Sorts the produce_list in ascending order of expiration, unless sort=False. The scroll menu is then cleared, and
    # a new menu item is added to the scroll menu for each item in produce_list.
    def build_pantry_menu(self):
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

        image_text = image_text.lower()
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
        if text is None or len(text) == 0:
            return

        match = match_item(text)
        if match is not None:
            match_id = insert_user_table(match)
            self.produce_list.append(Produce(query_user_item_by_id(match_id)[0]))

            # TODO sort by currently selected sorting option, pass text param if by search
            self.sort_method() if self.sort_method != self.sort_by_search else self.sort_method(self.last_search)

            # self.build_pantry_menu()
            self.ids.title_text.text = 'Produce Added Successfully!'
            self.ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)

        else:
            self.ids.title_text.text = 'Failed to Add Produce!'
            self.ids.title_text.color = utils.get_color_from_hex('#FFFFFF')
            Clock.schedule_once(self.parent.children[0].reset_title, 3)

    # Displays search box
    def display_search(self):

        # Add the default widgets to title_widgets, if it has not already been done.
        if len(self.title_widgets) == 0:
            for widget in self.ids.title_bar.children:
                self.title_widgets.append(widget)

        self.ids.title_bar.clear_widgets()
        self.ids.title_bar.add_widget(SearchBar())

    # Clears all widgets from the title bar, and inserts all of the widgets inside title_widgets (the default widgets).
    def reset_title_bar(self):
        self.ids.title_bar.clear_widgets()
        for widget in reversed(self.title_widgets):
            self.ids.title_bar.add_widget(widget)

    # TODO set search as sort_method and update last search
    # Pantry_list is re-ordered by a match ratio, in which items in the pantry_list that are most similar to the input
    # are ordered first. The pantry scroll menu is then rebuilt with this new ordering. Since produce_list stores
    # Produce objects and search_items takes a list, produce_list is converted to a list of lists. After the list is
    # reordered by search, convert produce_list back to a list of produce items.
    def sort_by_search(self, text):
        self.produce_list = [item.return_as_list() for item in self.produce_list]
        self.produce_list = search_item(text, self.produce_list, 0)
        self.produce_list = [Produce(item) for item in self.produce_list]
        self.build_pantry_menu()

        # TODO
        self.sort_method = self.sort_by_search
        self.last_search = text

    # TODO implement ascend vs descend; and set as sort_method; and last_exp_sort
    def sort_by_expiration(self, button_press=False):

        if button_press:
            if self.sort_method == self.sort_by_expiration:
                self.exp_sort_ascend = not self.exp_sort_ascend
            else:
                self.exp_sort_ascend = True
                self.sort_method = self.sort_by_expiration

        self.produce_list = sorted(self.produce_list,
                                   key=lambda x: int((dt.fromisoformat(x.expirationDate) - dt.today()).days),
                                   reverse=not self.exp_sort_ascend)

        self.build_pantry_menu()

    # TODO
    def sort_by_title(self, button_press=False):

        if button_press:
            if self.sort_method == self.sort_by_title:
                self.title_sort_ascend = not self.title_sort_ascend
            else:
                self.title_sort_ascend = True
                self.sort_method = self.sort_by_title

        self.produce_list = sorted(self.produce_list,
                                   key=lambda x: x.itemName,
                                   reverse=not self.title_sort_ascend)

        self.build_pantry_menu()


class IdeasPage(Screen):
    history_list = []  # list of all produce items that have been used or expired
    title_widgets = []  # list of all default title bar widgets

    # Sorting variables todo
    sort_method = None
    last_search = None

    # todo
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ideasSort = query_settings()[0][2]
        if ideasSort == 0:
            self.sort_method = self.sort_by_recommendation
            self.rec_sort_ascend = True
            self.title_sort_ascend = True
        elif ideasSort == 1:
            self.sort_method = self.sort_by_recommendation
            self.rec_sort_ascend = False
            self.title_sort_ascend = True
        elif ideasSort == 2:
            self.sort_method = self.sort_by_title
            self.title_sort_ascend = True
            self.rec_sort_ascend = True
        else:
            self.sort_method = self.sort_by_title
            self.title_sort_ascend = False
            self.rec_sort_ascend = True

    # Event function called when user navigates to ideas page. Clears all of the menu items from history_list and
    # the scroll menu. All recent expirations are then queried from the database and added to the scroll menu.
    def on_pre_enter(self, *args):
        self.ids.nav_bar.ids.ideas_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')

        # Reset title bar if search bar is on screen
        if type(self.ids.title_bar.children[0]) == SearchBar:
            self.reset_title_bar()

        self.history_list = query_all_recent_expiration_items()

        # todo
        self.sort_method() if self.sort_method != self.sort_by_search else self.sort_method(self.last_search)

        # self.build_ideas_menu()

    # Clears all widgets currently in the scroll menu, and then adds all items currently in the history_list to the
    # scroll menu.
    def build_ideas_menu(self):
        self.ids.ideas_scroll_menu.ids.grid_layout.clear_widgets()

        for item in self.history_list:
            self.ids.ideas_scroll_menu.add_to_menu(item)

    # Displays search box
    def display_search(self):

        # Add the default widgets to title_widgets, if it has not already been done.
        if len(self.title_widgets) == 0:
            for widget in self.ids.title_bar.children:
                self.title_widgets.append(widget)

        self.ids.title_bar.clear_widgets()
        self.ids.title_bar.add_widget(SearchBar())

    # Clears all widgets from the title bar, and inserts all of the widgets inside title_widgets (the default widgets).
    def reset_title_bar(self):
        self.ids.title_bar.clear_widgets()
        for widget in reversed(self.title_widgets):
            self.ids.title_bar.add_widget(widget)

    # History_list is re-ordered by a match ratio, in which items in the history_list that are most similar to the
    # input are ordered first. The ideas menu is then rebuilt with this new ordering.
    def sort_by_search(self, text):
        self.history_list = search_item(text, self.history_list, 1)
        self.build_ideas_menu()

        # todo
        self.sort_method = self.sort_by_search
        self.last_search = text

    # todo
    def sort_by_recommendation(self, button_press=False):

        if button_press:
            if self.sort_method == self.sort_by_recommendation:
                self.rec_sort_ascend = not self.rec_sort_ascend
            else:
                self.rec_sort_ascend = True
                self.sort_method = self.sort_by_recommendation

        self.history_list = sorted(self.history_list,
                                   key=lambda x: x[2].count("1") - x[2].count("2"),
                                   reverse=self.rec_sort_ascend)

        self.build_ideas_menu()

    # TODO
    def sort_by_title(self, button_press=False):
        if button_press:
            if self.sort_method == self.sort_by_title:
                self.title_sort_ascend = not self.title_sort_ascend
            else:
                self.title_sort_ascend = True
                self.sort_method = self.sort_by_title

        self.history_list = sorted(self.history_list,
                                   key=lambda x: x[1],
                                   reverse=not self.title_sort_ascend)

        self.build_ideas_menu()


class SettingsPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.settings_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


class AboutPage(Screen):
    def on_enter(self, *args):
        self.ids.nav_bar.ids.about_button.canvas.children[0].children[0].rgba = utils.get_color_from_hex('#385E3C')


class InputPage(Screen):

    # Passes text in input box to consider_produce in pantry page.
    def text_entered(self):
        self.parent.children[0].consider_produce(self.ids.produce_input.text.strip())


# ---------------------------------- Widget Classes ---------------------------------- #

class PantryScrollMenu(ScrollView):

    # Adds a PantryMenuItem, with the given name and time remaining, to the scroll menu.
    def add_to_menu(self, name, time_remaining):
        new_menu_item = PantryMenuItem(name, time_remaining)
        self.ids.grid_layout.add_widget(new_menu_item)


class PantryMenuItem(BoxLayout):
    def __init__(self, name, time_remaining, **kwargs):
        super().__init__(**kwargs)
        self.ids.produce_label.text = name
        self.ids.expiration_label.text = time_remaining

        # Change text color to red if the expiration is below threshold
        if int(time_remaining.split()[0]) <= 3:
            self.ids.produce_label.color = utils.get_color_from_hex("#C40233")
            self.ids.expiration_label.color = utils.get_color_from_hex("#C40233")

    # Removes self from PantryScrollMenu and pantry_items. If the item is in tne recent expirations table,
    # the trend values of the item within the table are updated based on the specific button pressed to
    # remove the item.
    # Parameter args[0] is True if the used apple button is pressed, false if the expired apple button is
    # pressed.
    # The pathing here is absolutely atrocious, but there is really no way around it.
    def remove(self, *args):
        calc_index = len(self.parent.children) - 1 - self.parent.children.index(self)  # index of self in produce_list
        holder = query_recent_expiration_item_by_name(
            self.parent.parent.parent.parent.produce_list[calc_index].itemName)

        # Update item if it already exists within the expirations table
        if len(holder) != 0:
            update_recent_expirations_table(holder[0], args[0])

        # Otherwise, add the item to the table
        else:
            insert_recent_expirations_table(self.parent.parent.parent.parent.produce_list[calc_index], args[0])

        delete_user_item(self.parent.parent.parent.parent.produce_list[calc_index].id)
        self.parent.parent.parent.parent.produce_list.pop(calc_index)
        self.parent.remove_widget(self)


class IdeasScrollMenu(ScrollView):

    # Constructs an IdeasMenuItem and adds it to the scroll menu.
    # Parameter item is a tuple, with produce item attributes.
    def add_to_menu(self, item):
        new_menu_item = IdeasMenuItem(item)
        self.ids.grid_layout.add_widget(new_menu_item)


class IdeasMenuItem(BoxLayout):
    def __init__(self, item, **kwargs):
        super().__init__(**kwargs)
        self.ids.produce_label.text = item[1]

        # Calculate ten trend, and applies relevant suggestions.
        count = item[2].count("1") - item[2].count("2")
        if count > 5:
            self.ids.suggestion_label.text = "Buy more!"
            self.ids.recent_trend_label.text = "Very Low"
            self.ids.suggestion_label.color = utils.get_color_from_hex('#536e1c')
            self.ids.recent_trend_label.color = utils.get_color_from_hex('#536e1c')
            self.ids.produce_label.color = utils.get_color_from_hex('#536e1c')
            self.ids.lifetime_trend_label.color = utils.get_color_from_hex('#536e1c')
        elif count > 2:
            self.ids.suggestion_label.text = "Buy a little more"
            self.ids.recent_trend_label.text = "Low"
        elif count > -3:
            self.ids.suggestion_label.text = "Keep it up!"
            self.ids.recent_trend_label.text = "Neutral"
        elif count > -6:
            self.ids.suggestion_label.text = "Buy a little less"
            self.ids.recent_trend_label.text = "High"
        else:
            self.ids.suggestion_label.text = "Buy less!"
            self.ids.recent_trend_label.text = "Very High"
            self.ids.suggestion_label.color = utils.get_color_from_hex("#C40233")
            self.ids.recent_trend_label.color = utils.get_color_from_hex('#C40233')
            self.ids.produce_label.color = utils.get_color_from_hex('#C40233')
            self.ids.lifetime_trend_label.color = utils.get_color_from_hex('#C40233')

        # Lifetime trend feedback
        if item[3] > 15:
            self.ids.lifetime_trend_label.text = "Very Low"
        elif item[3] > 5:
            self.ids.lifetime_trend_label.text = "Low"
        elif item[3] > -5:
            self.ids.lifetime_trend_label.text = "Neutral"
        elif item[3] > -15:
            self.ids.lifetime_trend_label.text = "High"
        else:
            self.ids.lifetime_trend_label.text = "Very High"


class SearchBar(BoxLayout):

    # Event function that is called when the submit button on any SearchBar is pressed. Input text is
    # formatted, and if non-empty, passed to its respective order_by_search function. The parent class's
    # title bar is also reset. Any screen that has a SearchBar must have these exact functions and ids.
    def submit(self):
        text = self.ids.input_box.text.strip()

        if text != "":
            self.parent.parent.parent.sort_by_search(text)

        self.parent.parent.parent.reset_title_bar()


# ---------------------------------- Driver Functions ---------------------------------- #

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
