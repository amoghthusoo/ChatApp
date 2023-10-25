Windows_Mode = True

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
import socket as so
import threading as th

if Windows_Mode == True:
    Window.size = (380, 768)
    Window.top = 0
    Window.left = 0

UI_SERVER = '''
MDScreenManager:

    MDScreen:

        name : "home"
        
        MDBoxLayout:

            orientation : "vertical"
            spacing : "15dp"

            MDTopAppBar:

                id : home_screen_top_app_bar
                title : "ChatApp"
                left_action_items : [["menu", lambda x : app.temp()]]
                md_bg_color : app.theme_color
                elevation : 0
            
            MDBoxLayout:

                orientation : "vertical"
                spacing : "20dp"
                padding : "20dp"

                MDLabel:
                    
                    text : "Enter IP Address :"
                    font_size : "18sp"
                    size_hint_y : None
                    height : self.texture_size[1]

                    bold : True

                MDTextField:

                    id : ip_address
                    hint_text: "IP Address"
                    mode: "rectangle"
                    line_color_focus : app.theme_color
                    hint_text_color_focus : app.theme_color
                    text_color_focus: "black"

                MDLabel:
                    
                    text : "Start Server :"
                    font_size : "18sp"
                    size_hint_y : None
                    height : self.texture_size[1]

                    bold : True
                
                MDRaisedButton:

                    id : start
                    text : "Start"
                    font_size : "18sp"
                    pos_hint : {'center_x' : 0.5, 'center_y' : 0.5}
                    on_release : app.initialise_start_server()
                    md_bg_color : app.theme_color
                    

                    elevation : 0
                    shadow_softness : 80
                    shadow_softness_size : 2
                    
                
                MDWidget:    

            MDWidget:
    MDScreen:

        name : "chatting"

        MDBoxLayout:

            orientation : "vertical"
            spacing : "15dp"

            MDTopAppBar:

                id : home_screen_top_app_bar
                title : "Start Chatting"
                left_action_items : [["menu", lambda x : app.temp()]]
                md_bg_color : app.theme_color
                elevation : 0
            
            ScrollView:

                id : scroll

                do_scroll_x: False
                do_scroll_y: True

                MDBoxLayout:

                    id : chatting_page
                    spacing : "10dp"
                    padding : "15dp"

                    size: (self.parent.width, self.parent.height-1)
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height

                    # MDLabel:
                    #     size_hint: (1, None)
                    #     height: self.texture_size[1]
                    #     text: "Hello"

            MDFloatLayout:

                MDBoxLayout:

                    orientation : "horizontal"
                    spacing : "10dp"
                    padding : "10dp"


                    MDTextField:
                        id : message_box
                        mode : "round"
                        hint_text: "Message"
                        line_color_focus : app.theme_color
                        hint_text_color_focus : app.theme_color
                        text_color_focus: "black"  
                        size_hint : (0.1, 0.13)
                        pos_hint : {"center_x" : 0.5, "center_y" : 0.12}
                    
                    MDFloatingActionButton:
                        icon : "send"
                        md_bg_color : app.theme_color
                        pos_hint : {"center_x" : 0.5, "center_y" : 0.12}
                        on_release : app.send_message()

                        elevation : 0
                        shadow_softness : 80
                        shadow_softness_size : 2
'''

class ChatApp_Server(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.theme_color = [18/255, 140/255, 126/255, 255/255]
        self.server_socket = so.socket()
        self.port = 9999

        self.configuration_dict = {"server_started" : False, "connected_with_client" : False, "redirect_to_chatting_page" : False,
                                   "sent_message" : "", "received_message" : ""}

        self.start_server_snackbar_event = Clock.schedule_interval(self.server_started_snackbar, 1/10)
        self.connected_with_client_event = Clock.schedule_interval(self.connected_with_client_snackbar, 1/10)
        self.redirect_to_chatting_page_event = Clock.schedule_interval(self.redirect_to_chatting_page, 1/10)
        self.display_message_event = Clock.schedule_interval(self.display_message, 1/10)
        

    def start_server(self):
        
        self.configuration_dict["server_started"] = True
        self.ip_address = self.root.ids.ip_address.text
        self.server_socket.bind((self.ip_address, self.port))
        self.server_socket.listen(1)
        self.client_socket, self.client_address = self.server_socket.accept()
        self.configuration_dict["connected_with_client"] = True
        self.configuration_dict["redirect_to_chatting_page"] = True

        self.receive_message()
        
        
    def initialise_start_server(self):
        
        start_server_thread = th.Thread(target = self.start_server)
        start_server_thread.start()
        self.root.ids.start.disabled = True

    def server_started_snackbar(self, dt):
        
        if self.configuration_dict["server_started"]:
            Snackbar(
                text = "Server Started Successfully !",
                snackbar_x = "9dp",
                snackbar_y = "9dp",
                size_hint_x = 0.95,
                duration = 1.5
                ).open()
            self.start_server_snackbar_event.cancel()

    def connected_with_client_snackbar(self, dt):

        if self.configuration_dict["connected_with_client"]:
            Snackbar(
                text = "Connected with {} .".format(self.client_address),
                snackbar_x = "9dp",
                snackbar_y = "9dp",
                size_hint_x = 0.95,
                duration = 1.5
                ).open()
            self.connected_with_client_event.cancel()

    def redirect_to_chatting_page(self, dt):
        
        if self.configuration_dict["redirect_to_chatting_page"]:
            self.root.transition.direction = "left"
            self.root.current = "chatting"
            self.redirect_to_chatting_page_event.cancel()

    def send_message(self):

        if len(self.root.ids.message_box.text) > 0:
            self.client_socket.send(self.root.ids.message_box.text.encode())

            self.configuration_dict["sent_message"] = self.root.ids.message_box.text
            self.diplay_self_message()

            self.root.ids.message_box.text = ""
    
    def diplay_self_message(self):

        message = MDLabel(text = self.configuration_dict["sent_message"])
        message.adaptive_height = True
        message.halign = "right"
        self.root.ids.chatting_page.add_widget(message)

        if self.root.ids.scroll.vbar[1] < 1:
            self.root.ids.scroll.scroll_y = 0
        
        self.configuration_dict["sent_message"] = ""
    
    def receive_message(self):    

        while True:
            message = self.client_socket.recv(1024).decode()
            self.configuration_dict["received_message"] = message
    
    def display_message(self, dt):

        if len(self.configuration_dict["received_message"]) > 0:

            message = MDLabel(text = self.configuration_dict["received_message"])    # size_hint = (1, None)
            # message.height = message.texture_size[1]
            message.adaptive_height = True
            # message.halign = "right"
            self.root.ids.chatting_page.add_widget(message)

            if self.root.ids.scroll.vbar[1] < 1:
                self.root.ids.scroll.scroll_y = 0
            
            self.configuration_dict["received_message"] = ""

    def temp(self):
        print(self.configuration_dict)

    def build(self):
        self.app = Builder.load_string(UI_SERVER)
        return self.app
    
root = ChatApp_Server()

if(__name__ == "__main__"):
    root.run()