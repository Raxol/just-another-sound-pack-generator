import sys

import customtkinter
import yaml

from ttsproviders.amazonpolly import AmazonPollyTTS
from ttsproviders.elevenlabs import ElevenLabsTTS
from ttsproviders.googletts import GoogleTTS
from ttsproviders.ibmwatson import IBMWatsonTTS
from ttsproviders.microsoftazure import MicrosoftAzureTTS

CONFIG = None

def load_config():
	global CONFIG
	try:
		with open('config.yaml', 'r') as file:
			CONFIG = yaml.safe_load(file)
			print("Config file loaded.")
	except yaml.YAMLError as error:
		print(f"Error parsing YAML config file: {error}")
		sys.exit(1)
	except FileNotFoundError:
		print("Config file missing. Copy & edit config_example.yaml")
		sys.exit(1)


class GoogleTTSFrame(customtkinter.CTkFrame):
	def __init__(self, master, **kwargs):
		super().__init__(master, **kwargs)
		
		self._tts_client = GoogleTTS(r"googletts_cred.json")
		
		self._voices = self._tts_client.get_voices()
		lang_values = []
		
		for voice in self._voices:
			if voice.language_codes[0] not in lang_values:
				lang_values.append(voice.language_codes[0])
		
		lang_values.sort()
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)

		# add widgets onto the frame, for example:
		self.label = customtkinter.CTkLabel(self, text="Google Cloud Text-to-Speech", font=customtkinter.CTkFont(size=20, weight="bold"))
		self.label.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
		
		self.language_select = customtkinter.CTkOptionMenu(self, values=lang_values, command=self.language_select_callback)
		self.language_select.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
		self.voice_select = customtkinter.CTkOptionMenu(self, command=self.voice_select_callback)
		self.voice_select.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
		self.language_select_callback(lang_values[0])
		
		self.rate_slider_description_label = customtkinter.CTkLabel(self, text="Speaking rate: 1")
		self.rate_slider_description_label.grid(row=2, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.rate_slider = customtkinter.CTkSlider(self, command=self.rate_slider_callback, from_=0.25, to=4)
		self.rate_slider.grid(row=3, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		self.rate_slider.set(1)
		
		self.pitch_slider_description_label = customtkinter.CTkLabel(self, text="Pitch: 0")
		self.pitch_slider_description_label.grid(row=4, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.pitch_slider = customtkinter.CTkSlider(self, command=self.pitch_slider_callback, from_=-20, to=20)
		self.pitch_slider.grid(row=5, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		self.pitch_slider.set(0)
		
		self.preview_text_entry_description_label = customtkinter.CTkLabel(self, text="Test Phrase", justify=customtkinter.LEFT)
		self.preview_text_entry_description_label.grid(row=6, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.preview_text_entry = customtkinter.CTkEntry(self, textvariable=customtkinter.StringVar(value='trainer signal recovered'), placeholder_text="trainer signal recovered")
		self.preview_text_entry.grid(row=7, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		
		self.preview_button = customtkinter.CTkButton(self, height=40, width=120, text="Play", font=customtkinter.CTkFont(size=18, weight="bold"), command=self.preview_button_callback)
		self.preview_button.grid(row=8, column=0, pady=(0,20), columnspan=2)
	
	def language_select_callback(self, value):
		selected_voice_names = []
		for voice in self._voices:
			if voice.language_codes[0].startswith(value):
				selected_voice_names.append(voice.name)
		
		selected_voice_names.sort()
		self._tts_client.language = value
		self.voice_select.configure(values=selected_voice_names)
		self.voice_select.set(selected_voice_names[0])
		self.voice_select_callback(selected_voice_names[0])
	
	def voice_select_callback(self, value):
		self._tts_client.voice_name = value
	
	def rate_slider_callback(self, value):
		self.rate_slider_description_label.configure(text=f"Speaking rate: {value:3.2f}")
		self._tts_client.speaking_rate = value

	def pitch_slider_callback(self, value):
		self.pitch_slider_description_label.configure(text=f"Pitch: {value:3.2f}")
		self._tts_client.pitch = value
	
	def preview_button_callback(self):
		print(f"Playing preview with {self._tts_client.SERVICE_NAME} | Text: {self.preview_text_entry.get()} | Voice: {self.voice_select.get()}")
		self._tts_client.play_text(self.preview_text_entry.get())

class ElevenLabsTTSFrame(customtkinter.CTkFrame):
	def __init__(self, master, **kwargs):
		super().__init__(master, **kwargs)
		
		self._tts_client = ElevenLabsTTS(CONFIG["elevenlabs"]["api_key"], "jsCqWAovK2LkecY7zXl4")
		
		self._voices = self._tts_client.get_voices()
		voice_names = []
		
		for voice in self._voices:
			voice_names.append(f"{voice.name} ({voice.labels['gender']}) ID:{voice.voice_id}")
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
	
		# add widgets onto the frame, for example:
		self.label = customtkinter.CTkLabel(self, text="ElevenLabs Text-to-Speech", font=customtkinter.CTkFont(size=20, weight="bold"))
		self.label.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
		
		self.voice_select = customtkinter.CTkOptionMenu(self, values=voice_names, command=self.voice_select_callback)
		self.voice_select.grid(row=1, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
		self.voice_select.set(voice_names[0])
		
		self.stability_slider_description_label = customtkinter.CTkLabel(self, text="Stability: 1")
		self.stability_slider_description_label.grid(row=2, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.stability_slider = customtkinter.CTkSlider(self, command=self.stability_slider_callback, from_=0.0, to=1.0)
		self.stability_slider.grid(row=3, column=0, padx=20, pady=(0,10), sticky="ew", columnspan=2)
		self.stability_slider.set(1)
		
		self.similarity_slider_description_label = customtkinter.CTkLabel(self, text="Similarity: 0")
		self.similarity_slider_description_label.grid(row=4, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.similarity_slider = customtkinter.CTkSlider(self, command=self.similarity_slider_callback, from_=0.0, to=1.0)
		self.similarity_slider.grid(row=5, column=0, padx=20, pady=(0,10), sticky="ew", columnspan=2)
		self.similarity_slider.set(0)
		
		self.style_slider_description_label = customtkinter.CTkLabel(self, text="Style: 0")
		self.style_slider_description_label.grid(row=6, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.style_slider = customtkinter.CTkSlider(self, command=self.style_slider_callback, from_=0.0, to=1.0)
		self.style_slider.grid(row=7, column=0, padx=20, pady=(0,10), sticky="ew", columnspan=2)
		self.style_slider.set(0)
		
		self.speaker_boost_checkbox = customtkinter.CTkCheckBox(self, text="Speaker Boost", command=self.speaker_boost_checkbox_event)
		self.speaker_boost_checkbox.grid(row=8, column=0, padx=20, pady=20, sticky="w")
		
		self.preview_text_entry_description_label = customtkinter.CTkLabel(self, text="Test Phrase", justify=customtkinter.LEFT)
		self.preview_text_entry_description_label.grid(row=9, column=0, padx=10, pady=(10,0), sticky="w", columnspan=2)

		self.preview_text_entry = customtkinter.CTkEntry(self, textvariable=customtkinter.StringVar(value='trainer signal recovered'), placeholder_text="trainer signal recovered")
		self.preview_text_entry.grid(row=10, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		
		self.preview_button = customtkinter.CTkButton(self, height=40, width=120, text="Play", font=customtkinter.CTkFont(size=18, weight="bold"), command=self.preview_button_callback)
		self.preview_button.grid(row=11, column=0, pady=(0,20), columnspan=2)
	
	def voice_select_callback(self, value):
		extracted_id = value[value.find("ID:")+3:]
		self._tts_client.voice_id = extracted_id
		self.stability_slider.set(self._tts_client.stability)
		self.similarity_slider.set(self._tts_client.similarity)
		self.style_slider.set(self._tts_client.style)
		if self.speaker_boost_checkbox.get() != self._tts_client.speaker_boost:
			self.speaker_boost_checkbox.toggle()
	
	def stability_slider_callback(self, value):
		self.stability_slider_description_label.configure(text=f"Stability: {value:3.2f}")
		self._tts_client.stability = value

	def similarity_slider_callback(self, value):
		self.similarity_slider_description_label.configure(text=f"Similarity: {value:3.2f}")
		self._tts_client.similarity = value
	
	def style_slider_callback(self, value):
		self.style_slider_description_label.configure(text=f"Style: {value:3.2f}")
		self._tts_client.style = value
	
	def speaker_boost_checkbox_event(self):
		self._tts_client.speaker_boost = self.speaker_boost_checkbox.get()
	
	def preview_button_callback(self):
		print(f"Playing preview with {self._tts_client.SERVICE_NAME} | Text: {self.preview_text_entry.get()} | Voice: {self.voice_select.get()}")
		self._tts_client.play_text(self.preview_text_entry.get())

class AmazonPollyTTSTTSFrame(customtkinter.CTkFrame):
	def __init__(self, master, **kwargs):
		super().__init__(master, **kwargs)
		
		self._tts_client = AmazonPollyTTS(CONFIG["amazonpolly"]["aws_access_key_id"], CONFIG["amazonpolly"]["aws_secret_access_key"], voice_id="Ruth")
		
		self._voices = self._tts_client.get_voices()
		lang_values = []
		
		for voice in self._voices:
			if voice.get("LanguageCode") not in lang_values:
				lang_values.append(voice.get("LanguageCode"))
		
		lang_values.sort()
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
	
		# add widgets onto the frame, for example:
		self.label = customtkinter.CTkLabel(self, text="Amazon Polly Text-to-Speech", font=customtkinter.CTkFont(size=20, weight="bold"))
		self.label.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
		
		self.language_select = customtkinter.CTkOptionMenu(self, values=lang_values, command=self.language_select_callback)
		self.language_select.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
		self.voice_select = customtkinter.CTkOptionMenu(self, command=self.voice_select_callback)
		self.voice_select.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
		self.language_select_callback(lang_values[0])
		
		self.preview_text_entry_description_label = customtkinter.CTkLabel(self, text="Test Phrase", justify=customtkinter.LEFT)
		self.preview_text_entry_description_label.grid(row=6, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.preview_text_entry = customtkinter.CTkEntry(self, textvariable=customtkinter.StringVar(value='trainer signal recovered'), placeholder_text="trainer signal recovered")
		self.preview_text_entry.grid(row=7, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		
		self.preview_button = customtkinter.CTkButton(self, height=40, width=120, text="Play", font=customtkinter.CTkFont(size=18, weight="bold"), command=self.preview_button_callback)
		self.preview_button.grid(row=8, column=0, pady=(0,20), columnspan=2)
	
	def language_select_callback(self, value):
		selected_voice_names = []
		for voice in self._voices:
			if voice.get("LanguageCode").startswith(value):
				selected_voice_names.append(voice.get("Id"))
		
		selected_voice_names.sort()
		self._tts_client.language = value
		self.voice_select.configure(values=selected_voice_names)
		self.voice_select.set(selected_voice_names[0])
		self.voice_select_callback(selected_voice_names[0])
	
	def voice_select_callback(self, value):
		self._tts_client.voice_id = value
	
	def preview_button_callback(self):
		print(f"Playing preview with {self._tts_client.SERVICE_NAME} | Text: {self.preview_text_entry.get()} | Voice: {self.voice_select.get()}")
		self._tts_client.play_text(self.preview_text_entry.get())

class MicrosoftAzureTTSFrame(customtkinter.CTkFrame):
	def __init__(self, master, **kwargs):
		super().__init__(master, **kwargs)
		
		self._tts_client = MicrosoftAzureTTS(CONFIG["microsoftazure"]["speech_security_key"])
		
		self._voices = self._tts_client.get_voices()
		lang_values = []
		
		for voice in self._voices:
			if voice.locale not in lang_values:
				lang_values.append(voice.locale)
		
		lang_values.sort()
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
	
		# add widgets onto the frame, for example:
		self.label = customtkinter.CTkLabel(self, text="Microsoft Azure Text-to-Speech", font=customtkinter.CTkFont(size=20, weight="bold"))
		self.label.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
		
		self.language_select = customtkinter.CTkOptionMenu(self, values=lang_values, command=self.language_select_callback)
		self.language_select.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
		self.voice_select = customtkinter.CTkOptionMenu(self, command=self.voice_select_callback)
		self.voice_select.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
		self.language_select_callback(lang_values[0])

		self.rate_slider_description_label = customtkinter.CTkLabel(self, text="Speaking rate: 1")
		self.rate_slider_description_label.grid(row=2, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.rate_slider = customtkinter.CTkSlider(self, command=self.rate_slider_callback, from_=0.5, to=2.0)
		self.rate_slider.grid(row=3, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		self.rate_slider.set(1)
		
		self.pitch_slider_description_label = customtkinter.CTkLabel(self, text="Pitch: 0")
		self.pitch_slider_description_label.grid(row=4, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.pitch_slider = customtkinter.CTkSlider(self, command=self.pitch_slider_callback, from_=-50, to=50, number_of_steps=100)
		self.pitch_slider.grid(row=5, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		self.pitch_slider.set(0)
		
		self.preview_text_entry_description_label = customtkinter.CTkLabel(self, text="Test Phrase", justify=customtkinter.LEFT)
		self.preview_text_entry_description_label.grid(row=6, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.preview_text_entry = customtkinter.CTkEntry(self, textvariable=customtkinter.StringVar(value='trainer signal recovered'), placeholder_text="trainer signal recovered")
		self.preview_text_entry.grid(row=7, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		
		self.preview_button = customtkinter.CTkButton(self, height=40, width=120, text="Play", font=customtkinter.CTkFont(size=18, weight="bold"), command=self.preview_button_callback)
		self.preview_button.grid(row=8, column=0, pady=(0,20), columnspan=2)
	
	def language_select_callback(self, value):
		selected_voice_names = []
		for voice in self._voices:
			if voice.locale.startswith(value):
				selected_voice_names.append(voice.short_name)
		
		selected_voice_names.sort()
		self._tts_client.language = value
		self.voice_select.configure(values=selected_voice_names)
		self.voice_select.set(selected_voice_names[0])
		self.voice_select_callback(selected_voice_names[0])
	
	def voice_select_callback(self, value):
		self._tts_client.voice_id = value
	
	def rate_slider_callback(self, value):
		self.rate_slider_description_label.configure(text=f"Speaking rate: {value:3.2f}")
		self._tts_client.speaking_rate = value

	def pitch_slider_callback(self, value):
		self.pitch_slider_description_label.configure(text=f"Pitch: {value}")
		self._tts_client.pitch = value
	
	def preview_button_callback(self):
		print(f"Playing preview with {self._tts_client.SERVICE_NAME} | Text: {self.preview_text_entry.get()} | Voice: {self.voice_select.get()}")
		self._tts_client.play_text(self.preview_text_entry.get())

class IBMWatsonTTSFrame(customtkinter.CTkFrame):
	def __init__(self, master, **kwargs):
		super().__init__(master, **kwargs)
		
		self._tts_client = IBMWatsonTTS(CONFIG["ibmwatson"]["api_key"], CONFIG["ibmwatson"]["api_url"])
		
		self._voices = self._tts_client.get_voices()
		lang_values = []
		
		for voice in self._voices:
			if voice.get("language") not in lang_values:
				lang_values.append(voice.get("language"))
		
		lang_values.sort()
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
	
		# add widgets onto the frame, for example:
		self.label = customtkinter.CTkLabel(self, text="IBM Watson Text-to-Speech", font=customtkinter.CTkFont(size=20, weight="bold"))
		self.label.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
		
		self.language_select = customtkinter.CTkOptionMenu(self, values=lang_values, command=self.language_select_callback)
		self.language_select.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
		self.voice_select = customtkinter.CTkOptionMenu(self, command=self.voice_select_callback)
		self.voice_select.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
		self.language_select_callback(lang_values[0])
		
		self.rate_slider_description_label = customtkinter.CTkLabel(self, text="Speaking rate: 0")
		self.rate_slider_description_label.grid(row=2, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.rate_slider = customtkinter.CTkSlider(self, command=self.rate_slider_callback, from_=20, to=170, number_of_steps=150)
		self.rate_slider.grid(row=3, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		self.rate_slider.set(0)
		
		self.pitch_slider_description_label = customtkinter.CTkLabel(self, text="Pitch: 0")
		self.pitch_slider_description_label.grid(row=4, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.pitch_slider = customtkinter.CTkSlider(self, command=self.pitch_slider_callback, from_=-100, to=100, number_of_steps=200)
		self.pitch_slider.grid(row=5, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		self.pitch_slider.set(0)
		
		self.preview_text_entry_description_label = customtkinter.CTkLabel(self, text="Test Phrase", justify=customtkinter.LEFT)
		self.preview_text_entry_description_label.grid(row=6, column=0, padx=20, pady=(10,0), sticky="w", columnspan=2)

		self.preview_text_entry = customtkinter.CTkEntry(self, textvariable=customtkinter.StringVar(value='trainer signal recovered'), placeholder_text="trainer signal recovered")
		self.preview_text_entry.grid(row=7, column=0, padx=20, pady=(0,20), sticky="ew", columnspan=2)
		
		self.preview_button = customtkinter.CTkButton(self, height=40, width=120, text="Play", font=customtkinter.CTkFont(size=18, weight="bold"), command=self.preview_button_callback)
		self.preview_button.grid(row=8, column=0, pady=(0,20), columnspan=2)
	
	def language_select_callback(self, value):
		selected_voice_names = []
		for voice in self._voices:
			if voice.get("language").startswith(value):
				selected_voice_names.append(voice.get("name"))
		
		selected_voice_names.sort()
		self._tts_client.language = value
		self.voice_select.configure(values=selected_voice_names)
		self.voice_select.set(selected_voice_names[0])
		self.voice_select_callback(selected_voice_names[0])
	
	def voice_select_callback(self, value):
		self._tts_client.voice_name = value
	
	def rate_slider_callback(self, value):
		self.rate_slider_description_label.configure(text=f"Speaking rate: {value}")
		self._tts_client.speaking_rate = value

	def pitch_slider_callback(self, value):
		self.pitch_slider_description_label.configure(text=f"Pitch: {value}")
		self._tts_client.pitch = value
	
	def preview_button_callback(self):
		print(f"Playing preview with {self._tts_client.SERVICE_NAME} | Text: {self.preview_text_entry.get()} | Voice: {self.voice_select.get()}")
		self._tts_client.play_text(self.preview_text_entry.get())

class App(customtkinter.CTk):
	def __init__(self):
		super().__init__()
		
		customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
		customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

		self.title("Jasper TTS Tester")
		self.geometry("700x600")
		
		# set grid layout 1x2
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		
		# create navigation frame
		self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
		self.navigation_frame.grid(row=0, column=0, sticky="nsew")
		self.navigation_frame.grid_rowconfigure(4, weight=1)
		
		self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="Jasper TTS Tester", font=customtkinter.CTkFont(size=20, weight="bold"))
		self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
		
		self.tts_option_menu = customtkinter.CTkOptionMenu(self.navigation_frame, width=150, values=["Google TTS", "ElevenLabsTTS", "Amazon Polly TTS", "Microsoft Azure TTS", "IBM Watson TTS"],  anchor="w", command=self.tts_option_callback)
		self.tts_option_menu.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
		
		self.googletts_frame = GoogleTTSFrame(master=self)
		self.elevenlabs_frame = ElevenLabsTTSFrame(master=self)
		self.amazonpolly_frame = AmazonPollyTTSTTSFrame(master=self)
		self.microsoftazure_frame = MicrosoftAzureTTSFrame(master=self)
		self.ibmwatson_frame = IBMWatsonTTSFrame(master=self)
		
		self.tts_option_callback("Google TTS")
	
	def tts_option_callback(self, value):
		if value == "Google TTS":
			self.googletts_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
		else:
			self.googletts_frame.grid_forget()
			
		if value == "ElevenLabsTTS":
			self.elevenlabs_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
		else:
			self.elevenlabs_frame.grid_forget()
		
		if value == "Amazon Polly TTS":
			self.amazonpolly_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
		else:
			self.amazonpolly_frame.grid_forget()
		
		if value == "Microsoft Azure TTS":
			self.microsoftazure_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
		else:
			self.microsoftazure_frame.grid_forget()
		
		if value == "IBM Watson TTS":
			self.ibmwatson_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
		else:
			self.ibmwatson_frame.grid_forget()


if __name__ == "__main__":
	load_config()

	app = App()
	app.mainloop()
