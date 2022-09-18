from urllib.request import urlopen
import json
import os
import sys
from matplotlib import markers
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import webbrowser as wb

import fmpAPI_terminal
path_prefix = fmpAPI_terminal.__path__[0]

apikey = os.getenv('FMP_API_KEY')

if apikey is None:
	print('No FMP_API_KEY environment variable detected. Cannot proceed.')
	exit()


statement_url = {'is': 'https://financialmodelingprep.com/api/v3/income-statement/',
    'bs': 'https://financialmodelingprep.com/api/v3/balance-sheet-statement/',
    'cf': 'https://financialmodelingprep.com/api/v3/cash-flow-statement/',
    'ev': 'https://financialmodelingprep.com/api/v3/enterprise-values/',
    'ttm': 'https://financialmodelingprep.com/api/v3/key-metrics-ttm/'} 

################################################################################################################################
################################################################################################################################
def printStatements(ticker, year):
    is_, bs_, cf_, _ = getStatements(ticker, period='Y')
    is_title, bs_title, cf_title = '--------------------- INCOME STATEMENT -----------', '-------------------- BALANCE SHEET ---------------', '--------------------- CASH FLOW ------------------'
    is_keys = [is_title, 'revenue', 'costOfRevenue', 'grossProfit', 'researchAndDevelopmentExpenses', 'generalAndAdministrativeExpenses', 'sellingAndMarketingExpenses', 'sellingGeneralAndAdministrativeExpenses', 'otherExpenses', 'operatingExpenses', 'costAndExpenses', 'interestIncome', 'interestExpense', 'depreciationAndAmortization', 'ebitda', 'operatingIncome', 'totalOtherIncomeExpensesNet', 'incomeBeforeTax', 'incomeTaxExpense', 'netIncome', 'weightedAverageShsOutDil']
    
    bs_keys = [bs_title,'cashAndCashEquivalents', 'shortTermInvestments', 'cashAndShortTermInvestments', 'netReceivables', 'inventory', 'otherCurrentAssets', 'totalCurrentAssets', 'propertyPlantEquipmentNet', 'goodwill', 'intangibleAssets', 'goodwillAndIntangibleAssets', 'longTermInvestments', 'taxAssets', 'otherNonCurrentAssets', 'totalNonCurrentAssets', 'otherAssets', 'totalAssets', 'accountPayables', 'shortTermDebt', 'taxPayables', 'deferredRevenue', 'otherCurrentLiabilities', 'totalCurrentLiabilities', 'longTermDebt', 'deferredRevenueNonCurrent', 'deferredTaxLiabilitiesNonCurrent', 'otherNonCurrentLiabilities', 'totalNonCurrentLiabilities', 'otherLiabilities', 'capitalLeaseObligations', 'totalLiabilities', 'preferredStock', 'commonStock', 'retainedEarnings', 'accumulatedOtherComprehensiveIncomeLoss', 'othertotalStockholdersEquity', 'totalStockholdersEquity', 'totalLiabilitiesAndStockholdersEquity', 'minorityInterest', 'totalEquity', 'totalLiabilitiesAndTotalEquity', 'totalInvestments', 'totalDebt', 'netDebt']

    cf_keys = [cf_title, 'deferredIncomeTax', 'stockBasedCompensation', 'changeInWorkingCapital', 'accountsReceivables', 'accountsPayables', 'otherWorkingCapital', 'otherNonCashItems', 'netCashProvidedByOperatingActivities', 'investmentsInPropertyPlantAndEquipment', 'acquisitionsNet', 'purchasesOfInvestments', 'salesMaturitiesOfInvestments', 'otherInvestingActivites', 'netCashUsedForInvestingActivites', 'debtRepayment', 'commonStockIssued', 'commonStockRepurchased', 'dividendsPaid', 'otherFinancingActivites', 'netCashUsedProvidedByFinancingActivities', 'effectOfForexChangesOnCash', 'netChangeInCash', 'cashAtEndOfPeriod', 'cashAtBeginningOfPeriod', 'operatingCashFlow', 'capitalExpenditure', 'freeCashFlow']

    is_up, bs_up, cf_up = {is_title:'-'}, {bs_title:'-'}, {cf_title:'-'}
    is_up.update(is_[str(year)])
    bs_up.update(bs_[str(year)])
    cf_up.update(cf_[str(year)])

    is_df = pd.DataFrame.from_dict(is_up, orient='index').loc[is_keys]
    bs_df = pd.DataFrame.from_dict(bs_up, orient='index').loc[bs_keys]
    cf_df = pd.DataFrame.from_dict(cf_up, orient='index').loc[cf_keys]
    is_df.columns, bs_df.columns, cf_df.columns =[year], [year], [year]
    
    pd.set_option('display.max_rows',500)
    df = pd.concat([is_df,bs_df,cf_df], axis=0)
    
    print(df)
    return df

################################################################################################################################
# Statement API / folder fetchers
################################################################################################################################
def getStatements(ticker, period='Y'):
    # Get data from /SECfillings/statement.txt or API:

    is_ = getData(ticker, 'is', period)
    bs_ = getData(ticker, 'bs', period)
    cf_ = getData(ticker, 'cf', period)
    ev_ = getData(ticker, 'ev', period)

    # convert to dictionary     
    is_dict, bs_dict, cf_dict, ev_dict =  {}, {}, {}, {}
    for i in range(min(len(is_),len(bs_),len(cf_),len(ev_))):
        is_itr, bs_itr, cf_itr, ev_itr = dict(is_[i]), dict(bs_[i]), dict(cf_[i]), dict(ev_[i])
        calendarYear = is_itr['calendarYear']
        if calendarYear is None:
            calendarYear = is_itr['fillingDate'][2:3]

        if period == 'Q':  
            calendarYear = calendarYear[-2:] + is_itr['period']

        is_dict[calendarYear] = is_itr
        bs_dict[calendarYear] = bs_itr
        cf_dict[calendarYear] = cf_itr
        ev_dict[calendarYear] = ev_itr
    
    return is_dict, bs_dict, cf_dict, ev_dict

def getData(ticker, statement_type, period='Y'):
    
    ticker = ticker.upper()
    postfix = {'Y':'a','Q':'q'}
    linkprefix = {'Y':'year','Q':'quarter'}
    
    # check if /SECfillings/statement.txt exists: if True, retrive; else, online API and write to file
    file_path = os.path.join(path_prefix,'SECfilings',linkprefix[period], ticker+'_'+statement_type+postfix[period]+'.txt' )
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read(); file.close()
            return json.loads(content)
 
    else:
        print('Downloading '+ticker+' '+linkprefix[period]+'ly '+statement_type+'data into SECfilings/'+linkprefix[period])
        url = statement_url[statement_type] + ticker +'?period='+linkprefix[period]+ '&apikey=' + apikey
        response = urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        if data:
            with open(file_path, 'w') as file:
                file.write(json.dumps(data)); file.close()
        else:
            print('Invalid '+ticker+'\n')
        return data

def getTTM(ticker):
    ticker = ticker.upper()
    # check if /SECfillings/statement.txt exists: if True, retrive; else, online API and write to file 
    file_path = os.path.join(path_prefix, 'SECfilings','ttm', ticker+'_ttm.txt' )
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read(); file.close()
            return json.loads(content)[0]
 
    else:
        print('Downloading '+ticker+' ttm data into SECfilings/ttm')
        url = statement_url['ttm'] + ticker + '?apikey=' + apikey
        response = urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        if data:
            with open(file_path, 'w') as file:
                file.write(json.dumps(data)); file.close()
        else:
            print('Invalid '+ticker+'\n')
        return data[0]

def getHistoricPrice(ticker, format='dict'):
    ticker = ticker.upper()
    file_path = os.path.join(path_prefix, 'historic', ticker+'.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read(); file.close()
            data = json.loads(content)
            return pd.DataFrame(data['historical'])
    else:
        print('Downloading '+ticker +' historic daily price')
        url = 'https://financialmodelingprep.com/api/v3/historical-price-full/' + ticker +'?serietype=line&apikey=' + apikey
        response = urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        if data:
            with open(file_path, 'w') as file:
                file.write(json.dumps(data)); file.close()
        else:
            print('Invalid '+ticker+'\n')
        return pd.DataFrame(data['historical'])

################################################################################################################################
# Downloading from csv functions
################################################################################################################################
def downloadStatements(csv_name, period):
    # load csv to get tickers
    file_path = os.path.join(path_prefic, 'marketIndex', csv_name,'.csv')
    df = pd.read_csv(file_path)
    symbols = df['symbol']

    # loop over symbols 
    for ticker in symbols:
        getStatements(ticker, period)
        print(''+ticker+' fetched...')

def downloadHistoricPrices(csv_name):
    # load csv to get tickers
    df = pd.read_csv(file_path)
    symbols = df['symbol']

    # loop over symbols 
    for ticker in symbols:
        getHistoricPrice(ticker)
        print(''+ticker+' fetched...')

################################################################################################################################
# Database Updates
################################################################################################################################
def updateStatementsfromList(path_, period):
    tickers = getTickerList(os.join(path_prefix,'charts/'+str(path_)))
    for t in tickers:
        updateStatements(t, period)

def updateStatements(ticker, period):
    # delete existing statments
    ttm_path = os.path.join(path_prefix, 'SECfilings','ttm'+ticker.upper()+'_ttm.txt')
    if os.path.exists(ttm_path):
        os.remove(ttm_path)
    if period == 'Y':
        path = os.path.join(path_prefix,'SECfilings','year',ticker.upper())
        if os.path.exists(path+'_bsa.txt'):
            os.remove(path+'_bsa.txt')
        if os.path.exists(path+'_isa.txt'):
            os.remove(path+'_isa.txt')
        if os.path.exists(path+'_cfa.txt'):
            os.remove(path+'_cfa.txt')
        if os.path.exists(path+'_eva.txt'):
            os.remove(path+'_eva.txt')
    else:
        path = os.path.join(path_prefix,'SECfilings','quarter',ticker.upper())
        if os.path.exists(path+'_bsq.txt'):
            os.remove(path+'_bsq.txt')
        if os.path.exists(path+'_isq.txt'):
            os.remove(path+'_isq.txt')
        if os.path.exists(path+'_cfq.txt'):
            os.remove(path+'_cfq.txt')
        if os.path.exists(path+'_evq.txt'):
            os.remove(path+'_evq.txt')
    # re-download all
    is_, bs_, cf_, ev_ = getStatements(ticker, period)
    ttm = getTTM(ticker.upper())

################################################################################################################################
# Database Diagnostics
################################################################################################################################
def checkListStatements(csv_name):    
    # this script checks if ticker in csv has non-empty statements
    df = pd.read_csv('marketIndex/'+csv_name+'.csv')
    symbols = df['symbol']

    for ticker in symbols:
        is_, _, _, _ = getStatements(ticker)
        if not bool(is_):
            print(ticker.upper()+' is empty')

def checkStatement(ticker): # checks if ticker is valid
    is_, _, _, _ = getStatements(ticker.upper())
    if not bool(is_):
        print(ticker.upper()+' Empty')
    else:
        print(ticker.upper()+' has values.')

################################################################################################################################
# Misc. functions
################################################################################################################################
def getTickerList(path_):
    # read text file for tickers 
    file = open(path_+'/tickers.txt', 'r')
    content = file.readlines() 
    ticker_list = []
    for l in content:
        ticker_list.append(l[0:-1])
    
    return ticker_list

def fl2str(value_fl):
    # conversion dictionary set up
    np.seterr(divide='ignore')
    unit_dict = {'k': 1e-3, 'M': 1e-6, 'B': 1e-9, 'T': 1e-12}
    digits = np.log(np.abs(value_fl)) / np.log(10)

    temp = value_fl[digits < 6].copy()
    temp = round(temp * unit_dict['k'],1)
    temp6 = temp.apply(lambda x: repr(str(x)+'k'))

    temp = value_fl[(digits >= 6) & (digits < 9)].copy()
    temp = round(temp * unit_dict['M'],1)
    temp69 = temp.apply(lambda x: repr(str(x)+'M'))
    
    temp = value_fl[(digits >= 9) & (digits < 12)].copy()
    temp = round(temp * unit_dict['B'],1)
    temp912 = temp.apply(lambda x: repr(str(x)+'B'))

    temp = value_fl[digits >= 12].copy()
    temp = round(temp * unit_dict['T'],1)
    temp12 = temp.apply(lambda x: repr(str(x)+'T'))
    
    # concat
    value_fl = pd.concat([temp6, temp69, temp912, temp12], axis=0)
    value_fl = value_fl.apply(lambda x: x[1:-1])

    return value_fl

if __name__ == '__main__':
    ticker = 'aapl'
    
    is_, bs_, cf_, ev_ = getStatements(ticker, period='Y')
    # ttm_ = getTTM(ticker)
    # printStatement(ticker, '2021')

    # check statements:
    # checkStatement(ticker)

    # update database:
    # updateStatement(ticker, period='Y')
    # updateSEC(ticker)
    # updateSECfromPath('example')

    # download data:
    # downloadStatements('sp500', period='Q')
    # downloadHistoricPrices('sp500')

    # get historic price
    # p = getHistoricPrice('msft')

    # CHECK IF MY CHANGEINWORKCAPITAL IS OKAY
    # s = pd.read_csv('marketIndex/sp500.csv')
    # tickers = s['symbol']
    # for t in ['msft']:
    #     try:  
    #         # print('Processing '+t+'...')
    #         df = printStatement(t ,2020)
    #         ebiat = df.loc['ebitda'] - df.loc['incomeTaxExpense']
    #         capex = df.loc['capitalExpenditure'] 
    #         ar = df.loc['accountsReceivables']
    #         ap = df.loc['accountsPayables']
    #         inv = df.loc['inventory']
    #         tempfcf = ebiat + capex - ar - inv + ap
    #         fcf = df.loc['freeCashFlow']
    #         print(str(fcf.values)+' '+str(tempfcf.values))
    #     except:
    #         0
    #         # print(t+' failed')
    print('End of self-Check Script.')
