from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.popup import Popup
from datetime import datetime, timezone
from caldav import DAVClient

# Set default window properties
Window.clearcolor = (0, 0, 0, 1)
Window.size = (600, 400)

# Register Orbitron font
LabelBase.register(name="Orbitron", fn_regular="Orbitron/static/Orbitron-Bold.ttf")

# KV string for the UI layout
KV = '''
MDScreen:
    md_bg_color: app.theme_cls.bg_normal

    MDBoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 20

        MDLabel:
            text: "Create New Event"
            halign: "center"
            font_style: "H5"
            font_name: "Orbitron"
            text_color: app.NEON_BLUE

        MDTextField:
            id: event_name
            hint_text: "Event Name"
            size_hint_x: None
            width: 300
            pos_hint: {"center_x": .5}
            font_name: "Orbitron"
            text_color: app.NEON_BLUE
            line_color: app.NEON_BLUE
            line_color_focus: app.NEON_TEAL

        MDTextField:
            id: event_desc
            hint_text: "Event Description"
            size_hint_x: None
            width: 300
            height: 100
            multiline: True
            pos_hint: {"center_x": .5}
            font_name: "Orbitron"
            line_color: app.NEON_BLUE
            text_color: app.NEON_BLUE
            line_color_focus: app.NEON_TEAL

        MDRaisedButton:
            text: "Select Start Date & Time"
            on_press: app.show_start_picker()
            pos_hint: {"center_x": .5}
            font_name: "Orbitron"
            line_color: app.NEON_BLUE
            text_color: app.NEON_BLUE

        MDRaisedButton:
            text: "Select End Date & Time"
            on_press: app.show_end_picker()
            pos_hint: {"center_x": .5}
            font_name: "Orbitron"
            line_color: app.NEON_BLUE
            text_color: app.NEON_BLUE

        MDRaisedButton:
            text: "Create Event"
            on_press: app.create_event()
            pos_hint: {"center_x": .5}
            font_name: "Orbitron"
            line_color: app.NEON_BLUE
            text_color: app.NEON_BLUE
'''

class EventCreatorApp(MDApp):

    NEON_TEAL = (0.0, 1.0, 1.0, 1.0)
    NEON_PINK = (1.0, 0.0, 0.5, 1.0)
    NEON_BLUE = (0.0, 0.5, 1.0, 1.0)

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.primary_hue = "A400"
        self.theme_cls.theme_style = "Dark"

        self.client = DAVClient(
            "https://caldav.icloud.com/",
            username="apple-user-email",
            password="apple-dev-key",
        )
        self.principal = self.client.principal()
        self.calendars = self.principal.calendars()

        return Builder.load_string(KV)
    
    def open_calendar_menu(self, instance):
        self.calendar_menu.open()

    def set_calendar(self, calendar_name):
        self.calendar_button.text = f"Calendar: {calendar_name}"
        self.calendar_menu.dismiss()

    def show_start_picker(self):
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.set_start_date)
        date_picker.open()

    def show_end_picker(self):
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.set_end_date)
        date_picker.open()

    def set_start_date(self, instance, date_obj, date_range):
        time_picker = MDTimePicker()
        time_picker.bind(on_save=self.set_start_time)
        time_picker.open()
        self.start_date = date_obj

    def set_end_date(self, instance, date_obj, date_range):
        time_picker = MDTimePicker()
        time_picker.bind(on_save=self.set_end_time)
        time_picker.open()
        self.end_date = date_obj

    def set_start_time(self, instance, time_obj):
        self.start_date_time = datetime.combine(self.start_date, time_obj)
        print(f"Start Date & Time: {self.start_date_time}")

    def set_end_time(self, instance, time_obj):
        self.end_date_time = datetime.combine(self.end_date, time_obj)
        print(f"End Date & Time: {self.end_date_time}")

    def create_event(self):
        event_name = self.root.ids.event_name.text
        event_desc = self.root.ids.event_desc.text

        if not event_name or not event_desc or not hasattr(self, "start_date_time") or not hasattr(self, "end_date_time"):
            self.show_popup("Error", "All fields are required!")
            return

        # Use the first calendar as default
        target_calendar = self.calendars[0] if self.calendars else None
        if not target_calendar:
            self.show_popup("Error", "No calendars found!")
            return

        event = (
                "BEGIN:VCALENDAR\n"
                "VERSION:2.0\n"
                "PRODID:-//github.com/EthanMasters23//iCalendar API 1.0//EN\n"
                "CALSCALE:GREGORIAN\n"
                "METHOD:PUBLISH\n"
                "BEGIN:VEVENT\n"
                f"UID:{datetime.now(tz=timezone.utc).timestamp()}\n"
                f"SEQUENCE:{str(0)}\n"
                "STATUS:CONFIRMED\n" # TENTATIVE/CONFIRMED/CANCELLED
                "TRANSP:TRANSPARENT\n" # OPAQUE: Blocks Availability / TRANSPARENT: Does not block availability
                f"DTSTAMP:{datetime.now(tz=timezone.utc).strftime('%Y%m%dT%H%M%SZ')}\n"
                f"DTSTART:{self.start_date_time.strftime('%Y%m%dT%H%M%SZ')}\n"
                f"DTEND:{self.end_date_time.strftime('%Y%m%dT%H%M%SZ')}\n"
                f"SUMMARY:{event_name}\n"
                f"DESCRIPTION:{event_desc}\n"
                "END:VEVENT\n"
                "END:VCALENDAR\n"
            )

        target_calendar.add_event(event)
        self.show_popup("Success", "Event added successfully!")

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=MDLabel(text=message, halign="center", font_name="Orbitron"),
            size_hint=(None, None),
            size=(300, 200),
        )
        popup.open()

if __name__ == "__main__":
    EventCreatorApp().run()
