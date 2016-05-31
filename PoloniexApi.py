#!/usr/bin python3
# -*- coding: utf-8 -*-
#
# PoloniexAPI : Poloniex API written in Python3
# 
# Copyright © 2016 Chiheb Nexus
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
##########################################################################################
#!/usr/bin python3

from urllib import request
from urllib.parse import urlencode
from json import loads
import hmac, hashlib, time

class PoloniexApi():
	"""
	Wrapper for Poloinex 
	"""
	def __init__(self, APIKey, Secret):
		"""
		Initialize APIKey & Secret key

		Warning: buy, sell, cancel, withdraw, return_open_orders, return_trade_history methods are for Advanced users
		"""
		self.APIKey = APIKey
		self.Secret = Secret.encode() # Must be a byte

	def return_pairs(self):
		"""
		Return Poloniex pairs
		"""
		pairs = request.urlopen('https://poloniex.com/public?command=returnTicker').read()

		return loads(pairs.decode("UTF-8")).keys()

	def return_coins_symbols(self):
		"""
		Return coins symbols supported by Poloniex
		"""
		output = request.urlopen('https://poloniex.com/public?command=returnCurrencies').read()
		symbols = loads(output.decode("UTF-8")).keys()

		return symbols

	def return_currencies_info(self, coin_symbol):
		"""
		Return currencies and their informations
		"""
		output = request.urlopen('https://poloniex.com/public?command=returnCurrencies').read()
		coins = loads(output.decode("UTF-8"))
		info = coins[coin_symbol]
		coin_info = [info["name"], info["txFee"], info["minConf"], info["frozen"], info["disabled"], info["delisted"]]

		return coin_info

	def api_query(self, command, req = {}):
		"""
		Main program
		"""
		if(command == "returnTicker" or command == "return24hVolume"):
			output = request.urlopen('https://poloniex.com/public?command=' + command).read()

			return loads(output.decode("UTF-8"))

		elif(command == "returnOrderBook"):
			output = request.urlopen('http://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])).read()

			return loads(output.decode("UTF-8"))

		elif(command == "returnMarketTradeHistory"):
			output = request.urlopen('http://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])).read()
			
			return loads(output.decode("UTF-8"))

		else:
			req['command'] = command
			req['nonce'] = int(time.time() * 1000)
			post_data = urlencode(req).encode("UTF-8")

			sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
			headers = {'Sign': sign, 'Key': self.APIKey}

			send_data = request.Request('https://poloniex.com/tradingApi', post_data, headers)
			output = request.urlopen(send_data).read()

			return loads(output.decode("UTF-8"))

	def return_ticker(self, currencyPair):
		"""
		Return currency pair ticker or all the currencies ticker
		"""
		if currencyPair == "all":

			return self.api_query('returnTicker')

		else:

			return self.api_query('returnTicker')[currencyPair]

	def return_24h_volume(self, currencyPair):
		"""
		Return currency pair 24h volume or return 24h volume of all currencies
		"""
		if currencyPair == "all":

			return self.api_query('return24hVolume')

		else:

			return self.api_query('return24hVolume')[currencyPair]

	def return_order_book(self, currencyPair):
		"""
		Return Order book of the current currency pair
		"""
		return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

	def return_balances(self, coin):
		"""
		Return balance of the coin or all coins
		"""
		if coin == "all":

			return self.api_query('returnBalances')

		else:

			return self.api_query('returnBalances')[coin]

	def return_open_orders(self, currencyPair):
		"""
		Return currency pair open orders 
		"""
		return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})

	def return_trade_history(self, currencyPair):
		"""
		Return trade history of the current currency pair
		"""
		return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})

	def buy(self, currencyPair, rate, amount):
		"""
		Instant buy 
		"""
		return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

	def sell(self, currencyPair, rate, amount):
		"""
		Instant sell
		"""
		return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

	def cancel(self, currencyPair, orderNumber):
		"""
		Instant cancel
		"""
		return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

	def withdraw(self, currency, amount, address):
		"""
		Instant withdraw
		"""
		return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})



