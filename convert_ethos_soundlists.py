import csv
import os

SOURCE_DIR = "convert"
OUTPUT_DIR = f"soundlists{os.sep}ethos"
AUDIO_PATH = "audio/LANG/system"

def convert_csv_file(convert_dir, output_dir, source_file):
	with open(f"{convert_dir}{os.sep}{source_file}", "r", encoding="utf-8-sig") as csv_content:
		with open(f"{output_dir}{os.sep}{source_file}", "w", newline="", encoding="UTF-8") as file:
			writer = csv.writer(file)
			lang = source_file.replace(".csv", "").split("_")[1]

			csv_reader = csv.reader(csv_content, delimiter=",")
			for row in csv_reader:
				if row[0] == "filename":
					print("Skipping header row..")
					continue

				new_row = []
				new_row.append(AUDIO_PATH.replace("LANG", lang))
				new_row.append(row[0])
				new_row.append(row[1].strip())
				writer.writerow(new_row)

def convert_files():
	files_to_convert = os.listdir(SOURCE_DIR)

	for file in files_to_convert:
		if not file.endswith(".csv"):
			continue
		print(f"Converting '{file}..")
		convert_csv_file(SOURCE_DIR, OUTPUT_DIR, file)

convert_files()
