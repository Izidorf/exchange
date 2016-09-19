import simpy
import random

import urllib, json
import time
import json
import time


import operator
from scipy import stats
import matplotlib.pyplot as plt
# import pylab as P
import numpy as np
from scipy.stats import lognorm, gamma, beta, norm

from config import *

class ExchangeEvent:
	""" Market event """
	def __init__(self, env, orderBook, name):
		self.env = env
		self.orderBook = orderBook
		self.name = name

	def simulate(self):
		while True:
			time = self.calculateExchangeEventTime()

			yield self.env.timeout(abs(time))
			print('%s event at time=%f,' % (self.name, self.env.now))

			self.performExchangeEvent()

class LimitAsk(ExchangeEvent):
	"""docstring for """
	def __init__(self, env, orderBook, name):
		ExchangeEvent.__init__(self, env, orderBook, name)

	def performExchangeEvent(self):
		price = self.calculatePrice()
		volume = self.calculateVolume()
		self.orderBook.ask(price, volume)

	def calculateExchangeEventTime(self):
		return lognorm.rvs(LIMIT_ASK_TIME_shape, loc=LIMIT_ASK_TIME_mu, scale=LIMIT_ASK_TIME_sigma, size=1)

	def calculateVolume(self):
		return  lognorm.rvs(LIMIT_ASK_SIZE_shape, loc=LIMIT_ASK_SIZE_mu, scale=LIMIT_ASK_SIZE_sigma, size=1)

	def calculatePrice(self):
		bBid = self.orderBook.getBestBid()
		return bBid+gamma.rvs(LIMIT_ASK_shape, loc=LIMIT_ASK_mu, scale=LIMIT_ASK_sigma, size=1)[0]


class LimitBid(ExchangeEvent):
	"""docstring for """
	def __init__(self, env, orderBook, name):
		ExchangeEvent.__init__(self, env, orderBook, name)

	def performExchangeEvent(self):
		price = self.calculatePrice()
		volume = self.calculateVolume()
		self.orderBook.bid(price, volume)

	def calculateExchangeEventTime(self):
		return lognorm.rvs(LIMIT_BID_TIME_shape, loc=LIMIT_BID_TIME_mu, scale=LIMIT_BID_TIME_sigma, size=1) #random.random()

	def calculateVolume(self):
		return lognorm.rvs(CANCEL_BID_SIZE_shape, loc=CANCEL_BID_SIZE_mu, scale=CANCEL_BID_SIZE_sigma, size=1)

	def calculatePrice(self):
		bAsk = self.orderBook.getBestAsk()
		return bAsk-gamma.rvs(LIMIT_BID_shape, loc=LIMIT_BID_mu, scale=LIMIT_BID_sigma, size=1)[0]



class CancelBid(ExchangeEvent):
	"""docstring for """
	def __init__(self, env, orderBook, name):
		ExchangeEvent.__init__(self, env, orderBook, name)

	def performExchangeEvent(self):
		# Perform cancelation
		price = self.calculatePrice() # distribution
		volume = self.calculateVolume() # distribution
		self.orderBook.cancelBid(price, volume)

	def calculatePrice(self):
		bAsk = self.orderBook.getBestAsk()
		return bAsk-gamma.rvs(CANCEL_BID_PRICE_shape, loc=CANCEL_BID_PRICE_mu, scale=CANCEL_BID_PRICE_sigma, size=1)[0]

	def calculateVolume(self):
		return lognorm.rvs(CANCEL_BID_SIZE_shape, loc=CANCEL_BID_SIZE_mu, scale=CANCEL_BID_SIZE_sigma, size=1)

	def calculateExchangeEventTime(self):
		return lognorm.rvs(CANCEL_BID_TIME_shape, loc=CANCEL_BID_TIME_mu, scale=CANCEL_BID_TIME_sigma, size=1)

class CancelAsk(ExchangeEvent):
	"""docstring for """
	def __init__(self, env, orderBook, name):
		ExchangeEvent.__init__(self, env, orderBook, name)

	def performExchangeEvent(self):
		bBid = self.orderBook.getBestBid()
		price = bBid+gamma.rvs(LIMIT_ASK_shape, loc=LIMIT_ASK_mu, scale=LIMIT_ASK_sigma, size=1)[0]
		volume = lognorm.rvs(CANCEL_ASK_SIZE_shape, loc=CANCEL_ASK_SIZE_mu, scale=CANCEL_ASK_SIZE_sigma, size=1) # distribution
		self.orderBook.cancelAsk(price, volume)

	def calculateExchangeEventTime(self):
		return lognorm.rvs(CANCEL_ASK_TIME_shape, loc=CANCEL_ASK_TIME_mu, scale=CANCEL_ASK_TIME_sigma, size=1)

class MarketBuy(ExchangeEvent):
	"""docstring for """
	def __init__(self, env, orderBook, name):
		ExchangeEvent.__init__(self, env, orderBook, name)


	def performExchangeEvent(self):
		quantity = beta.rvs(MARKET_BUY_PRICE_shape,MARKET_BUY_PRICE_shape2, loc=MARKET_BUY_PRICE_mu, scale=MARKET_BUY_PRICE_sigma, size=1)
		best_asks = self.orderBook.sortAsks()
		i = 0
		while quantity > 0 and i < len(best_asks):
			best_ask = best_asks[i][0]
			best_volume = best_asks[i][1]
			if quantity < best_volume:
				self.orderBook.cancelAsk(best_ask, quantity)
				quantity=0
			else:
				available = self.orderBook.askOrders[best_ask]
				quantity = quantity - available
				self.orderBook.askOrders.pop(best_ask, None)
			i = i + 1

	def calculateExchangeEventTime(self):
		return lognorm.rvs(MARKET_BUY_TIME_shape, loc=MARKET_BUY_TIME_mu, scale=MARKET_BUY_TIME_sigma, size=1)

class MarketSell(ExchangeEvent):
	"""docstring for """
	def __init__(self, env, orderBook, name):
		ExchangeEvent.__init__(self, env, orderBook, name)


	def performExchangeEvent(self):
		quantity = beta.rvs(MARKET_SELL_PRICE_shape,MARKET_SELL_PRICE_shape2, loc=MARKET_SELL_PRICE_mu, scale=MARKET_SELL_PRICE_sigma, size=1)
		best_bids = self.orderBook.sortBids()
		i = 0
		while quantity > 0 and i < len(best_bids):
			best_ask = best_bids[i][0]
			best_volume = best_bids[i][1]
			if quantity < best_volume:
				self.orderBook.cancelBid(best_ask, quantity)
				quantity=0
			else:
				available = self.orderBook.bidOrders[best_ask]
				quantity = quantity - available
				self.orderBook.bidOrders.pop(best_ask, None)
			i = i + 1

	def calculateExchangeEventTime(self):
		return lognorm.rvs(MARKET_SELL_TIME_shape, loc=MARKET_SELL_TIME_mu, scale=MARKET_SELL_TIME_sigma, size=1)
