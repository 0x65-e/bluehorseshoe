from HTMLTableParser import HTMLTableParser
import js2py
import requests
import re
from settings import get_setting
from decimal import Decimal
from datetime import datetime
from pprint import pprint

class Document(object):

    def __init__(self):
        self.value = ''

    def write(self, *args):
        self.value += ''.join(str(i) for i in args)
		

_dividend_cache = tuple()

# Necessary variables for JS evaluation
variables = """var TTI_fontFace        = 'Arial';      // The font face to use in the table
var TTI_fontSize        = '2';          // The font size to use in data rows 
var TTI_fontColor       = '#222222';    // The font color to use in data rows
var TTI_boldTarget      = 6;            // The target threshold to make the row bold
var TTI_trColor1        = "#F9F9F9";    // Background color for alternating rows
var TTI_trColor2        = "#FFFFFF";    // Background color for alternating rows
var TTI_thColor         = "#DEDEDE";    // Background color for column headers
var TTI_thFontColor     = "#222222";    // Font color for column headers
var TTI_thFontSize      = "2";          // Font size for column headers
var TTI_colname1        = "Ticker";     // Name for table column 1
var TTI_colname2        = "Name";       // Name for table column 2
var TTI_colname3        = "Div. Amt.";  // Name for table column 3
var TTI_colname4        = "Yield";      // Name for table column 4
var TTI_colname5        = "Ex-date";    // Name for table column 5
var TTI_colname6        = "Pay date";   // Name for table column 6
var TTI_tableWidth      = "100%";       // Width for table
var TTI_cellSpacing     = "0";          // Cellspacing for table
var TTI_cellPadding     = "2";          // Cellpadding for table
var TTI_border          = "0";          // Border for table"""

def get_dividends():
	"""
	Gets tickers with dividends that end trading today (i.e. ex-dividend date tomorrow)
	Return value is a sorted (high->low by percent) of [symbol, name, type: {Q/M/A/S}, dividend, current price, return, ex-date (datetime), payment date (string)]
	"""
	global _dividend_cache
	if _dividend_cache and (datetime.now() - _dividend_cache[0]).total_seconds() / 60 < get_setting("DATA_STALE_TIMEOUT"):
		return _dividend_cache[1]
	
	target = "https://secure.tickertech.com/bnkinvest/custom.js"

	document = Document()

	# Request
	response = requests.get(target)
	js = response.text
	location = ""

	context = js2py.EvalJs({'document': document, 'location' : ""})

	# Strip out links to symbols and replace with a table row containing the symbol
	js = re.sub(r'<a href="/symbol/([a-z.]*)">', r'\1</td><td>', js)
	js.replace(r'</a>', '')

	# Parse and execute the function
	context.execute(variables + js)
	context.TTI_showDividendTable()

	# Decode
	parser = HTMLTableParser()
	parser.feed(context.document.value)

	# Modify list
	entries = parser.tables[0][1:-2]
	dividends = []

	for entry in entries:
		entry[0] = entry[0].upper()
		entry[3] = Decimal(entry[3])
		entry[4] = Decimal(entry[4])
		entry[5] = entry[3]/entry[4]
		entry[6] = datetime.strptime(entry[6], "%m/%d").replace(year=datetime.now().year)
		
		if (entry[6] > datetime.now()) and entry[5] > get_setting("MIN_DIVIDEND_RETURN") and entry[4] < get_setting("MAX_DIV_SHARE_PRICE"):
			dividends.append(entry)

	dividends.sort(key=lambda x: x[5], reverse=True)
	
	_dividend_cache = (datetime.now(), dividends)

	return dividends
