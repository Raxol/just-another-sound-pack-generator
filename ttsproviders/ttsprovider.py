import os
from abc import ABC, abstractmethod

from pydub import AudioSegment

TEMP_DIR = "temp"


class TTSProvider(ABC):
	SERVICE_NAME = "TTS Service"
	_apply_eq = False

	@abstractmethod
	def play_text(self, text):
		pass

	@abstractmethod
	def save_file(self, text, file_path, apply_eq=False):
		pass
	
	@abstractmethod
	def get_voices(self):
		pass

	@property
	def apply_eq(self):
		return self._apply_eq
	
	@apply_eq.setter
	def apply_eq(self, value):
		try:
			_value = bool(value)
			self._apply_eq = _value
		except TypeError as e:
			raise TypeError("apply_eq must be boolean") from e

	def set_property_by_name(self, name, value):
		if hasattr(self, name):
			setattr(self, name, value)
		else:
			raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'", name=name, obj=self)
	
	@staticmethod
	def save_and_convert_file(audio_data, input_format, file_path, apply_eq=False):
		try:
			tts_output = f"{TEMP_DIR}{os.sep}audio_file.{input_format}"

			if not os.path.exists(os.path.dirname(tts_output)):
				os.makedirs(os.path.dirname(tts_output))

			with open(tts_output, "wb") as out:
				out.write(audio_data)
				print(f"Temporary audio content written to file {tts_output}")
			if apply_eq:
				# TODO: Take a look at https://github.com/jiaaro/pydub/blob/master/pydub/scipy_effects.py#L119
				# 		scipy_effects does offer an eq function, maybe this could streamline this function a bit more
				eq_file = f"{TEMP_DIR}{os.sep}eq.wav"
				temp_file = AudioSegment.from_file(tts_output)
				ffmpeg_parameters = [
					"-ac", "1",
					"-ar", "32000",
					"-af", "equalizer=f=100:width_type=h:width=1800:g=-8,equalizer=f=10000:width_type=h:width=18000:g=7,silenceremove=start_periods=1:start_silence=0.075:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse"
				]
				temp_file.export(eq_file, format="wav", parameters=ffmpeg_parameters)
				temp_file = AudioSegment.from_file(eq_file)
				temp_file.apply_gain(1).high_pass_filter(200).normalize(0.5).export(file_path, format="wav")
			else:
				temp_file = AudioSegment.from_file(tts_output)
				ffmpeg_parameters = [
					"-ac", "1",
					"-ar", "32000",
					"-af", "silenceremove=start_periods=1:start_silence=0.075:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse"
				]
				temp_file.apply_gain(1).normalize(0.5).export(file_path, format="wav", parameters=ffmpeg_parameters)
			
		finally:
			print(f"Audio file saved: {file_path}")
			os.remove(tts_output)
			if apply_eq:
				os.remove(eq_file)
