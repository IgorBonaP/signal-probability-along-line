#%%
import pandas as pd
import numpy as np
from constants import (SKIP_FLAGS, SUMMARY_TITLE, LENGTHS_TITLE)
import pathlib
from datetime import date
from typing import Generator, Union, Tuple
#%%
COLUMNS = {
	"COORDS": "X",
	"SIGNAL": "Y",
	"SIGNAL CEILING": "Ceiling",
	"BIN COVERAGE": "Coverage",
	"SCORE": "Score",
	"COUNT": "Sum",
}

def load_data(csv: Union[str,pathlib.Path], lag: int=0)-> pd.DataFrame:
	'''
	Bins the first column of a two columnns table csv and calculates the percetange
	of signal present on each bin on the second columnn.
	Assumes that data is in the first 2 columns of the csv and that the first column contains
	X values and second contains Y value.

	Example:

	bin_size=0.2
	file.csv ------------------------> DataFrame
		X, Y							index | X 			| Y | Ceiling | Coverage
		0, 255							0		(0,0.2]		255		510		0.5
		1, 0							1		(0.2,0.4]	510		510		1
		2, 0							2		(0.4,0.6]	510		510		1
		3, 255							3		(0.6,0.8]	0		510		0
		4, 255							4		(0.8,0.1]	0		510		0
		5, 255
		6, 255
		7,0
		8,0
		9,0

	Second element of tuple would be 10 as this is the last X value in the csv.
	'''
	try:
		df = pd.read_csv(
		csv,
		usecols=[0,1],
		header=0,
		skiprows=[1,lag+2])

	except ValueError:
		raise SyntaxError("Bad csv syntax. Expecting ',' as delimiters.")
	else:
		return df

def bin_and_calculate_coverage(normalized_coords_line_scan_df:pd.DataFrame, bin_size: float)->pd.DataFrame:
	'''
	Categorizes the data in bins of proportional size defined by bin_size and calculates
	how much of each bin is filled with signal in relation to the maximum possible value
	contained in that bin.

	Bin_size should be a proportion (between 0 and 1)

	Example:

	DataFrame object with 10 rows, bin_size = 0.2

	Ouput will be a new dataframe with 5 rows, each of which with the sum of the
	binned rows under the Y column, the max signal for each bin under the Ceiling column
	and how much of a given bin is filled with signal under column Coverage.
	'''
	df = normalized_coords_line_scan_df.copy()

	if bin_size > 1 or bin_size <= 0:
		raise ValueError("Relative coordinate must be between 0 and 1.")

	number_of_bins = round(1/bin_size)
	if number_of_bins > len(df.index):
		raise ValueError("Number of bins cannot exceed the total size of the table.")
	max_value = get_max_grayvalue(check_bitdepth(df))

	categories = pd.qcut(df[COLUMNS["COORDS"]], number_of_bins, precision=1)
	categorized_df = df.groupby([categories.astype(str)])[COLUMNS["SIGNAL"]]

	binned_df = categorized_df.sum().reset_index()
	binned_df[COLUMNS["SIGNAL CEILING"]] = [np.multiply(max_value, size) for size in categorized_df.size().values]
	binned_df[COLUMNS["BIN COVERAGE"]] = binned_df[COLUMNS["SIGNAL"]]/binned_df[COLUMNS["SIGNAL CEILING"]]
	return binned_df

def summarize_signal_probability_along_line(csvdir: pathlib.Path,
	savepath: pathlib.Path,
	bin_size: float,
	threshold: float,
	lag: int=0,
	std_out=print)->Tuple[pd.DataFrame, dict]:
	'''
	Iterates over csvdir to score the presence of signal over the length of a linescan,
	calculates the propability of finding signal in each discrete region of the linescan, given by the bin_size,
	of all files contained on csvdir and extracts and saves the length of linescans.

	Returns a tuple with (Dataframe containing the penetrance summary, Dataframe with line_lengths).
	'''
	if not check_and_setup_dirs(csvdir, savepath, std_out=std_out):
		return

	for n, f in enumerate(get_files_to_analyse(csvdir)):
		raw_data = load_data(f, lag=lag)
		processed_data = (raw_data.pipe(normalize_coordinates, lag)
			.pipe(bin_and_calculate_coverage, bin_size)
			.pipe(score_coverage, threshold))
		line_lenght = raw_data[COLUMNS["COORDS"]].iloc[-1]-lag

		# Save subject counts on csv named with the orginal file name.
		try:
			processed_data.to_csv(savepath.joinpath(f"{f.name}_{SKIP_FLAGS[0]}.csv"))
		except PermissionError:
			std_out(f"You currently have no permission to save {f.name} table.",
			"Skipping...")

		if n == 0:
			score_total = pd.DataFrame.from_dict({COLUMNS["COORDS"]:processed_data[COLUMNS["COORDS"]],
				COLUMNS["SCORE"]:list((0 for _ in range(len(processed_data.index))))})
			lengths = pd.DataFrame.from_dict({"image":[f.stem,], "line_lenght":[line_lenght, ]})
		else:
			lengths.loc[n] = [f.stem, line_lenght]

		score_total[COLUMNS["SCORE"]] += processed_data[COLUMNS["SCORE"]].values
		score_total[f.name] = processed_data[COLUMNS["SCORE"]].values

	# Calculate the penetrance of each signal covered bins for the analysed group.
	score_total["penetrance"] = np.divide(score_total[COLUMNS["SCORE"]], n+1)

	# Save the summary dataframes to csv files on savepath.
	counts_savepath = savepath.joinpath(f"{SUMMARY_TITLE}.csv")
	lengths_savepath = savepath.joinpath(f"{LENGTHS_TITLE}.csv")
	score_total.to_csv(counts_savepath)
	lengths.to_csv(lengths_savepath)
	save_parameters_txt(savepath, bin_size, threshold, lag=lag)

	return (score_total, lengths)

def get_files_to_analyse(csvdir: pathlib.Path)->Generator[pathlib.Path, None, None]:
	return (f for f in csvdir.glob("*.csv")
	if not any([flag.lower() in f.name.lower() for flag in SKIP_FLAGS]))

def check_and_setup_dirs(csvdir: pathlib.Path, savepath: pathlib.Path, std_out=print)->bool:
	'''
	Checks if csvdir is a valid dir and tries to create the savepath if it does not exists.
	Returns True upon success and False otherwise.
	'''

	result = True
	if not csvdir.is_dir():
		std_out("Could not find csv directory or path is not a folder.")
		result =  False
	elif not savepath.exists():
		try:
			savepath.mkdir()
		except PermissionError:
			std_out("You don't have the permission to create this folder.\nPlease select another one.")
			result =  False

	return result

def save_parameters_txt(savepath:pathlib.Path,
	bin_size: float,
	threshold: float,
	lag:int =0,
	std_out=print)->pathlib.Path:
	'''
	Saves the parameters used in a txt file.
	The resulting txt file can be used as a config file.
	Returns the path to the saved file.
	'''
	now = date.today()
	info = f"[Parameters - {now} run]\n\nbin_size = {bin_size}\nthreshold = {threshold}\nlag = {lag}"
	params_path = savepath.joinpath(f"{now} Analysis parameter.txt")
	try:
		with open(params_path, "w") as params_file:
			params_file.write(info)
	except PermissionError as pe:
		std_out(pe.args[0])
	except FileNotFoundError:
		std_out(f"Could not find {params_path}.")
	else:
		return params_path

def check_bitdepth(line_scan_df:pd.DataFrame)->int:
	'''
	Tests the bit depth of the measures recorded in the data frame.
	Basically, if values are between 0,255 will test as 8bit.
	If any value is higher than 255 will test as 16bit.
	Other bitdepths have not been implemented.
	Returns the bitdepth as an int (either 8 or 16).
	'''
	if any([signal > 255 for signal in line_scan_df["Y"]]):
		bitdepth = 16
	else:
		bitdepth = 8
	return bitdepth

def get_max_grayvalue(bitdepth:int)->int:
	'''
	Returns the maximum possible value acording to
	the bitdepth.
	Precomputed values based on ImageJ1 ImagePlus images.
	'''
	if bitdepth == 8:
		return 255
	elif bitdepth == 16:
		return 65535

def load_summary(csv:pathlib.Path)->pd.DataFrame:
	try:
		return pd.read_csv(
		csv,
		header=0,)

	except ValueError:
		raise SyntaxError("Bad csv syntax. Expecting ',' as delimiters.")

def score_coverage(binned_line_scan_df: pd.DataFrame, threshold)->pd.DataFrame:
	df = binned_line_scan_df.copy()
	df["Score"] = [1 if bucket > threshold else 0 for bucket in df["Coverage"]]
	return df

def normalize_coordinates(line_scan_df: pd.DataFrame, lag:int=0)->pd.DataFrame:
	df = line_scan_df.copy()
	max_value = df[COLUMNS["COORDS"]].iloc[-1]-lag
	df[COLUMNS["COORDS"]] = df[COLUMNS["COORDS"]].divide(max_value)
	return df