import argparse
import csv
import os
import sys

import yaml

from ttsproviders.amazonpolly import AmazonPollyTTS
from ttsproviders.elevenlabs import ElevenLabsTTS
from ttsproviders.googletts import GoogleTTS
from ttsproviders.ibmwatson import IBMWatsonTTS
from ttsproviders.microsoftazure import MicrosoftAzureTTS

OUTPUT_DIRECTORY = "output"
JASPER_VERSION = "v1.0"


def load_config():
	try:
		with open("config.yaml", "r") as file:
			config = yaml.safe_load(file)
			print("Config file loaded.")
	except yaml.YAMLError as error:
		print(f"Error parsing YAML config file: {error}")
		sys.exit(1)
	except FileNotFoundError:
		print("Config file missing. Copy & edit config_example.yaml")
		sys.exit(1)
	return config

def read_csv_file_and_create_audio(csv_file, output_dir, soundpack_dir, tts_client):
	character_count = 0
	with open(csv_file, "r") as csv_content:
		dialect = csv.Sniffer().sniff(csv_content.read(), delimiters=";,")
		csv_content.seek(0)
		csv_reader = csv.reader(csv_content, dialect=dialect)
		for row in csv_reader:
			file_dir = row[0]
			file_name = row[1]
			complete_path = f"{output_dir}{os.sep}{soundpack_dir}{os.sep}{file_dir}{os.sep}{file_name}"
			text = row[2]

			if text is None or text == "":
				print(f"Empty text for {file_name}. Skipping entry..")
				continue
			
			if not os.path.exists(os.path.dirname(complete_path)):
				os.makedirs(os.path.dirname(complete_path))
			
			tts_client.save_file(text, complete_path)
			character_count += len(text)
	print(f"Synthesized {character_count} characters")

def init_tts_client(service, config, overwrites, enhancement):
	try:
		config = load_config()
		
		print("Initializing TTS Client")
		if service == "google":
			if not os.path.isfile(r"googletts_cred.json"):
				print("Missing Google TTS credentials file!")
				sys.exit(1)
			
			client = GoogleTTS(
				credentials_file = 	r"googletts_cred.json",
				language = 			config["googletts"]["language"], 
				voice_name = 		config["googletts"]["voice_name"], 
				speaking_rate = 	float(config["googletts"]["speaking_rate"]),
				pitch = 			float(config["googletts"]["pitch"]), 
				sample_rate_hertz = int(config["googletts"]["sample_rate"])
			)
				
		elif service == "elevenlabs":
			client = ElevenLabsTTS(
				api_key = 		config["elevenlabs"]["api_key"],
				voice_id = 		config["elevenlabs"]["voice_id"],
				stability = 	float(config["elevenlabs"]["stability"]),
				similarity = 	float(config["elevenlabs"]["similarity"]),
				style = 		float(config["elevenlabs"]["style"]),
				speaker_boost = bool(config["elevenlabs"]["speaker_boost"])
			)
		elif service == "amazon":
			client = AmazonPollyTTS(
				aws_access_key_id = 	config["amazonpolly"]["aws_access_key_id"],
				aws_secret_access_key = config["amazonpolly"]["aws_secret_access_key"],
				region_name = 			config["amazonpolly"]["region_name"],
				language = 				config["amazonpolly"]["language"],
				engine = 				config["amazonpolly"]["engine"],
				voice_id = 				config["amazonpolly"]["voice_id"]
			)
		elif service == "microsoft":
			client = MicrosoftAzureTTS(
				speech_security_key = 	config["microsoftazure"]["speech_security_key"],
				region_name = 			config["microsoftazure"]["region_name"],
				language = 				config["microsoftazure"]["language"],
				voice_id = 				config["microsoftazure"]["voice_id"],
				speaking_rate = 		float(config["microsoftazure"]["speaking_rate"]),
				pitch = 				int(config["microsoftazure"]["pitch"]),
				output_format = 		config["microsoftazure"]["output_format"]
			)
		elif service == "ibm":
			client = IBMWatsonTTS(
				api_key = 		config["ibmwatson"]["api_key"],
				api_url = 		config["ibmwatson"]["api_url"],
				voice_name = 	config["ibmwatson"]["voice_name"],
				speaking_rate = int(config["ibmwatson"]["speaking_rate"]),
				pitch = 		int(config["ibmwatson"]["pitch"])
			)
		else:
			print("Service not found. Exiting..")
			sys.exit(1)
		
		if overwrites is not None:
			attributes = overwrites.split(",")
			for att_line in attributes:
				att = att_line.split("=")
				client.set_property_by_name(att[0], att[1])
		
		client.set_property_by_name("apply_eq", enhancement)		
		
		return client

	except Exception as e:
		print(f"Error on initilization: {e}")
		sys.exit(1)


def main(csv_file, service, soundpack_dir, overwrites, enhancement):
	print(f"Welcome to Jasper {JASPER_VERSION}")
	print("Just Another Sound Pack genERator")
	tts_client = init_tts_client(service, load_config(), overwrites, enhancement)
	read_csv_file_and_create_audio(csv_file, OUTPUT_DIRECTORY, soundpack_dir, tts_client)
	#Add disclaimer.txt to sound pack folder
	with open(f"{OUTPUT_DIRECTORY}{os.sep}{soundpack_dir}{os.sep}disclaimer.txt", "w") as file:
		file.write("The voices in this sound pack are AI-generated.")


if __name__ == "__main__":
	# Instantiate the parser
	parser = argparse.ArgumentParser(description="Generates sound files for OpenTX/Ethos/etc radios with TTS from various services")
	parser.add_argument("-s", "--service", choices=["google", "elevenlabs", "amazon", "microsoft", "ibm"], type=str, help="Use 'google', 'amazon', 'microsoft', 'elevenlabs' or 'ibm'", required=True)
	parser.add_argument("-f", "--file", type=str, help="CSV File to read from", required=True)
	parser.add_argument("-n", "--name", type=str, help="Name of the Soundpack", required=True)
	parser.add_argument("-o", "--overwrites", type=str, help="Overwrite settings from config: pitch=4,language=de-DE")
	parser.add_argument("-e", "--enhancement", help="Apply audio enhancement to output file (reduce lows/bass, boost highs/treble)", action="store_true")
	args = parser.parse_args()
	
	main(args.file, args.service, args.name, args.overwrites, args.enhancement)
	sys.exit(0)
