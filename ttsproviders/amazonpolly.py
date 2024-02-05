import io

import boto3
import sounddevice as sd
import soundfile as sf

from .ttsprovider import TTSProvider


class AmazonPollyTTS(TTSProvider):
	SERVICE_NAME = "Amazon Polly TTS"

	def __init__(self, aws_access_key_id, aws_secret_access_key, region_name="eu-central-1", language="en-GB", engine="neural", voice_id="Kimberly"):
		self._language = language
		self._voice_id = voice_id
		self._engine = engine
		
		session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
		self._client = session.client('polly')
		
		print(f"{self.SERVICE_NAME} setup: Selected voice: {self._voice_id}")
	
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
	
	def play_text(self, text):
		print(f"{self.SERVICE_NAME}: Playing Text..")
		
		response = self._generate_tts_output(text)
		
		with io.BytesIO(response["AudioStream"].read()) as file:
			data, samplerate = sf.read(file)			
			sd.play(data, samplerate=samplerate, blocking=True)
	
	def save_file(self, text, file_path):
		print(f"{self.SERVICE_NAME}: Saving file..")
		
		response = self._generate_tts_output(text)

		TTSProvider.save_and_convert_file(response.get('AudioStream').read(), "mp3", file_path)
		
		#with open(file_path, "wb") as out:
		#	out.write(response.get('AudioStream').read())
		#	print(f"{self.SERVICE_NAME}: Audio content written to file {file_path}")
	
	def get_voices(self):
		voices = []
		
		response = self._client.describe_voices(Engine=self._engine)
		
		for v in response.get("Voices"):
			voices.append(v)
		
		while response.get("NextToken") is not None:
			response = self._client.describe_voices(Engine=self._engine)

			for v in response.get("Voices"):
				voices.append(v)
		
		return voices
		
	def _generate_tts_output(self, text):
		if text.startswith("<speak"):
			type = "ssml"
		else:
			type = "text"
		
		response = self._client.synthesize_speech(
			Engine=self._engine,
			LanguageCode=self._language,
			OutputFormat='mp3',
			Text=text,
			TextType=type,
			VoiceId=self._voice_id
		)
		
		return response
