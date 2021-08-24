from settings import get_setting

# TODO: put/call debit spreads

def credit_spreads(price, type, opts, best_only=True):
	"""Calculates return for two contract credit spreads
	Returns [short strike, long strike, short premium, long premium, credit, percent return, odds, % from price]
	"""
	spreads = []
	best_round = []
	type = type.lower()
	end = len(opts)
	for (short, opt) in enumerate(opts):
		if (opt[3] > get_setting("FILTER_PROBABILITY") and ((type == "call" and opt[0] > price) or (type == "put" and opt[0] < price))):
			# Try all spreads
			low = 0 if type == "put" else short+1
			high = short if type == "put" else end
			for long in range(low, high):
				collateral = abs(opt[0] - opts[long][0])
				test_put = [ opt[0], opts[long][0], opt[1], opts[long][2], opt[1] - opts[long][2], (opt[1] - opts[long][2]) / collateral, min(opt[3], opts[long][3]), abs(price - opt[0]) / price ]
				if (test_put[5] > get_setting("MIN_OPTION_RETURN")):
					if (best_only):
						if ((not best_round or test_put[5] > best_round[5]) and collateral <= get_setting("MAX_SPREAD_COLLATERAL") / 100):
							best_round = test_put.copy()
					else:
						spreads.append(test_put)
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
			filtered.append([put[0], put[1], put[2], put[1]/put[0] * 100, put[3], (put[0] - price) / price, put[0] - put[1]]) # TODO: Filter based on % return above threshhold and distance from price?
	elif type == "call":
		for call in options:
			filtered.append([call[0], call[1], call[2], call[1]/price * 100, call[3], (call[0] - price) / price, (call[0] - price + call[1]) / price]) # TODO: Filter based on % return if called > 0 and % return above threshhold
	else:
		print("Unknown type %s" % type)
	return filtered
	