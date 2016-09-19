import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import pandas as pd



def JSONStream(fd, buffer_size=4096, decode=None):
	'''
	Decodes distinct JSON objects from a stream (a file-like object)
	Returns a generator that yields sequential JSON objects as they are retreived from the stream
	:param fd: A file-like object representing the input stream
	:param buffer_size: Optional read buffer size
	:param decode: An optional custom JSON decode function
	'''

	if not decode:
		import json
		decode = json.JSONDecoder().raw_decode
	buf = ''
	data = fd.read(buffer_size)
	while data:
		try:
			if not buf: data = data.lstrip()
			buf, data = buf+data, None
			while buf:
				obj, i= decode(buf)
				buf = buf[i:].lstrip()
				yield(obj)
		except GeneratorExit: break
		except ValueError: pass
		if not fd.closed:
			data = fd.read(buffer_size)

def calc_time_difference(time):
	if(len(time) < 2):
		return 0

	t = time[0]
	for i in range(1, len(time)):
		time[i-1] = abs((time[i]-t)/1000.0)
		t = time[i]

	return time[:-1]

def load_json(filename):
	with open(filename, 'r') as fd:
		ob_state = {}
		# buy limit orders
		buy_time = []
		buy_size = []
		buy_price = []

		# sell limit orders
		sell_time = []
		sell_size = []
		sell_price = []

		# buy limit cancellations
		buy_c_time = []
		buy_c_size = []
		buy_c_price = []

		# sell limit cancelations
		sell_c_time = []
		sell_c_size = []
		sell_c_price = []

		# trades
		trade_b_time = []
		trade_b_volume = []
		trade_b_price = []

		trade_s_time = []
		trade_s_volume = []
		trade_s_price = []

		count = 0


		for o in JSONStream(fd):
			count = count + 1
			print count
			print o
			# for key, value in o.items():
			if 'asks' in o and 'bids' in o:
				ob_state=o
			if 'state' in o and 'localTimestamp' in o:
				value = o['state']
				best_ask = ob_state['asks'][0]['limitPrice']
				best_bid = ob_state['bids'][0]['limitPrice']
				time = o['localTimestamp']
				volume = o['orderInfo']['volume']
				price = o['orderInfo']['limitPrice']
				if value == 'CREATED':
					if o['direction'] == 'BUY' and best_bid-price < 5 and best_bid-price > -5:
						buy_time.append(time)
						buy_size.append(volume)
						buy_price.append(best_bid-price)
					elif o['direction'] == 'SELL' and best_ask-price < 5 and best_ask-price > -5:
						sell_time.append(time)
						sell_size.append(volume)
						sell_price.append(best_ask-price)
				elif value == 'DELETED' and best_bid-price < 5 and best_bid-price > -5:
					if o['direction'] == 'BUY' :
						buy_c_time.append(time)
						buy_c_size.append(volume)
						buy_c_price.append(best_bid-price)
					elif o['direction'] == 'SELL' and best_ask-price < 5 and best_ask-price > -5:
						sell_c_time.append(time)
						sell_c_size.append(volume)
						sell_c_price.append(best_ask-price)
				# elif value == 'UPDATED':
				# 	if o['direction'] == 'BUY' :
				# 		trade_b_time.append(time)
				# 		trade_b_volume.append(volume)
				# 		trade_b_price.append(price)
				# 	elif o['direction'] == 'SELL':
				# 		trade_s_time.append(time)
				# 		trade_s_volume.append(volume)
				# 		trade_s_price.append(price)
			if 'exchangeTradeId' in o:


				time = o['localTimestamp']
				volume = o['volume']
				price = o['price']
				best_bid = ob_state['bids'][0]['limitPrice']

				if price >= best_bid and best_bid-price <= 0 and best_bid-price > -5:
					trade_b_time.append(time)
					trade_b_volume.append(volume)
					trade_b_price.append(best_bid-price)
				elif best_ask-price <= 0 and best_ask-price > -5:
					trade_s_time.append(time)
					trade_s_volume.append(volume)
					trade_s_price.append(best_ask-price)







		sell_time = calc_time_difference(sell_time)
		sell_c_time = calc_time_difference(sell_c_time)
		buy_time = calc_time_difference(buy_time)
		buy_c_time = calc_time_difference(buy_c_time)
		trade_b_time = calc_time_difference(trade_b_time)
		trade_s_time = calc_time_difference(trade_s_time)

		# buy_size = map(lambda x: float(x)/1000000000.0, buy_size)
		# trade_size = map(lambda x: float(x)/1000000000.0, trade_size)
		# trade_b_volume = map(lambda x: float(x)/1000000000.0, trade_b_volume )
		# trade_s_volume = map(lambda x: float(x)/1000000000.0, trade_s_volume)
		#

		# print trade_b_time
		# print trade_s_t ime


		return buy_time, buy_size, buy_price, sell_time, sell_size, sell_price, buy_c_time, buy_c_size, buy_c_price, sell_c_time, sell_c_size, sell_c_price, trade_b_time,trade_s_time,trade_s_volume, trade_b_volume, trade_b_price, trade_s_price

# if __name__ == "__main__":
# 	buy_time = load_json('log2.txt')
# 	print buy_time

	# df.to_csv(path_or_buf ='test.csv')
