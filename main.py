from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from datetime import datetime, timedelta
from random import randrange

KV = """
<MainScreen>:
    # FloatLayout allows overlaying GIFs on top
    MDBoxLayout:
        id: main_layout
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
            id: card
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

                MDRaisedButton:
                    id: dropdown_button
                    text: "Day"
                    size_hint: None, None
                    size: dp(140), dp(48)
                    md_bg_color: app.theme_cls.primary_color
                    text_color: 1, 1, 1, 1
                    on_release: app.open_menu()
                    shorten: True
                    shorten_from: "center"
                    text_size: self.size
                    font_size: self.height * 0.4
                    halign: "center"

                Widget:

                MDRaisedButton:
                    text: "Submit"
                    size_hint: None, None
                    size: dp(140), dp(48)
                    md_bg_color: app.theme_cls.primary_color
                    text_color: 1, 1, 1, 1
                    shorten: True
                    shorten_from: "center"
                    text_size: self.size
                    font_size: self.height * 0.4
                    halign: "center"
                    on_release: app.update()

        MDFlatButton:
            text: "Restart"
            pos_hint: {"center_x": 0.5}
            on_release: app.restart()
"""

options = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def randomDate(startYear, endYear):
    d1 = datetime.strptime(f'1/1/{startYear}', '%m/%d/%Y')
    d2 = datetime.strptime(f'12/31/{endYear}', '%m/%d/%Y')
    delta = d2 - d1
    random_second = randrange(delta.days * 86400)
    return (d1 + timedelta(seconds=random_second)).strftime('%m/%d/%Y')

def getDay(dateString):
    dateObject = datetime.strptime(dateString, "%m/%d/%Y").date()
    return options[dateObject.weekday()]

class MainScreen(FloatLayout):
    pass

class DayOfWeekGame(MDApp):
    def build(self):
        self.title = "Day Guess Game"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Dark"

        Builder.load_string(KV)
        self.root = MainScreen()

        # Preload sounds
        self.sounds = {name: SoundLoader.load(f"{name}.wav") for name in ["good","bad","perfect","fail"]}

        # Preload GIFs into memory (opacity=0)
        self.end_gifs = {
            "perfect": Image(source="perfect.gif", allow_stretch=True, keep_ratio=False,
                             anim_delay=0.05, size_hint=(1,1), opacity=0),
            "fail": Image(source="fail.gif", allow_stretch=True, keep_ratio=False,
                          anim_delay=0.05, size_hint=(1,1), opacity=0)
        }
        for gif in self.end_gifs.values():
            self.root.add_widget(gif)

        # Game setup
        self.startYear = 1975
        self.endYear = 2025
        self.count = 5
        self.points = 0
        self.x = 0
        self.dates = [randomDate(self.startYear, self.endYear) for _ in range(self.count)]
        self.selected_day = None
        self.root.ids.question_label.text = self.get_label_text()

        return self.root

    def playit(self, name):
        snd = self.sounds.get(name)
        if snd:
            snd.stop()
            snd.play()

    def flash_card(self, correct=True):
        card = self.root.ids.card
        original_color = self.theme_cls.bg_light
        flash_color = (0,1,0,0.4) if correct else (1,0,0,0.4)
        anim = Animation(md_bg_color=flash_color, duration=0.15) + Animation(md_bg_color=original_color, duration=0.4)
        anim.start(card)

    def show_end_gif(self, name):
        gif = self.end_gifs.get(name)
        if not gif:
            return
        gif.opacity = 1
        anim = Animation(opacity=0, duration=0.8)
        Clock.schedule_once(lambda dt: anim.start(gif), 3)

    def get_label_text(self):
        if self.x < self.count:
            return f"{self.x+1} of {self.count}\n\n{self.dates[self.x]}\n"
        else:
            return f"Game Over!\nYou got {self.points} of {self.count} correct!"

    def open_menu(self):
        menu_items = [{"text": day, "viewclass":"OneLineListItem", "on_release": lambda x=day: self.set_day(x)} for day in options]
        self.menu = MDDropdownMenu(caller=self.root.ids.dropdown_button, items=menu_items, width_mult=3, position="auto", ver_growth="up")
        Clock.schedule_once(lambda dt: self.menu.open(), 0.05)

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
            self.playit("good")
            self.flash_card(True)
        else:
            self.playit("bad")
            self.flash_card(False)

        self.x += 1

        if self.x == self.count:
            if self.points == self.count:
                self.show_end_gif("perfect")
                self.playit("perfect")
            else:
                self.show_end_gif("fail")
                self.playit("fail")

        self.root.ids.question_label.text = self.get_label_text()

    def restart(self):
        self.points = 0
        self.x = 0
        self.dates = [randomDate(self.startYear,self.endYear) for _ in range(self.count)]
        self.root.ids.question_label.text = self.get_label_text()
        self.root.ids.dropdown_button.text = "Day"
        self.selected_day = None

if __name__ == "__main__":
    DayOfWeekGame().run()
