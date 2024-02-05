import io

import sounddevice as sd
import soundfile as sf
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1

from .ttsprovider import TTSProvider


class IBMWatsonTTS(TTSProvider):
	SERVICE_NAME = "IBM Watson TTS"

	def __init__(self, api_key, api_url, voice_name="en-US_MichaelV3Voice", speaking_rate=0, pitch=0):
		self._voice_name = voice_name
		self._speaking_rate = speaking_rate
		self._pitch = pitch
		
		authenticator = IAMAuthenticator(api_key)
		self._text_to_speech = TextToSpeechV1(
			authenticator=authenticator
		)
		self._text_to_speech.set_service_url(api_url)
		
		print(f"{self.SERVICE_NAME} setup: Selected voice: {self._voice_name}")
	
	@property
	def voice_name(self):
		return self._voice_name
	
	@voice_name.setter
	def voice_name(self, name):
		if not isinstance(name, str):
			raise TypeError("Voice id/name must be a string")
		self._voice_name = name
	
	@property
	def speaking_rate(self):
		return self._speaking_rate
	
	@speaking_rate.setter
	def speaking_rate(self, value):
		try:
			_value = int(value)
			if 20 <= _value <= 170:
				self._speaking_rate = _value
			else:
				raise ValueError("speaking_rate must be between 20 and 170")
		except TypeError as e:
			raise TypeError("speaking_rate value must be a valid integer") from e
	
	@property
	def pitch(self):
		return self._pitch
	
	@pitch.setter
	def pitch(self, value):
		try:
			_value = int(value)
			if -100 <= _value <= 100:
				self._pitch = _value
			else:
				raise ValueError("pitch must be between -100 and 100")
		except TypeError as e:
			raise TypeError("pitch value must be a valid integer") from e
	
	def play_text(self, text):
		print(f"{self.SERVICE_NAME}: Playing Text..")
		
		response = self._generate_tts_output(text)
		
		with io.BytesIO(response.content) as file:
			data, samplerate = sf.read(file)			
			sd.play(data, samplerate=samplerate, blocking=True)
	
	def save_file(self, text, file_path):
		print(f"{self.SERVICE_NAME}: Saving file..")
		
		response = self._generate_tts_output(text)

		TTSProvider.save_and_convert_file(response.content, "wav", file_path)
	
	def get_voices(self):
		voices = self._text_to_speech.list_voices().get_result()
		return voices["voices"]
		
	def _generate_tts_output(self, text):
		print("Generating IBM Watson TTS Output..")
		
		return self._text_to_speech.synthesize(
			text, 
			accept='audio/wav;rate=32000', 
			voice=self._voice_name, 
			rate_percentage=self._speaking_rate, 
			pitch_percentage=self._pitch
		).get_result()
