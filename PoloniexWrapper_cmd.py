#!/usr/bin python3
# -*- coding: utf-8 -*-
#
# PoloniexWrapper_cmd : Poloniex API with buy simulation v0.1
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

from PoloniexApi import *
import sys

class Wrapper():
	"""
	Poloniex wrapper v0.1
	"""
	def __init__(self):
		"""
		Initialize the wrapper
		"""
		# For advanced users
		# If you don't know what is APIKEY & Secret Key, keep them like that
		apiKey = 'PUT_YOUR_POLONIEX_API_KEY'
		secret = 'PUT_YOUR_POLONIEX_SECRET_KEY'
		self.API = PoloniexApi(apiKey, secret)
		self.supported_coins = self.getting_supported_coins()
		self.pairs = self.getting_pairs()
		answer = input("Do you want to see Poloniex supported pairs? [Y/N]: ")

		while True:
			
			if answer == 'Y' or answer == 'y':
				self.pretty_format_pairs(self.pairs)
				break

			if answer == 'N' or answer == 'n':
				break

			else:
				answer = input("Please enter a valid response [Y/N]: ")

		self.order_book = []


	def run(self):
		"""
		Main program
		"""
		pair = self.get_user_coin_pair()
		pair_input = pair.split("_")[0]
		pair_output = pair.split("_")[1]
		self.pretty_format_currency_ticker(pair)
		response = input("Do you want to show order book? [Y/N]: ")

		while True:
			
			if response == "Y" or response == "y":
				self.pretty_format_order_book(pair)
				self.order_book = self.getting_order_book(pair)
				break

			elif response == "N" or response == "n":
				self.order_book = self.getting_order_book(pair)
				break

			else:
				response = input("Please enter 'Y' or 'N': ")

		amount = input("Please enter your {0} deposit amount: ".format(pair_input))

		while True:
			try:
				if isinstance(float(amount), float):
					print("Looking for the lowest ASK price to get your {0}...".format(pair_output))
					print(" |-> Done")
					#print("The best price is: {0} {1} ".format(self.order_book["asks"][0][0], pair_input, self.order_book["asks"][0][1], pair_output))
					self.buying_limit(self.order_book, float(amount), pair_input, pair_output)
					break

				else:
					amount = input("Please enter a valid {0} amount".format(pair_input))

			except Exception as e:
				print("[x] Problem occured", e)
				break


	def buying_limit(self, order_book, amount, pair_input, pair_output):
		"""
		Find the first low price to exchange. 
		If user amount is higher than the total lowest ASK amount, then this script will look the other ASk amounts 
		untill the deposit amount will vanish. 
		"""
		i, j = 0, 0
		org_amount = amount
		coins_to_buy, price_total_to_buy = 0.0, 0.0
		buy_max = float(order_book["asks"][i][j+1]) * float(order_book["asks"][i][j])
		best_price = float(order_book["asks"][i][j])

		while True:
			
			if amount > buy_max:
				print("\tYou'll buy {0} {1} with this price {2} {3}".format(order_book["asks"][i][j+1], pair_output, order_book["asks"][i][j], pair_input))
				amount = amount - buy_max
				coins_to_buy += float(order_book["asks"][i][j+1])
				price_total_to_buy += float(order_book["asks"][i][j+1]) * float(order_book["asks"][i][j])

				i+= 1
				
			if i+1 > len(order_book["asks"]): # If i+1 len(order_book["asks"]) : index out of range!
				break

			else:
				buy_max = float(order_book["asks"][i][j+1]) * float(order_book["asks"][i][j])
				
			if amount <= buy_max and amount >0:
				
				print("\tYou'll buy %0.8f %s with this price %s %s" % (amount/ float(order_book["asks"][i][j]), pair_output, order_book["asks"][i][j], pair_input))
				#coins_to_buy += float(order_book["asks"][i][j+1])
				coins_to_buy += amount/ float(order_book["asks"][i][j])
				price_total_to_buy += amount
				break

		print("\t |-> You've bought %0.8f %s for %0.8f %s / from %f %s" % (coins_to_buy, pair_output, price_total_to_buy, pair_input, org_amount, pair_input))

	def getting_supported_coins(self):
		"""
		Retrieving Poloniex supported coins
		"""
		try:

			print("Retrieving supported coins symbol...")
			symbols = self.API.return_coins_symbols()
			print(" |-> Done")

			return symbols

		except Exception:
			print("[x] Cannot retrieve supported coins.")
			print("Program will exit.")
			self.safe_exit()

	def get_user_coin_pair(self):
		"""
		Get user input pair to exchange
		"""
		deposit_coin, exchange_coin = "", ""

		while True:
			deposit_coin = input("Please enter your deposit coin: ")
			deposit_coin = deposit_coin.upper()

			if deposit_coin in self.supported_coins:
				print(" |-> {0} is supported.".format(deposit_coin))
			else:
				pass

			exchange_coin = input("Please enter the coin you want to exchange to: ")
			exchange_coin = exchange_coin.upper()

			if exchange_coin in self.supported_coins:
				print(" |-> {0} is supported".format(exchange_coin))
				pair = deposit_coin +"_"+ exchange_coin
				print("Cheking if the pair {0} is valid...".format(pair))

				if pair in self.pairs:
					print(" |-> Valid.")

					return pair

				else:
					print("[x] The pair {0} is not valid!".format(pair))

	def getting_order_book(self, currency_pair):
		"""
		Getting Poloniex order book
		"""
		currency_pair = currency_pair.upper()

		return self.API.return_order_book(currency_pair)


	def pretty_format_order_book(self, currency_pair):
		"""
		Formatting order book in the terminal 
		"""
		try:
			print("Retrieving order book for the pair: {0}".format(currency_pair.upper()))

			order_book = self.getting_order_book(currency_pair)
			ASK = order_book["asks"]
			BID = order_book["bids"]
			mainUnity = currency_pair.split("_")[0]
			price_unity = "Price/"+ mainUnity.upper()
			exchUnity = currency_pair.split("_")[1]
			ask_unity = "ASK/"+ exchUnity.upper()
			bid_unity = "BID/"+ exchUnity.upper()

			print(" |-> Done")
			print("\t\t\t\t{0} Order book".format(currency_pair.upper()))
			print("\t--------------------------------------------------------------")
			print("\t{:^13} | {:^13} | {:^13} | {:^13}".format(price_unity, ask_unity, price_unity, bid_unity))
			print("\t--------------------------------------------------------------")

			for i in range(len(ASK)):
				print("\t{:^13} | {:^13} | {:^13} | {:^13}".format(ASK[i][0], ASK[i][1], BID[i][0], BID[i][1]))

		except Exception:
			print("[x] Cannot retrieve {0} order book.".format(currency_pair.upper()))
			print("Program will exit....")
			self.safe_exit()


	def getting_ticker_currency(self, currency_pair):
		"""
		Getting Poloniex input pair Ticker
		"""
		currency_pair = currency_pair.upper()
		try:
			print("Retrieving ticker for the pair: {0}...".format(currency_pair))
			ticker = self.API.return_ticker(currency_pair)
			print(" |-> Done")
			return ticker
		except Exception:
			print("Cannot retrieve {0} ticker".format(currency_pair))
			self.safe_exit()


	def pretty_format_currency_ticker(self, currency_pair):
		"""
		Formatting input pair ticker
		"""
		ticker = self.getting_ticker_currency(currency_pair)
		mainUnity, secondUnity = currency_pair.split("_")[0], currency_pair.split("_")[1]
		mainUnity = mainUnity.upper()
		frozen = ""

		if int(ticker['isFrozen']) == 0:
			frozen = "NO"
		else:
			frozen = "Yes"

		print("\t\tCurrency Pair: {0}".format(currency_pair.upper()))
		print("\t-------------------------------------------")
		print("\t-> High price in 24h: {0} {1}".format(ticker['high24hr'], mainUnity))
		print("\t-> Base volume: {0} {1}".format(ticker['baseVolume'], mainUnity))
		print("\t-> Lowest price in 24h: {0} {1}".format(ticker['low24hr'], mainUnity))
		print("\t-> Is Frozen: {0}".format(frozen))
		print("\t-> Percentage change: {0} {1}".format(ticker['percentChange'], "%"))
		print("\t-> Lowest ASK: {0} {1}".format(ticker['lowestAsk'], mainUnity))
		print("\t-> Last price: {0} {1}".format(ticker['last'], mainUnity))
		print("\t-> Quote volume: {0} {1}".format(ticker['quoteVolume'], secondUnity))
		print("\t-> Highest BID: {0} {1}".format(ticker['highestBid'], mainUnity))
		print("\t-------------------------------------------")


	def getting_coins_info(self, coin_symbol):
		"""
		Getting Polonix coin info
		"""
		coin_info = []
		coin_symbol = coin_symbol.upper()
		try:
			print("Retrieving {0} info ...".format(coin_symbol))
			coin_info = self.API.return_currencies_info(coin_symbol)
			print(" |-> Done\n")
			return coin_info
		except Exception:
			print("[x] Failes to retrieve {0} informations".format(coin_symbol))
			self.safe_exit()
			return False

	def pretty_format_coins_info(self, coin_symbol):
		"""
		Formatting coin info 
		"""
		frozen, disabled, delisted = "","",""
		coin_info = self.getting_coins_info(coin_symbol)

		if coin_info[3] == 0:
			frozen = "No"
		else:
			frozen = "Yes"

		if coin_info[4] == 0:
			disabled = "No"
		else:
			disabled = "Yes"

		if coin_info[5] == 0:
			delisted = "No"
		else:
			delisted = "Yes"

		print(" {:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10}".format("Symbol", "Name", "Fees",
		 "Min confir", "Frozen", "Disabled", "Delisted"))
		print("{:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10}".format(coin_symbol, coin_info[0], coin_info[1], coin_info[2],
			frozen, disabled, delisted))
		print("\n")


	def getting_pairs(self):
		"""
		Getting Poloniex supported pairs
		"""
		pairs = []
		try:
			print("Retrieving supported pairs to exchange...")
			pairs = self.API.return_pairs()
			print(" |-> Done\n")
		except Exception:
			print("[x] Failed to retrieve pairs!")
			self.safe_exit()
		return pairs

	def safe_exit(self):
		"""
		Safe exit from the terminal
		"""
		print("Program will exit ...")
		sys.exit()


	def pretty_format_pairs(self, pairs):
		"""
		Formatting pairs
		"""
		k = 0
		print("\n")

		for i in pairs:
			k+= 1
			print("| {:^13} ".format(i), end = "   ")

			if k == 5:
				print(" ")
				k = 0

		print("\n")		

### Test ####

if __name__ == '__main__':
	app = Wrapper()
	app.run()

