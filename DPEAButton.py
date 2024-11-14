from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
import os.path

dpea_button_kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "", "../../../EarthquakeSim/DPEAButton.kv")
Builder.load_file(dpea_button_kv_path)

class DPEAButton(Button):
    """
    DPEAButton class
    """
    shadow_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "shadow.png")
    shadow_path = ObjectProperty(shadow_image_path)

    def __init__(self, **kwargs):
        """
        Specifies the background_color, background_normal, and size_hint for all instances
        :param kwargs: Arguments passed to the Button Instance
        """
        super(DPEAButton, self).__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.size_hint = (None, None)
        self.original_colors = list()

    def on_press(self):
        """
        Overrides the Button default on_press to darken the color of the button.
        :return: None
        """
        super(DPEAButton, self).on_press()
        self.original_colors = self.color
        self.color = [i * 0.7 for i in self.original_colors]

    def on_touch_up(self, touch):
        """
        Overrides the Button default on_touch_up to revert the buttons color back to its original color.
        NOTE: This method is called for every widget onscreen
        :return: None
        """
        super(DPEAButton, self).on_touch_up(touch)

        # If button hasn't been pressed self.original colors is empty and will make the button color be black
        # So if the length is empty it hasn't been pressed so we return
        if len(self.original_colors) == 0:
            return

        self.color = self.original_colors
