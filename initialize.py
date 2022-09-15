import os
from urllib.request import urlopen
import json

# create files and directories: 
os.system('mkdir charts; mkdir SECfilings')
os.system('cd SECfilings; mkdir quarter; mkdir year; mkdir ttm')
os.system('cd charts; mkdir watchlist')
os.system('cd charts/watchlist; touch tickers.txt')
os.system('cd charts/watchlist; touch tickers.txt; echo aapl >> tickers.txt; echo msft >> tickers.txt; echo goog >> tickers.txt')
# help\commands.txt

# prompt user for API key (take user to website)
print("\nInput your apikey here. If you don't have an apikey, create a (free) account in https://site.financialmodelingprep.com/login to obtain one. Once you've created an account you can find the apikey in https://site.financialmodelingprep.com/developer/docs under 'Your Details' section.\n")
data, itr = {}, 0
while isinstance(data, dict):
    if itr !=0:
        print('\n'+data['Error Message']+'\n')
        
    apikey = input('apikey: ')
    # check if apikey is valid
    url = 'https://financialmodelingprep.com/api/v3/income-statement/INTC?period=year&apikey='+apikey
    response = urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    itr=itr+1
    

# save apikey in textfile for api.py access
os.system('touch apikey.txt; echo '+apikey+' >> apikey.txt')

# Terminate initialization
print('\nInitialization complete. You may now run main.py in terminal. If this is the first time you are using this package, run example.py for a brief interactive introduction. \n\nHave fun! \nIbrahim Al Balushi.\n')