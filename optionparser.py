from settings import get_setting

# TODO: put/call debit spreads

def put_credit_spreads(price, puts, best_only=True):
	"""Calculates return for two contract put credit spreads
	Returns [short strike, long strike, short premium, long premium, credit, percent return, odds, % from price]
	"""
	spreads = []
	best_round = []
	for (short, put) in enumerate(puts):
		if (put[3] > get_setting("FILTER_PROBABILITY") and put[0] < price):
			# Try all spreads up to the short
			for long in range(0, short):
				test_put = [ put[0], puts[long][0], put[1], puts[long][2], put[1] - puts[long][2], (put[1] - puts[long][2]) / (put[0] - puts[long][0]), min(put[3], puts[long][3]), (price - put[0]) / price ]
				if (test_put[5] > get_setting("MIN_OPTION_RETURN")):
					if (best_only):
						if (not best_round or test_put[5] > best_round[5]):
							best_round = test_put.copy()
					else:
						spreads.append(test_put)
			if (best_only and best_round):
				spreads.append(best_round)
				best_round = []
	return spreads
	
def call_credit_spreads(price, calls, best_only=True):
	"""Calculates return for two contract call credit spreads
	Returns [short strike, long strike, short premium, long premium, credit, percent return, odds, % from price]
	"""
	spreads = []
	best_round = []
	end = len(calls)
	for (short, call) in enumerate(calls):
		if (call[3] > get_setting("FILTER_PROBABILITY") and call[0] > price):
			# Try all calls worth more than the short
			for long in range(short+1, end):
				test_call  = [ call[0], calls[long][0], call[1], calls[long][2], call[1] - calls[long][2], (call[1] - calls[long][2]) / (calls[long][0] - call[0]), min(calls[long][3], call[3]), (call[0] - price) / price ]
				if (test_call[5] > get_setting("MIN_OPTION_RETURN")):
					if (best_only):
						if (not best_round or test_call[5] > best_round[5]):
							best_round = test_call.copy()
					else:
						spreads.append(test_call)
			if (best_only and best_round):
				spreads.append(best_round)
				best_round = []
	return spreads
	
def filter_options(type, price, options):
	"""Filter bare options based on settings
	Returns [strike, bid, ask, percent return, odds, % from price, return if called/cost basis if put]
	"""
	filtered = []
	type = type.lower()
	if type == "put":
		for put in options:
			#if (put[3] > get_setting("FILTER_PROBABILITY") and put[0] < price):
			filtered.append([put[0], put[1], put[2], put[1]/put[0] * 100, put[3], (put[0] - price) / price, put[0] - put[1]])
	elif type == "call":
		for call in options:
			filtered.append([call[0], call[1], call[2], call[1]/price * 100, call[3], (call[0] - price) / price, (call[0] - price + call[1]) / price])
	else:
		print("Unknown type %s" % type)
	return filtered
	