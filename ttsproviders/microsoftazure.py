import azure.cognitiveservices.speech as speechsdk

from .ttsprovider import TTSProvider


class MicrosoftAzureTTS(TTSProvider):
	SERVICE_NAME = "Microsoft Azure TTS"

	def __init__(self, speech_security_key, region_name="germanywestcentral", language="en-GB", voice_id="en-GB-LibbyNeural", speaking_rate = 1.0, pitch = 0, output_format="Riff48Khz16BitMonoPcm"):
		self._language = language
		self._speaking_rate = speaking_rate
		self._pitch = pitch
		self._voice_id = voice_id
		
		self._speech_config = speechsdk.SpeechConfig(subscription=speech_security_key, region=region_name)
		self._speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat[output_format])
		
		print(f"{self.SERVICE_NAME} setup: Selected voice: {voice_id}")
	
	@property
	def language(self):
		return self._language
	
	@language.setter
	def language(self, lang):
		if not isinstance(lang, str):
			raise TypeError("language must be a string")
		self._language = lang
	
	@property
	def voice_id(self):
		return self._voice_id
	
	@voice_id.setter
	def voice_id(self, name):
		if not isinstance(name, str):
			raise TypeError("Voice id/name must be a string")
		self._voice_id = name
	
	@property
	def speaking_rate(self):
		return self._speaking_rate
	
	@speaking_rate.setter
	def speaking_rate(self, value):
		try:
			_value = float(value)
			if 0.5 <= _value <= 2.0:
				self._speaking_rate = _value
			else:
				raise ValueError("speaking_rate must be between 0.5 and 2.0")
		except TypeError as e:
			raise TypeError("speaking_rate value must be a valid float") from e
	
	@property
	def pitch(self):
		return self._pitch
	
	@pitch.setter
	def pitch(self, value):
		try:
			_value = int(value)
			if -50 <= _value <= 50:
				self._pitch = _value
			else:
				raise ValueError("pitch must be between -50 and 50")
		except TypeError as e:
			raise TypeError("pitch value must be a valid float") from e
	
	def _get_ssml_text(self, text):
		# Only request pitch & rate if we changed it from the default value
		# every character between the <voice> tags will be billed 
		if self._pitch != 0 and self._speaking_rate != 1.0:
			print("both")
			text_insert = f"""<prosody pitch="{self._pitch}%" rate="{self._speaking_rate}">{text}</prosody>"""
		elif self._pitch != 0:
			print("only pitch")
			text_insert = f"""<prosody pitch="{self._pitch}%">{text}</prosody>"""
		elif self._speaking_rate != 1.0:
			print("only speaking rate")
			text_insert = f"""<prosody rate="{self._speaking_rate}">{text}</prosody>"""
		else:
			print("only text")
			text_insert = text
		
		return f"""
			<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{self._language}">
				<voice name="{self._voice_id}">{text_insert}</voice>
			</speak>"""
			
	
	def play_text(self, text):
		print(f"{self.SERVICE_NAME}: Playing Text..")
		ssml_text = self._get_ssml_text(text)
		speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self._speech_config)
		speech_synthesizer.speak_ssml(ssml_text)
	
	def save_file(self, text, file_path):
		print(f"{self.SERVICE_NAME}: Saving file..")

		ssml_text = self._get_ssml_text(text)

		speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self._speech_config, audio_config=None)
		
		result = speech_synthesizer.speak_ssml_async(ssml_text).get()

		if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
			print(f"Speech synthesized for text [{text}]")
			TTSProvider.save_and_convert_file(result.audio_data, "wav", file_path)
		elif result.reason == speechsdk.ResultReason.Canceled:
			cancellation_details = result.cancellation_details
			print(f"Speech synthesis canceled: {cancellation_details.reason}")
			if cancellation_details.reason == speechsdk.CancellationReason.Error:
				print(f"Error details: {cancellation_details.error_details}")
		
	
	def get_voices(self):
		response = speechsdk.SpeechSynthesizer(speech_config=self._speech_config, audio_config=None).get_voices_async().get()
		
		if response.reason == speechsdk.ResultReason.VoicesListRetrieved:
			return response.voices
		elif response.reason == speechsdk.ResultReason.Canceled:
			print(f"List Voices Request canceled; error details: {response.error_details}")
			return None
