from sys import platform

__APP_NAME__ = ".IBP_linescan_bin_coverage"
__version__ = "0.2"
PIXEL_SCALING = 0.099 # microns/px
SKIP_FLAGS = ("processed", "done")
SUMMARY_TITLE = "Counts summary"
LENGTHS_TITLE = "ROI lengths"

if platform == "darwin":
	FILES_BROWSER_COMMAND = ["open", "--"]
elif platform == "linux2":
	FILES_BROWSER_COMMAND = ["xdg-open", "--"]
elif platform == "win32":
	FILES_BROWSER_COMMAND = ["explorer", "/select,"]
