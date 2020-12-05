from HTMLTableParser import HTMLTableParser
import requests
import datetime
from settings import get_setting
from decimal import Decimal

_ts_data_cache = dict() # Contains a tuple of (timestamp, header, contracts)

urlmask = "https://www.stockoptionschannel.com/symbol/?symbol=%s&month=%s&type=%s"

def get_contracts(symbol, month, type):
	"""Gets the contracts for a symbol at a particular month of one type (call or put).
	Returns (price, [contracts]) where each contract is [strike, bid, ask, odds]
	"""
	target = urlmask % (symbol.strip("$"), month, type)
	if(get_setting("DEBUG")): print(target)
		
	key = "%s-%s-%s" % (symbol, month, type)
	if key in _ts_data_cache and (datetime.datetime.now() - _ts_data_cache[key][0]).total_seconds() / 60 < get_setting("DATA_STALE_TIMEOUT"):
		header = _ts_data_cache[key][1]
		print(header)
		price = Decimal(header[header.find("Last:")+6:header.find(" , ")])
		return (price, _ts_data_cache[key][2])
	
	# Request
	response = requests.get(target, cookies={'slogin' : get_setting("SLOGIN")})
	xhtml = response.text

	# Decode
	parser = HTMLTableParser()
	parser.feed(xhtml)
	
	# TODO: Check if no options available (raise exception or print error, schedule contract reload)

	# Modify list - [strike, bid, ask, odds]
	tables = parser.tables[6:-5]
	contracts = [ [ Decimal(tables[i-1][1][0].split(" ")[0]), Decimal(tables[i-1][1][1]), Decimal(tables[i][0][1]), int(tables[i][0][5][:-1]) ] for i in range(1, len(tables)) ]
	
	# Grab header with price and change
	header = tables[0][0][2].split("\n")[-1]
	start_index = header.find("(")
	end_index = header.find(",  V")
	header = header[start_index:end_index]
	print(header)
	
	# Grab price
	price = Decimal(header[header.find("Last:")+6:header.find(" , ")])
	
	_ts_data_cache[key] = (datetime.datetime.now(), header, contracts)
	
	return (price, contracts)
	

def update_months(symbol, symbol_month):
	"""Gets the available contract months for symbol and stores it as string:list pair in symbol_month"""
	target = "https://www.stockoptionschannel.com/symbol/?symbol=%s" % (symbol.strip("$"))
					
	# Request
	response = requests.get(target, cookies={'slogin' : get_setting("SLOGIN")})
	xhtml = response.text

	# Decode
	parser = HTMLTableParser()
	parser.feed(xhtml)

	# Modify list
	entries = parser.tables[7][1:]
	dates = [ datetime.datetime.strptime(entry[0], "%B %d, %Y").strftime("%Y%m%d") for entry in entries ]
	
	symbol_month[symbol] = dates