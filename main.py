import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.lang import Builder
from plyer import battery
import google.generativeai as genai

from kivy.utils import platform

# Android Specific Native APIs
if platform == 'android':
    from jnius import autoclass, cast
    from android import activity
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    RecognizerIntent = autoclass('android.speech.RecognizerIntent')
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    Locale = autoclass('java.util.Locale')
    String = autoclass('java.lang.String')

# ==========================================
# SCI-FI UI DESIGN (Added Settings Screen)
# ==========================================
KV = '''
ScreenManager:
    SplashScreen:
    JarvisDashboard:
    SettingsScreen:

<SplashScreen>:
    name: 'splash'
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: "ARVIND JARVIS AI\\nSYSTEM ACTIVATION..."
        color: 0, 1, 1, 1
        font_size: '24sp'
        bold: True
        halign: 'center'

<JarvisDashboard>:
    name: 'dashboard'
    canvas.before:
        Color:
            rgba: 0.02, 0.02, 0.02, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 15

        BoxLayout:
            size_hint_y: 0.08
            Label:
                text: "JARVIS MAINFRAME"
                color: 0, 0.9, 1, 1
                font_size: '18sp'
                bold: True
                halign: 'left'
            Button:
                text: "⚙ SETTINGS"
                size_hint_x: 0.3
                background_color: 0.2, 0.2, 0.2, 1
                color: 1, 1, 1, 1
                on_release: app.root.current = 'settings'

        ScrollView:
            size_hint_y: 0.62
            canvas.before:
                Color:
                    rgba: 0, 0.1, 0.2, 0.3
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10]
            Label:
                id: chat_history
                text: "JARVIS: Systems ready, Sir Arvind Ji.\\n"
                color: 0, 1, 0.9, 1
                text_size: self.width - 20, None
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'left'
                valign: 'top'
                padding: [10, 10]

        TextInput:
            id: user_input
            size_hint_y: 0.1
            background_color: 0.05, 0.05, 0.08, 1
            foreground_color: 0, 1, 1, 1
            cursor_color: 0, 1, 1, 1
            hint_text: "Type command..."
            multiline: False

        BoxLayout:
            size_hint_y: 0.15
            spacing: 10
            
            Button:
                text: "SEND"
                background_color: 0, 0.3, 0.5, 1
                color: 1, 1, 1, 1
                bold: True
                on_release: app.send_message(user_input.text)
                
            Button:
                text: "MIC (VOICE)"
                background_color: 0, 0.6, 0.3, 1
                color: 1, 1, 1, 1
                bold: True
                on_release: app.start_voice_recognition()

<SettingsScreen>:
    name: 'settings'
    canvas.before:
        Color:
            rgba: 0.02, 0.02, 0.02, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        
        Label:
            text: "API CONFIGURATION"
            color: 0, 1, 1, 1
            font_size: '20sp'
            bold: True
            size_hint_y: 0.2
            
        TextInput:
            id: api_input
            hint_text: "Paste Gemini API Key here..."
            background_color: 0.1, 0.1, 0.1, 1
            foreground_color: 0, 1, 1, 1
            multiline: False
            size_hint_y: 0.15
            
        Button:
            text: "SAVE & ACTIVATE AI"
            background_color: 0, 0.6, 0.3, 1
            color: 1, 1, 1, 1
            bold: True
            size_hint_y: 0.15
            on_release: app.save_api_key(api_input.text)
            
        Button:
            text: "BACK TO DASHBOARD"
            background_color: 0.5, 0.1, 0.1, 1
            color: 1, 1, 1, 1
            bold: True
            size_hint_y: 0.15
            on_release: app.root.current = 'dashboard'
            
        Widget:
            size_hint_y: 0.35
'''

class SplashScreen(Screen):
    pass

class JarvisDashboard(Screen):
    pass
    
class SettingsScreen(Screen):
    pass

class JarvisApp(App):
    def build(self):
        self.tts = None
        self.chat_session = None
        # Path to securely save API key in phone storage
        self.api_file = os.path.join(self.user_data_dir, 'gemini_key.txt')
        
        if platform == 'android':
            self.init_android_tts()
            activity.bind(on_activity_result=self.on_activity_result)
            
        return Builder.load_string(KV)

    def on_start(self):
        Clock.schedule_once(lambda dt: setattr(self.root, 'current', 'dashboard'), 2)
        self.load_api_key()
        self.speak("Mainframe online. Good day, Sir Arvind Ji.")

    # --- API KEY MANAGEMENT ---
    def load_api_key(self):
        if os.path.exists(self.api_file):
            with open(self.api_file, 'r') as f:
                key = f.read().strip()
                if key:
                    self.init_gemini(key)
                    # Show key securely in settings
                    settings = self.root.get_screen('settings')
                    settings.ids.api_input.text = key

    def save_api_key(self, key):
        key = key.strip()
        if key:
            with open(self.api_file, 'w') as f:
                f.write(key)
            self.init_gemini(key)
            self.root.current = 'dashboard'
            self.log_chat("SYSTEM", "API Key Saved. Neural link established.")
            self.speak("API key configured successfully.")

    def init_gemini(self, key):
        try:
            genai.configure(api_key=key)
            SYSTEM_PROMPT = "You are JARVIS, an advanced AI phone assistant created by Arvind. Address the user as 'Sir Arvind Ji'. Keep responses short for voice dictation. Speak fluent Hindi and English."
            model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
            self.chat_session = model.start_chat(history=[])
        except Exception as e:
            self.log_chat("SYSTEM", "Invalid API Key format.")

    # --- ANDROID NATIVE APIs ---
    def init_android_tts(self):
        try:
            self.tts = TextToSpeech(PythonActivity.mActivity, None)
            self.tts.setLanguage(Locale.US)
        except Exception:
            pass

    def speak(self, text):
        if platform == 'android' and self.tts:
            self.tts.speak(String(text), TextToSpeech.QUEUE_FLUSH, None)

    def start_voice_recognition(self):
        if platform == 'android':
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, String("Speak Command, Sir..."))
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivityForResult(intent, 1000)

    def on_activity_result(self, request_code, result_code, intent):
        if request_code == 1000 and result_code == -1: 
            results = intent.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if results and results.size() > 0:
                voice_text = results.get(0)
                self.send_message(voice_text)

    # --- CHAT & INTENT PROCESSING ---
    def log_chat(self, sender, text):
        dashboard = self.root.get_screen('dashboard')
        dashboard.ids.chat_history.text += f"\\n{sender}: {text}\\n"
        
    def send_message(self, text):
        if not text.strip(): return
        
        dashboard = self.root.get_screen('dashboard')
        dashboard.ids.user_input.text = ""
        self.log_chat("Sir Arvind Ji", text)
        
        cmd = text.lower()

        # Phone Commands
        if "open youtube" in cmd:
            self.execute_intent(Intent.ACTION_VIEW, "https://www.youtube.com")
            self.reply("Opening YouTube, Sir.")
            return
        elif "open google" in cmd:
            self.execute_intent(Intent.ACTION_VIEW, "https://www.google.com")
            self.reply("Opening Google, Sir.")
            return
        elif "call papa" in cmd or "call dad" in cmd:
            self.execute_intent(Intent.ACTION_DIAL, "tel:") 
            self.reply("Opening dialer, Sir.")
            return
        elif "battery" in cmd:
            try:
                level = battery.battery_level
                self.reply(f"Battery is at {level} percent, Sir.")
            except:
                self.reply("Battery sensors unavailable.")
            return

        # AI Conversation
        if self.chat_session is None:
            self.reply("Please configure your API Key in Settings first.")
            return
            
        try:
            response = self.chat_session.send_message(text)
            self.reply(response.text)
        except Exception:
            self.reply("Neural link offline. Please check internet or API Key.")

    def reply(self, text):
        self.log_chat("JARVIS", text)
        self.speak(text)

    def execute_intent(self, action, uri_string):
        if platform == 'android':
            intent = Intent(action)
            intent.setData(Uri.parse(String(uri_string)))
            PythonActivity.mActivity.startActivity(intent)

if __name__ == '__main__':
    JarvisApp().run()

