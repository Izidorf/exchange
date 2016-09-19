from scipy.stats import burr
from scipy import stats
import scipy
import matplotlib.pyplot as plt
import numpy as np
import read_json as rj
import collections


with np.errstate(divide='ignore'):
	np.float64(1.0) / 0.0

def fitting(y, dist_name,par):
	dist = getattr(scipy.stats, dist_name)
	param = dist.fit(y)
	y_fitted = dist.rvs(*param[:-2], loc=param[-2], scale=param[-1], size=len(y))

	# Plot Histogram
	plt.hist(y, color='blue',normed=True, histtype='stepfilled', alpha=0.2, label='original data')
	plt.hist(y_fitted, color='red',normed=True, histtype='stepfilled', alpha=0.2, label='fitted data')
	plt.title('Match - '+dist_name)
	plt.xlabel('probabilty')
	plt.ylabel('time s')
	plt.savefig('distributions/hist_'+dist_name+'_'+par)
	plt.close()

	# Probability plot
	stats.probplot(y, sparams=param, dist=dist, plot=plt)
	plt.title('Probability plot - ' + dist_name+'_'+par)
	plt.savefig('distributions/prob_'+dist_name+'_'+par)
	plt.close()

	# Test P-Value
	vals = stats.ks_2samp(y, y_fitted)

	print dist_name, " - ", vals
	f = lambda y : dist.rvs(*param[:-2], loc=param[-2], scale=param[-1], size=y)

	return {"pval" : vals, "lambda" : f}



def plot_dis(samp, name, par):
	plt.hist(samp, bins=100, color='grey');
	plt.title('Frequency - '+name)
	plt.xlabel('Price USD')
	plt.ylabel('Frequency')
	plt.savefig('distributions/_hist'+name+'__'+par)
	plt.close()



N=1000
shape_c = 10.5
shape_d = 4.3
bur_mu = 0.1
bur_sigma = 2

buy_time, buy_size, buy_price, sell_time, sell_size, sell_price, buy_c_time, buy_c_size, buy_c_price, sell_c_time, sell_c_size, sell_c_price, trade_b_time, trade_s_time, trade_s_volume, trade_b_volume, trade_b_price, trade_s_price = rj.load_json('log14.txt')
print "**********************\n************************\n***********************"
print trade_b_time,"     "#,trade_s_time


def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

data_price = collections.OrderedDict([ ('bid_price' ,  buy_price), ('bid_c_price', buy_c_price), ('ask_price', sell_price), ('ask_c_price', sell_c_price), ('market_buy_price', trade_b_price)])#,'market_sell' : trade_s_time} }
data_size = collections.OrderedDict([  ('bid_size'  , buy_size), ('bid_c_size', buy_c_size), ('ask_size', sell_size), ('ask_c_size', sell_c_size), ('market_buy_size', trade_b_volume)])#,'market_sell' : trade_s_time} }
data_time = collections.OrderedDict( [ ('bid_time'  , buy_time), ('bid_c_time', buy_c_time), ('ask_time', sell_time), ('ask_c_time', sell_c_time), ('market_buy_time', trade_b_time)])#,'market_sell' : trade_s_time} }
datas = merge_dicts(data_price, data_size, data_time)

dist_names = ['expon']#, 'gamma', 'beta', 'rayleigh', 'norm', 'pareto', 'burr', 'expon', 'rice']

mainResult = collections.OrderedDict()
data = sell_c_time
#
for k,data in datas.items():
	param_results = []
	mainResult[k]=collections.OrderedDict()
	for dist in dist_names:
		single_result = fitting(data, dist,k)
		single_result["dis"]=dist
		param_results.append(single_result)
		plot_dis(data, dist,k)

	mainResult[k] = param_results

#
# RETURN ONLY BEST FITTING FUNCTIONS IN DICTIONARY
# dict { 'event_type' : { "size" : func1, "price" : func2, "price3" : func3 } }
#
print mainResult
