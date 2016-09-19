from LOB import *

# Get current state of the orderbook
oBook = OrderBook()

oBook.loadLimitOrderBookData()
oBook.showOrderBook(' - Start')
# oBook.printTop10Bids()
# oBook.printTop10Aks()

# Initialise environment
env = simpy.Environment()
setup(env, oBook)

# Execute!
env.run(until=10)
# oBook.printTop10Bids()

oBook.showOrderBook(' - Simulation')
#
time.sleep(10)
oBook2 = OrderBook()
oBook2.loadLimitOrderBookData()
oBook2.showOrderBook(' - Real')
