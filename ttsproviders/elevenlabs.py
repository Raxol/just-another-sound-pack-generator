from elevenlabs import (Voice, VoiceSettings, generate, play, save,
                        set_api_key, voices)

from .ttsprovider import TTSProvider


class ElevenLabsTTS(TTSProvider):
	SERVICE_NAME = "ElevenLabs TTS"

	def __init__(self, api_key=None, voice_id="", stability=None, similarity=None, style=None, speaker_boost=None):
		if api_key is not None:
			set_api_key(api_key)
		
		self._voice_id = voice_id
		self._voice_settings = VoiceSettings.from_voice_id(self._voice_id)
		
		if stability is not None and isinstance(stability, float):
			self._voice_settings.stability = stability
		
		if similarity is not None and isinstance(similarity, float):
			self._voice_settings.similarity_boost = similarity
		
		if style is not None and isinstance(style, float):
			self._voice_settings.style = style
		
		if speaker_boost is not None and isinstance(speaker_boost, bool):
			self._voice_settings.use_speaker_boost = speaker_boost
		
		print(f"{self.SERVICE_NAME} setup: Voice ID: {self._voice_id}")
	
	@property
	def voice_id(self):
		return self._voice_id
	
	@voice_id.setter
	def voice_id(self, voice):
		if not isinstance(voice, str):
			raise TypeError("Voice id/name must be a string")
		self._voice_id = voice
		self._voice_settings = VoiceSettings.from_voice_id(self._voice_id)
	
	@property
	def stability(self):
		return self._voice_settings.stability
	
	@stability.setter
	def stability(self, value):
		try:
			_value = float(value)
			if 0.0 <= _value <= 1.0:
				self._voice_settings.stability = _value
			else:
				raise ValueError("stability must be between 0.0 and 1.0")
		except TypeError as e:
			raise TypeError("stability value must be a valid float") from e
	
	@property
	def similarity(self):
		return self._voice_settings.similarity_boost
	
	@similarity.setter
	def similarity(self, value):
		try:
			_value = float(value)
			if 0.0 <= _value <= 1.0:
				self._voice_settings.similarity_boost = _value
			else:
				raise ValueError("similarity_boost must be between 0.0 and 1.0")
		except TypeError as e:
			raise TypeError("similarity_boost value must be a valid float") from e
	
	@property
	def style(self):
		return self._voice_settings.style
	
	@style.setter
	def style(self, value):
		try:
			_value = float(value)
			if 0.0 <= _value <= 1.0:
				self._voice_settings.style = _value
			else:
				raise ValueError("style must be between 0.0 and 1.0")
		except TypeError as e:
			raise TypeError("style value must be a valid float") from e
	
	@property
	def speaker_boost(self):
		return self._voice_settings.use_speaker_boost
	
	@speaker_boost.setter
	def speaker_boost(self, value):
		try:
			_value = bool(value)
			self._voice_settings.use_speaker_boost = _value
		except TypeError as e:
			raise TypeError("speaker_boost must be boolean") from e
		
	
	def play_text(self, text):
		print(f"{self.SERVICE_NAME}: Playing Text..")
		play(self._generate_tts_output(text))
	
	def save_file(self, text, file_path):
		print(f"{self.SERVICE_NAME}: Saving file..")
		TTSProvider.save_and_convert_file(self._generate_tts_output(text), "mp3", file_path)
		print(f"{self.SERVICE_NAME}: Audio content written to file {file_path}")
	
	def get_voices(self):
		return voices()
	
	def _generate_tts_output(self, text):
		audio = generate(
			text=text,
			voice=Voice(
				voice_id=self._voice_id,
				settings=self._voice_settings
			),
			model="eleven_multilingual_v2",
		)
		return audio
