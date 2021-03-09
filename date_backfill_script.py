import glob, pandas, os, sys
import data_annotation

'''
This is (ideally) a one-time backfill script for the purpose of pulling the date information
from the folder that a csv is in and adding it as a column to the actual csv, for the purpose
of making it easier to use downstream when we plot multiple experiments at the same time.
'''

if __name__ == "__main__":
	folder = sys.argv[1]
	dates = sys.argv[2:]

	for date in dates:
		glob_paths = glob.glob(os.path.join(folder, f'{date}*', 'data', '*processed_data*.csv'))
		glob_paths += glob.glob(os.path.join(folder, f'data_{date}', '*processed_data*.csv'))

		for file in glob_paths:
			data = data_annotation.AnnotatedData([file])
			data.load_annotated_files()
			data.set_date(date)
			data.save()
