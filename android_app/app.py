import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button;

kivy.require('1.11.1')

class BaseApp(App):

    # Function that returns the root widget
    def build(self):

        # Label with text Hello World is
        # returned as root widget
        return Label(text="Hello World !")

    # Here our class is initialized


if __name__ == "__main__":
    BaseApp().run()
