from csv import reader, writer
from os import path, makedirs

def str_to_bool(str):
	if str.lower() in 'true':
		return True
	return False

_settings = {
	"DATA_STALE_TIMEOUT" : [5, int, "Data is only valid and cached for this many minutes"],
	"SLOGIN" : ["", str, "Authentication cookie for stockoptionschannel.com"],
	"MIN_OPTION_RETURN" : [0.03, float, "Minimum percent return for options and option spreads"],
	"FILTER_PROBABILITY" : [79, int, "Minimum percent of expiring worthless for option spreads to be considered"],
	"MIN_TIME_DIFFERENCE" : [1, int, "Options spreads must have this many days before expiration to be considered"],
	"MIN_DIVIDEND_RETURN" : [0.01, float, "Minimum percent return for dividend plays to be considered"],
	"MAX_DIV_SHARE_PRICE" : [100, int, "Maximum share price for dividend plays to be considered"],
	"PRINT_ALL" : [False, str_to_bool, "Print all spreads, not just the best at each price point"],
	"DEBUG" : [False, str_to_bool, "Print copious debugging messages"],
	"MAX_CALENDAR_MONTHS" : [5, int, "Maximum number of contracts (not necessarily months) to consider for calendar spreads"],
	}



def read_settings(file):
	# Load symbols of interest
	if path.exists(file):
		r = reader(open(file, "r", newline=''))
		for row in r:
			if row[0] in _settings.keys():
				_settings[row[0]][0] = _settings[row[0]][1](row[1])

def get_setting(setting):
	setting = setting.upper()
	if setting in _settings.keys():
		return _settings[setting][0]
	else:
		print("Setting not present")
		
def set_setting(setting, value):
	setting = setting.upper()
	if setting in _settings.keys():
		if _settings[setting][1] == bool and (value.lower() in 'false'):
			value = ""
		_settings[setting][0] = _settings[setting][1](value)
		print("%s: %s" % (setting, str(_settings[setting][0])))
	else:
		print("Setting not present")
		
def is_setting(setting):
	return setting.upper() in _settings.keys()
	
def print_settings():
	for setting, val in _settings.items():
		print("%s: %s    %s" % (setting, str(val[0]), val[2]))
		
def save_settings(file):
	# Store to dictionary on disk
	w = writer(open(file, "w", newline=''))
	for setting, val in _settings.items():
		w.writerow([setting, val[0]])
	