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
            username="ethansmasters@outlook.com",
            password="qges-nfnn-qvsa-xdgx",
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
                f"SEQUENCE:{str(0)}\n" # Increment every time the event is updated
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



























# # Apple iCalendar Streamline Event Data

# from kivy.app import App
# from kivy.uix.button import Button
# from kivy.uix.textinput import TextInput
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.label import Label
# from kivy.uix.popup import Popup
# from kivy.uix.spinner import Spinner
# from kivy.core.window import Window
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.scrollview import ScrollView
# from kivy.core.text import LabelBase
# from kivy.graphics import RoundedRectangle, Color
# from caldav import DAVClient
# from datetime import datetime, timedelta


# LabelBase.register(name="Orbitron", fn_regular="Orbitron/static/Orbitron-Bold.ttf")

# Window.clearcolor = (0, 0, 0, 1) 
# Window.size = (600, 400) 

# class EventCreatorApp(App):
#     def build(self):
#         self.client = DAVClient("https://caldav.icloud.com/", username="ethansmasters@outlook.com", password="qges-nfnn-qvsa-xdgx")
#         self.principal = self.client.principal()
#         self.calendars = self.principal.calendars()

#         self.layout = BoxLayout(orientation='vertical', padding=40, spacing=20)  # Increased padding and spacing

#         self.layout.add_widget(Label(text="Create New Event", font_size=36, color=(0.0, 1.0, 1.0, 1.0), font_name="Orbitron"))

#         self.name_input = TextInput(hint_text="Event Name", multiline=False, size_hint_y=None, height=50, 
#                                     background_normal='', background_active='', foreground_color=(0.0, 1.0, 1.0, 1.0), font_name="Orbitron")
#         self.name_input.canvas.before.add(Color(0.0, 1.0, 0.0, 1.0))  # Neon border color
#         self.name_input.canvas.before.add(RoundedRectangle(size=self.name_input.size, pos=self.name_input.pos, radius=[10]))

#         self.layout.add_widget(self.name_input)

#         self.desc_input = TextInput(hint_text="Event Description", multiline=True, size_hint_y=None, height=100, 
#                                     background_normal='', background_active='', foreground_color=(0.0, 1.0, 1.0, 1.0), font_name="Orbitron")
#         self.desc_input.canvas.before.add(Color(0.0, 1.0, 0.0, 1.0))  # Neon border color
#         self.desc_input.canvas.before.add(RoundedRectangle(size=self.desc_input.size, pos=self.desc_input.pos, radius=[10]))
        
#         self.layout.add_widget(self.desc_input)

#         self.start_date_input = TextInput(hint_text="Start Date (YYYY-MM-DD)", multiline=False, size_hint_y=None, height=50, 
#                                           background_normal='', background_active='', foreground_color=(0.0, 1.0, 1.0, 1.0), font_name="Orbitron")
#         self.start_date_input.canvas.before.add(Color(0.0, 1.0, 0.0, 1.0))  # Neon border color
#         self.start_date_input.canvas.before.add(RoundedRectangle(size=self.start_date_input.size, pos=self.start_date_input.pos, radius=[10]))
        
#         self.layout.add_widget(self.start_date_input)

#         self.end_date_input = TextInput(hint_text="End Date (YYYY-MM-DD)", multiline=False, size_hint_y=None, height=50, 
#                                         background_normal='', background_active='', foreground_color=(0.0, 1.0, 1.0, 1.0), font_name="Orbitron")
#         self.end_date_input.canvas.before.add(Color(0.0, 1.0, 0.0, 1.0))  # Neon border color
#         self.end_date_input.canvas.before.add(RoundedRectangle(size=self.end_date_input.size, pos=self.end_date_input.pos, radius=[10]))
        
#         self.layout.add_widget(self.end_date_input)

#         calendar_names = [calendar.name for calendar in self.calendars]
#         self.calendar_spinner = Spinner(text="Select Calendar", values=calendar_names, size_hint=(None, None), size=(295, 44), font_name="Orbitron")
#         self.calendar_spinner.background_normal = ''
#         self.calendar_spinner.background_color = (0.0, 1.0, 0.0, 1.0)  # Neon green background color
        
#         self.layout.add_widget(self.calendar_spinner)

#         submit_button = Button(text="Create Event", size_hint=(None, None), size=(250, 50), 
#                                background_normal='', background_color=(0.0, 1.0, 0.0, 1.0), font_name="Orbitron")
#         submit_button.bind(on_press=self.create_event)

#         submit_button.canvas.before.add(Color(0.0, 1.0, 0.0, 0.5))  # Neon glow
#         submit_button.canvas.before.add(RoundedRectangle(size=submit_button.size, pos=submit_button.pos, radius=[10]))

#         self.layout.add_widget(submit_button)

#         return self.layout

#     def create_event(self, instance):
#         event_name = self.name_input.text
#         event_desc = self.desc_input.text
#         start_date = self.start_date_input.text
#         end_date = self.end_date_input.text
#         calendar_name = self.calendar_spinner.text
        
#         if not event_name or not event_desc or not start_date or not end_date:
#             self.show_popup("Error", "All fields are required!")
#             return
        
#         target_calendar = self.get_calendar_by_name(calendar_name)
#         if not target_calendar:
#             self.show_popup("Error", "Calendar not found!")
#             return
        
#         event = """BEGIN:VCALENDAR
#         VERSION:2.0
#         PRODID:-//github.com/EthanMasters23//iCalendar API 1.0//EN
#         CALSCALE:GREGORIAN
#         METHOD:PUBLISH
#         BEGIN:VEVENT
#         UID:{uid}
#         SEQUENCE:0
#         STATUS:CONFIRMED
#         TRANSP:TRANSPARENT
#         DTSTAMP:{now}
#         DTSTART:{start_time}
#         DTEND:{end_time}
#         SUMMARY:{event_name}
#         DESCRIPTION:{event_desc}
#         URL:http://americanhistorycalendar.com/peoplecalendar/1,328-abraham-lincoln
#         END:VEVENT
#         END:VCALENDAR
#         """.format(
#             uid=str(datetime.utcnow().timestamp()),
#             now=datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
#             start_time=self.convert_date_to_utc(start_date),
#             end_time=self.convert_date_to_utc(end_date),
#             event_name=event_name,
#             event_desc=event_desc
#         )

#         target_calendar.add_event(event)
#         self.show_popup("Success", "Event added successfully!")

#     def convert_date_to_utc(self, date_str):
#         return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%dT%H%M%SZ")
    
#     def get_calendar_by_name(self, name):
#         for calendar in self.calendars:
#             if calendar.name == name:
#                 return calendar
#         return None

#     def show_popup(self, title, message):
#         content = BoxLayout(orientation='vertical')
#         content.add_widget(Label(text=message))
#         close_button = Button(text="Close", size_hint=(None, None), size=(100, 50))
#         content.add_widget(close_button)
#         popup = Popup(title=title, content=content, size_hint=(None, None), size=(300, 200))
#         close_button.bind(on_press=popup.dismiss)
#         popup.open()

# if __name__ == '__main__':
#     EventCreatorApp().run()







### old class no gui ###


# class iCalendarAPI:
#     def __init__(self):
#         self.connect_client()
#         self.calendars = None

#     def connect_client(self):
#         client = DAVClient("https://caldav.icloud.com/", username="ethansmasters@outlook.com", password="qges-nfnn-qvsa-xdgx")
#         principal = client.principal()

#         self.calendars = principal.calendars()

#     def print_calendars(self):
#         for i, calendar in enumerate(self.calendars):
#             print(f"Calendars {i}: {calendar.name}")

#     def get_target_calendar(self, input_calendar):
#         for calendar in self.calendars:
#             if calendar.name == input_calendar:
#                 return calendar
#         return None
    
#     def add_event(self):
#         event = '''BEGIN:VCALENDAR
#         VERSION:2.0
#         BEGIN:VEVENT
#         UID:12345@example.com
#         DTSTAMP:{now}
#         DTSTART:{start_time}
#         DTEND:{end_time}
#         SUMMARY:Sample Event
#         DESCRIPTION:This is a test event created via Python.
#         END:VEVENT
#         END:VCALENDAR
#         '''.format(
#             now=datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
#             start_time=(datetime.utcnow() + timedelta(days=1)).strftime("%Y%m%dT%H%M%SZ"),
#             end_time=(datetime.utcnow() + timedelta(days=1, hours=1)).strftime("%Y%m%dT%H%M%SZ")
#         )

#         # Upload the event
#         target_calendar.add_event(event)
#         print("Event added!")