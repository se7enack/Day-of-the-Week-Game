from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from datetime import datetime, timedelta
from random import randrange

KV = """
<MainScreen>:
    orientation: "vertical"
    spacing: "20dp"
    padding: "30dp"
    md_bg_color: app.theme_cls.bg_normal

    MDLabel:
        id: title_label
        halign: "center"
        theme_text_color: "Primary"
        font_style: "H5"
        text: "Guess the Day of the Week!"

    MDCard:
        orientation: "vertical"
        padding: "20dp"
        radius: 20
        size_hint_y: None
        height: "200dp"
        md_bg_color: app.theme_cls.bg_light

        MDLabel:
            id: question_label
            halign: "center"
            theme_text_color: "Primary"
            font_style: "Body1"
            text: ""

        MDBoxLayout:
            orientation: "horizontal"
            spacing: "10dp"
            size_hint_y: None
            height: "48dp"
            padding: "10dp"

            # Left side: dropdown button
            MDRaisedButton:
                id: dropdown_button
                text: "Day"
                size_hint_x: 0.5
                md_bg_color: app.theme_cls.primary_color
                text_color: 1, 1, 1, 1
                on_release: app.open_menu()  # ✅ Fixed here

            Widget:  # spacer

            # Right side: submit button
            MDRaisedButton:
                text: "Submit"
                size_hint_x: 0.3
                md_bg_color: app.theme_cls.primary_color
                on_release: app.update()

    MDFlatButton:
        text: "Restart"
        pos_hint: {"center_x": 0.5}
        on_release: app.restart()
"""

# Days of the week
options = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def playit(soundfile):
    sound = SoundLoader.load(soundfile)
    if sound:
        sound.play()


def randomDate(startYear, endYear):
    """Generate a random date between the given years."""
    d1 = datetime.strptime(f'1/1/{startYear}', '%m/%d/%Y')
    d2 = datetime.strptime(f'12/31/{endYear}', '%m/%d/%Y')
    delta = d2 - d1
    random_second = randrange(delta.days * 86400)
    x = d1 + timedelta(seconds=random_second)
    return x.strftime('%m/%d/%Y')


def getDay(dateString):
    """Return the day of week for the given date string."""
    dateObject = datetime.strptime(dateString, "%m/%d/%Y").date()
    return options[dateObject.weekday()]


class MainScreen(MDBoxLayout):
    pass


class DayOfWeekGame(MDApp):
    def build(self):
        self.title = "Day Guess Game"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Dark"

        Builder.load_string(KV)
        self.root = MainScreen()

        # Game state setup
        self.startYear = 1975
        self.endYear = 2025
        self.count = 5
        self.points = 0
        self.x = 0
        self.dates = [randomDate(self.startYear, self.endYear) for _ in range(self.count)]

        self.root.ids.question_label.text = self.get_label_text()
        self.selected_day = None

        return self.root

    def get_label_text(self):
        """Update question or show final score."""
        if self.x < self.count:
            return f"{self.x+1} of {self.count}\n\n{self.dates[self.x]}\n"
        else:
            return f"Game Over!\nYou got {self.points} of {self.count} correct!"

    def open_menu(self):
        """Recreate and open the dropdown menu each time (fixes Android bug)."""
        menu_items = [
            {"text": day, "viewclass": "OneLineListItem", "on_release": lambda x=day: self.set_day(x)}
            for day in options
        ]

        self.menu = MDDropdownMenu(
            caller=self.root.ids.dropdown_button,
            items=menu_items,
            width_mult=3,
            position="auto",
            ver_growth="up",
        )

        # Delay helps Android properly position the menu
        Clock.schedule_once(lambda dt: self.menu.open(), 0.05)

    def set_day(self, day):
        """Handle user day selection."""
        self.selected_day = day
        self.root.ids.dropdown_button.text = day
        self.menu.dismiss()

    def update(self):
        """Check answer and move to next date."""
        if self.x >= self.count or not self.selected_day:
            return

        reality = getDay(self.dates[self.x])
        picked = self.selected_day

        if reality == picked:
            self.points += 1
            playit("good.mp3")
        else:
            playit("bad.mp3")

        self.x += 1

        if self.x == self.count:
            # Play final sound
            if self.points == self.count:
                playit("perfect.mp3")
            else:
                playit("fail.mp3")

        self.root.ids.question_label.text = self.get_label_text()

    def restart(self):
        """Restart the game."""
        self.points = 0
        self.x = 0
        self.dates = [randomDate(self.startYear, self.endYear) for _ in range(self.count)]
        self.root.ids.question_label.text = self.get_label_text()
        self.root.ids.dropdown_button.text = "Day"
        self.selected_day = None


if __name__ == "__main__":
    DayOfWeekGame().run()
