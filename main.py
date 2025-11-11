from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.audio import SoundLoader
from datetime import datetime, timedelta
from random import randrange

# Game settings
startYear = 1974
endYear = 2024
count = 5

# Sound files
good = "good.mp3"
bad = "bad.mp3"
perfect = "perfect.mp3"
meh = "fail.mp3"

options = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

def playit(soundfile):
    sound = SoundLoader.load(soundfile)
    if sound:
        sound.play()

def randomDate(start, end):
    d1 = datetime.strptime(f'1/1/{startYear} 12:00 AM', '%m/%d/%Y %I:%M %p')
    d2 = datetime.strptime(f'12/31/{endYear} 11:59 PM', '%m/%d/%Y %I:%M %p')
    delta = d2 - d1
    intDelta = (delta.days * 24 * 60 * 60) + delta.seconds
    randomSecond = randrange(intDelta)
    x = d1 + timedelta(seconds=randomSecond)
    date_str = x.strftime('%-m/%-d/%Y')
    return date_str

def getDay(dateString):
    dateObject = datetime.strptime(dateString, "%m/%d/%Y").date()
    dayNumber = dateObject.weekday()
    return options[dayNumber]

class DayOfWeekGame(App):
    def build(self):
        self.points = 0
        self.x = 0
        self.dates = [randomDate(startYear,endYear) for _ in range(count)]

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.label = Label(text=self.get_label_text())
        self.layout.add_widget(self.label)
        
        self.spinner = Spinner(text='Sunday', values=options)
        self.layout.add_widget(self.spinner)
        
        self.submit_btn = Button(text="Submit", on_press=self.update)
        self.layout.add_widget(self.submit_btn)
        
        self.restart_btn = Button(text="Restart", on_press=self.restart)
        self.layout.add_widget(self.restart_btn)
        
        return self.layout

    def get_label_text(self):
        if self.x < count:
            return f"{self.x+1} of {count}\nPick a Day-of-the-Week\nfor {self.dates[self.x]}"
        else:
            return f"Game Over!\n{self.points} out of {count} correct!"

    def update(self, instance):
        if self.x >= count:
            return

        reality = getDay(self.dates[self.x])
        picked = self.spinner.text

        if reality == picked:
            self.points += 1
            playit(good)
        else:
            playit(bad)

        self.x += 1
        if self.x == count:
            if self.points == count:
                playit(perfect)
            else:
                playit(meh)

        self.label.text = self.get_label_text()

    def restart(self, instance):
        self.points = 0
        self.x = 0
        self.dates = [randomDate(startYear,endYear) for _ in range(count)]
        self.label.text = self.get_label_text()
        self.spinner.text = 'Sunday'

if __name__ == "__main__":
    DayOfWeekGame().run()
