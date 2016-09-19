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

from LOBHistory import *
from ExchangeEvents import *

def _url_request(url):
	url = url
	response = urllib.urlopen(url)
	return json.loads(response.read())

def get_orderbook():
	data = _url_request( "https://www.bitstamp.net/api/order_book/" )
	return data

class OrderBook:
	"""docstring for """
	def __init__(self):
		self.askOrders = {}
		self.bidOrders = {}

	def loadLimitOrderBookData(self):
		data = get_orderbook()
		for price,amount in data['asks']:
			self.ask(float(price), float(amount))

		for price,amount in data['bids']:
			self.bid(float(price), float(amount))

	def bid(self, price, amount):
		if price in self.bidOrders:
			self.bidOrders[price] += amount
		else:
			self.bidOrders[price] = amount

	def getBestBid(self):
		return max(self.bidOrders.keys(), key=float)

	def getBestAsk(self):
		return min(self.askOrders.keys(), key=float)

	def ask(self, price, amount):
		if price in self.askOrders:
			self.askOrders[price] += amount
		else:
			self.askOrders[price] = amount

	def cancelBid(self, price, amount):
		if price in self.bidOrders:
			self.bidOrders[price] -= amount
		else:
			idx = min(self.bidOrders.keys(), key=lambda k: abs(k-price))
			if  self.bidOrders[idx] < amount:
				self.bidOrders[idx]=0
			else:
				self.bidOrders[idx]-=amount

	def cancelAsk(self, price, amount):
		if price in self.askOrders:
			self.askOrders[price] -= amount
		else:
			idx = min(self.askOrders.keys(), key=lambda k: abs(k-price))
			if  self.askOrders[idx] < amount:
				self.askOrders[idx]=0
			else:
				self.askOrders[idx]-=amount

	def showOrderBook(self, name):
		plt.figure(1)
		volumeA = []
		priceA = []
		volumeB = []
		priceB = []
		for price,volume in self.askOrders.iteritems():
			v = float(volume)
			p = float(price)
			if( v < 1000 and p < 1000):
				volumeA.append(v)
				priceA.append(p)

		for price,volume in self.bidOrders.iteritems():
			v = float(volume)
			p = float(price)
			if( v < 1000 and p < 1000):
				volumeB.append(v)
				priceB.append(p)
		plt.figure(1)

		volumeA = np.array(volumeA)
		priceA = np.array(	priceA)
		volumeB = np.array(volumeB)
		priceB = np.array(	priceB)
		indA = priceA.argsort()[:60]
		indB = np.argpartition(priceB, -60)[-60:]
		volumeA = volumeA[indA]
		priceA = 	priceA[indA]
		volumeB = volumeB[indB]
		priceB = 	priceB[indB]
		# print priceB, volumeB

		b = self.getBestBid()
		a = self.getBestAsk()
		plt.hist(priceA, weights=volumeA, bins=40, range=(a-1,a+4),color='white')
		plt.hist(priceB, weights=volumeB, bins=40, range=(b-4,b+1),color='grey')
		plt.title('Limit Order Book' + name)
		plt.xlabel('Price')
		plt.ylabel('Volume')
		plt.savefig('distributions/'+str(time.time())+name+'.png')
		plt.cla()
		# plt.show()

	def sortAsks(self):
		return sorted(self.askOrders.items(), key=operator.itemgetter(0))

	def sortBids(self):
		result = sorted(self.bidOrders.items(), key=operator.itemgetter(0))
		result.reverse()
		return result

	def printTop10Aks(self):
		print "*****************************************"
		print "				Top 10 Asks					"
		sorted_x = sorted(self.askOrders.items(), key=operator.itemgetter(0))
		for key,value in sorted_x[0:10]:
			print key, value
		print "*****************************************"

	def printTop10Bids(self):
		print "*****************************************"
		print "				Top 10 Bids					"
		sorted_x = sorted(self.bidOrders.items(), key=operator.itemgetter(0))
		sorted_x.reverse()
		for key,value in sorted_x[0:10]:
			print key, value
		print "*****************************************"


def setup(env, oBook):
	#Create different orders while simulation is running
	env.process(LOBHistory(env, oBook, "Logging").log())
	env.process(LimitBid(env, oBook, "Limit Bid").simulate())
	env.process(LimitAsk(env, oBook, "Limit Ask").simulate())
	env.process(CancelBid(env, oBook, "Cancel Bid").simulate())
	env.process(CancelAsk(env, oBook, "Cancel Ask").simulate())
	env.process(MarketBuy(env, oBook, "Market Buy").simulate())
	env.process(MarketSell(env, oBook, "Market Sell").simulate())
