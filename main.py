from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
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

            # Left side: dropdown button only
            MDRaisedButton:
                id: dropdown_button
                text: "Day"
                size_hint_x: 0.5
                md_bg_color: app.theme_cls.primary_color
                text_color: 1, 1, 1, 1
                on_release: app.menu.open()

            Widget:  # flexible spacer

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

options = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def playit(soundfile):
    sound = SoundLoader.load(soundfile)
    if sound:
        sound.play()

def randomDate(startYear, endYear):
    d1 = datetime.strptime(f'1/1/{startYear}', '%m/%d/%Y')
    d2 = datetime.strptime(f'12/31/{endYear}', '%m/%d/%Y')
    delta = d2 - d1
    random_second = randrange(delta.days * 86400)
    x = d1 + timedelta(seconds=random_second)
    return x.strftime('%m/%d/%Y')

def getDay(dateString):
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

        self.startYear = 1975
        self.endYear = 2025
        self.count = 5
        self.points = 0
        self.x = 0
        self.dates = [randomDate(self.startYear, self.endYear) for _ in range(self.count)]

        self.root.ids.question_label.text = self.get_label_text()

        menu_items = [
            {"text": day, "viewclass": "OneLineListItem", "on_release": lambda x=day: self.set_day(x)}
            for day in options
        ]
        self.menu = MDDropdownMenu(
            caller=self.root.ids.dropdown_button,
            items=menu_items,
            width_mult=4,
        )
        self.selected_day = None
        return self.root

    def get_label_text(self):
        if self.x < self.count:
            return f"{self.x+1} of {self.count}\n\nWhat day did this date fall on?\n\n{self.dates[self.x]}"
        else:
            return f"Game Over!\nYou got {self.points} of {self.count} correct!"

    def set_day(self, day):
        self.selected_day = day
        self.root.ids.dropdown_button.text = day
        self.menu.dismiss()

    def update(self):
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
            if self.points == self.count:
                playit("perfect.mp3")
            else:
                playit("fail.mp3")

        self.root.ids.question_label.text = self.get_label_text()

    def restart(self):
        self.points = 0
        self.x = 0
        self.dates = [randomDate(self.startYear, self.endYear) for _ in range(self.count)]
        self.root.ids.question_label.text = self.get_label_text()
        self.root.ids.dropdown_button.text = "Day"
        self.selected_day = None

if __name__ == "__main__":
    DayOfWeekGame().run()
