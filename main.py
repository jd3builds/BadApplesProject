import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
import os
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
#pytesseract.pytesseract.tesseract_cmd = r'./venv/Lib/site-packages/pytesseract'

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
    def capture(self):
        camera = self.ids['camera']
        camera.export_to_png("IMG_TEST.png") #todo make a file name
        print("Captured")
        #print(pytesseract.image_to_string(Image.open('IMG_TEST.png')))
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
        #vibrator.vibrate(10)
        return style


if __name__ == "__main__":
    BadApplesApp().run()
