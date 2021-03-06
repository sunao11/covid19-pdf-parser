# pip install pdfplumber pandas
import sys
import pdfplumber
import pandas as pd

output_txt = open('data/manual_output.csv', 'w')

with open(sys.argv[1], 'rb') as f:
	pdf = pdfplumber.open(f.name)
	df = pd.DataFrame(columns=["確定陽性者", "性別", "年齢", "発病日", "確定日", "居住地", "職業", "推定感染経路"])
	for page in pdf.pages:
		# Start convert Table from page 3
		if page.page_number >= 3:
			# clean up the invisible text hidden by the clips
			cleanPage = page.filter(lambda obj: obj["non_stroking_color"] != (1,1,1))

			tables = cleanPage.extract_tables({
				"vertical_strategy": "text",
				"horizontal_strategy": "lines",
				"intersection_y_tolerance": 15,
				"min_words_horizontal": 2,
			})

			for table in tables:
				localDf = pd.DataFrame(table, columns=["確定陽性者", "性別", "年齢", "発病日", "確定日", "居住地", "職業", "推定感染経路"])
				localDf = localDf.replace('\n','', regex=True)

				# Remove each page's header row
				indexNames = localDf[ localDf['確定陽性者'] == "確定陽性者" ].index
				localDf.drop(indexNames , inplace=True)

				# TODO: Replace date format
				prepend_year = '2020'
				find_pattern = r"^(?P<m>\d*)月(?P<d>\d*)\D*"
				replace_pattern = lambda date: prepend_year + '/' + date.group('m') + '/' + date.group('d')
				localDf['発病日'] = localDf['発病日'].str.replace(find_pattern, replace_pattern, regex=True)
				localDf['確定日'] = localDf['確定日'].str.replace(find_pattern, replace_pattern, regex=True)
				df = df.append(localDf)

	df.to_csv(output_txt, index=False, header=True)
	print("CSV file created at: data/manual_output.csv")
