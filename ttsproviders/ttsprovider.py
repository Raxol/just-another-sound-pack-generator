import os
from abc import ABC, abstractmethod

from pydub import AudioSegment


class TTSProvider(ABC):
	SERVICE_NAME = "TTS Service"

	@abstractmethod
	def play_text(self, text):
		pass

	@abstractmethod
	def save_file(self, text, file_path):
		pass
	
	@abstractmethod
	def get_voices(self):
		pass

	def set_property_by_name(self, name, value):
		if hasattr(self, name):
			setattr(self, name, value)
		else:
			raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'", name=name, obj=self)
	
	@staticmethod
	def save_and_convert_file(audio_data, input_format, file_path):
		temp_file_path = f"temp{os.sep}audio_file.{input_format}"

		if not os.path.exists(os.path.dirname(temp_file_path)):
				os.makedirs(os.path.dirname(temp_file_path))

		with open(temp_file_path, "wb") as out:
			out.write(audio_data)
			print(f"Temporary audio content written to file {temp_file_path}")
		
		temp_file = AudioSegment.from_file(temp_file_path)
		ffmpeg_parameters = [
			"-ac", "1",
			"-ar", "32000",
			"-af", "silenceremove=start_periods=1:start_silence=0.075:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse"
		]
		temp_file.normalize(1).apply_gain(-4).export(file_path, format="wav", parameters=ffmpeg_parameters)

		print(f"Audio file saved: {file_path}")
		os.remove(temp_file_path)
