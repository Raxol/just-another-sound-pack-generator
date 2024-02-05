import io

import sounddevice as sd
import soundfile as sf
from google.cloud import texttospeech
from google.oauth2 import service_account

from .ttsprovider import TTSProvider


class GoogleTTS(TTSProvider):
	SERVICE_NAME = "Google Cloud TTS"

	def __init__(self, credentials_file, language="en-GB", voice_name="en-GB-Neural2-A", speaking_rate=1.0, pitch=0.0, sample_rate_hertz=32000):
		self._language = language
		self._voice_name = voice_name
		self._speaking_rate = speaking_rate
		self._pitch = pitch
		self._sample_rate_hertz = sample_rate_hertz
		
		credentials = service_account.Credentials.from_service_account_file(credentials_file)
		self._client = texttospeech.TextToSpeechClient(credentials=credentials)
		print(f"{self.SERVICE_NAME} setup: Selected voice: {self._voice_name}")
	
	@property
	def language(self):
		return self._language
	
	@language.setter
	def language(self, lang):
		if not isinstance(lang, str):
			raise TypeError("language must be a string")
		self._language = lang
	
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
			_value = float(value)
			if 0.25 <= _value <= 4.0:
				self._speaking_rate = _value
			else:
				raise ValueError("speaking_rate must be between 0.25 and 4.0")
		except TypeError as e:
			raise TypeError("speaking_rate value must be a valid float") from e
	
	
	@property
	def pitch(self):
		return self._pitch
	
	@pitch.setter
	def pitch(self, value):
		try:
			_value = float(value)
			if -20.0 <= _value <= 20.0:
				self._pitch = _value
			else:
				raise ValueError("pitch must be between -20.0 and 20.0")
		except TypeError as e:
			raise TypeError("pitch value must be a valid float") from e
	
	@property
	def sample_rate_hertz(self):
		return self._sample_rate_hertz
	
	@sample_rate_hertz.setter
	def sample_rate_hertz(self, value):
		try:
			_value = int(value)
			if 24000 <= _value <= 48000:
				self._sample_rate_hertz = _value
			else:
				raise ValueError("sample_rate_hertz must be between 24000 and 48000")
		except TypeError as e:
			raise TypeError("sample_rate_hertz value must be a valid integer") from e
	
	def play_text(self, text):
		print(f"{self.SERVICE_NAME}: Playing Text..")
		
		response = self._generate_tts_output(text)
		
		with io.BytesIO(response.audio_content) as file:
			data, samplerate = sf.read(file)			
			sd.play(data, samplerate=samplerate, blocking=True)
	
	def save_file(self, text, file_path):
		print(f"{self.SERVICE_NAME}: Saving file..")
		
		response = self._generate_tts_output(text)

		TTSProvider.save_and_convert_file(response.audio_content, "wav", file_path)
		
		#with open(file_path, "wb") as out:
		#	out.write(response.audio_content)
		#	print(f"{self.SERVICE_NAME}: Audio content written to file {file_path}")
	
	def get_voices(self):
		request = texttospeech.ListVoicesRequest()

		response = self._client.list_voices(request=request)
		
		return response.voices
		
	def _generate_tts_output(self, text):
		if text.startswith("<speak"):
			synthesis_input = texttospeech.SynthesisInput(ssml=text)
		else:
			synthesis_input = texttospeech.SynthesisInput(text=text)
		
		
		voice = texttospeech.VoiceSelectionParams(
			language_code=self._language, name=self._voice_name
		)

		audio_config = texttospeech.AudioConfig(
			audio_encoding=texttospeech.AudioEncoding.LINEAR16,
			speaking_rate = self._speaking_rate,
			pitch = self._pitch,
			sample_rate_hertz=self._sample_rate_hertz
		)

		response = self._client.synthesize_speech(
			input=synthesis_input, voice=voice, audio_config=audio_config
		)
		
		return response
