import psycopg2
import requests
import json
import csv
from collections import defaultdict
import sched,time
import configparser
import urllib3
urllib3.disable_warnings()
import celery
#Read Config File 

#Config = configparser.RawConfigParser()
#Config.read('./config.ini')

#Get database info from config file

hostname = 'postgressql-cryptocurrency.cibilq8azida.us-east-2.rds.amazonaws.com'
username = 'acms_user'
password = 'acms1234'
database = 'CryptocurrencyDb'
port = '5432'
url = 'https://api.coinmarketcap.com/v1/ticker'
"""
hostname = 'baasu.db.elephantsql.com'
username = 'dbuzkqmi'
password = 'vi24qSFc5TG77k5GPa4aQr3XlnLOBIRf'
database = 'dbuzkqmi'
port = '5432'
url = 'https://api.coinmarketcap.com/v1/ticker'
"""
coins=['BTC','ETH','LTC','XRP','BCH']
@celery.task()
def insertIntoDatabase():
	urllib3.disable_warnings()
	print("Function called")
	# Database Connection	
	myConnection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database,port=port)
	curr=myConnection.cursor()
	# Fetch Data From api coinmarket cap
	response=requests.get(url)
        #Loads data in json format
	Y=json.loads(response.text)
        X=[]
        for y in Y:
	     if(y['symbol'] in coins):
		  X.append(y)
 
	count=0
        #store json data in the form of dictionary 
	deleteQuery="delete from currency_current"
	curr.execute(deleteQuery)
	for x in X:
		insertQuery="INSERT INTO public.currency_current(currency) values ('{}')".format(json.dumps(x))
		curr.execute(insertQuery)
	myConnection.commit()
	values=dict()
	for x in X:
		if count == 0 :
			header=x.keys()
			count+=1
		val=x.values()
		for i in range(len(header)) :
			if val[i] is None :
				val[i]=0
			if header[i] in values:
				values[header[i]].append(val[i])
			else:
				values[header[i]]=[val[i]]
			count+=1
	
        #Insert Dictionary (Convert from json) into database
	k=insertIntoDatabase.counter
	
	for i in range(len(X)) :
		insertquery="INSERT INTO public.currency(ID,ID_DAY,ID_MONTH,name,symbol,rank,price_usd,price_btc,c_24h_volume_usd,market_cap_usd,available_supply,total_supply,max_supply,percentage_change_1h,percentage_change_24h,percentage_change_7d,last_updated) values({},{},{},'{}','{}',{},{},{},{},{},{},{},{},{},{},{},{})".format(k,k/6,k/36,values['name'][i],values['symbol'][i],values['rank'][i],values['price_usd'][i],values['price_btc'][i],values['24h_volume_usd'][i],values['market_cap_usd'][i],values['available_supply'][i],values['total_supply'][i],values['max_supply'][i],values['percent_change_1h'][i],values['percent_change_24h'][i],values['percent_change_7d'][i],values['last_updated'][i])
		curr.execute(insertquery)
        # Commit changes
	myConnection.commit()
	insertIntoDatabase.counter=insertIntoDatabase.counter+1
	myConnection.close()
        # Run service in particular intervals
insertIntoDatabase.counter=0

