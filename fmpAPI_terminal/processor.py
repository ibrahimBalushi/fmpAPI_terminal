from .api import *

################################################################################################################################
# SEARCH engine
################################################################################################################################
def searchGrowth(csv_name):
    
    # Get symbols in csv
    df = pd.read_csv('marketIndex/'+csv_name+'.csv')
    symbols = df['symbol']

    for ticker in symbols:
        print('Checking: '+ticker)
        # check if statement is nonempty
        isa_, _, _, _ = getStatements(ticker)
        if not bool(isa_):
            print(ticker+' is Empty')
            continue

        # retrive growth metrics
        metrics = getGrowthMetrics(ticker)
        # check criteria
        roic = metrics.loc['roic'].min()    
        equity = metrics.loc['equity'].min()
        revenue = metrics.loc['revenue'].min()
        eps = metrics.loc['eps'].min()
        cash = metrics.loc['cash'].min()
        minValue = min([roic, equity, eps, cash])
        if minValue >= 0.1:
            # save to file those meeting criteria
            with open('searches/pass.txt','a') as passfile:
                passfile.write(ticker)
                passfile.write('\n')
        else: 
            print(ticker+' failed')
            # save to file those failing criteria
            with open('searches/fail.txt','a') as failfile:
                failfile.write(ticker+'\n')

################################################################################################################################
# VALUATION MODEL ###############################################################################################################################
def chart_path(path_, filename=None):
	if filename is None:
		return os.path.join(path_prefix, 'charts',path_)
	else:
		return os.path.join(path_prefix, 'charts',path_, filename)
		

def writeMOS(path_):
    ticker_ls = getTickerList(chart_path(path_))
    with open(os.path.join(path_prefix,'charts',path_+'/MOS.txt'),'w') as file:
        for tkr in ticker_ls:
            MOSdict = computeMOS(tkr)
            file.write(MOSdict.to_string()+'\n---------------------------------------------------\n')
    file.close()


def computeMOS(ticker, onscreen=False):
    
    # uppcase just in-case
    ticker = ticker.upper()

    # # TTM EPS
    ttmEPS = getTTM(ticker)['netIncomePerShareTTM']
    
    # Get historic growth and P/E ratios
    # equity growth
    growth_table, _ = getGrowthMetrics(ticker)
    equity5YGrowth = round(growth_table.loc['equity']['5Y'],2)
    # historic P/E
    trends_dict = getTrendMetrics(ticker, 5)
    histPE = round(trends_dict['valuation'].loc['P/E',:].values.mean(),0)

    # read file for analyst estimates:
    file = pd.read_csv(os.path.join(path_prefix,'parameters','valuation'), index_col=0)
    # and analyst(yahoo) growth
    analyst5YGrowth = file.loc[ticker][0]

    # default P/E 
    defaultPE = round(2 * min(equity5YGrowth, analyst5YGrowth) * 100,0)

    # Calculate Valuation:    
    def calculator(Growth, estPE):
        # Grow TTM EPS 5 years into the future
        futureEPS = ttmEPS * ((1+Growth) ** 5)
        # Get future  Price from estimated future P/E  
        futurePrice = futureEPS * estPE
        # Discount at 15% to present for Fair Value
        fairPrice = futurePrice / ((1 + 0.15) ** 5)
        
        FOS = 0.5   # FACTOR of SAFETY prescribed
        
        if Growth<0:
            fairPrice=0
        return round(fairPrice, 2) * FOS

    frame = pd.DataFrame([[calculator(equity5YGrowth, histPE), calculator(analyst5YGrowth, histPE)],[calculator(equity5YGrowth, defaultPE), calculator(analyst5YGrowth, defaultPE)]],columns=['equity ('+str(equity5YGrowth)+')','analyst ('+str(analyst5YGrowth)+')'],index=['P/E ('+str(histPE)+')','default ('+str(defaultPE)+')'])
    frame.index.name = ticker
    
    if onscreen:
        print(frame)
    return frame

################################################################################################################################
# GRAPHICAL generators ################################################################################################################################
# plot COMPARE functions
def comparePlots(ticker_list, field, years, period):

    _, ax = plt.subplots(figsize=(7,6))
    for ticker in ticker_list:
        _, gdetails = getGrowthMetrics(ticker, years, period)
        metrics = getAllMetrics(ticker, period)

        # trends = getTrendMetrics(ticker, years, period)
        # trends['valuation'].index = ['pe','pc','pb','price','fcy']
        
        # ABSOLUTE values
        old_fields = ['revenue','netIncome','operatingIncome','freeCashFlow','totalStockholdersEquity','revenuePerShare','netIncomePerShare','operatingIncomePerShare','freeCashFlowPerShare','totalStockholdersEquityPerShare','longTermDebtCoverage','grossProfitMargin','operatingProfitMargin','netIncomeMargin','inventoryTurnover','capitalExpenditure','priceToEarnings','priceToOperatingIncome','priceToFreeCashFlow','priceToBook','freeCashFlowYield','returnOnInvestedCapital','totalStockholdersEquityGrowth','netIncomeGrowth','revenueGrowth','freeCashFlowGrowth','stockPriceGrowth','sharesRepurchaseRate']
        fields = ['r','ni','oi','fcf','e','rps','eps','ops','fcfps','eqps','dc','gpm','opm','nim','it','capex','pe','poi','pfcf','pb','fcfy','roic','eg','epsg','rg','fcfg','pg','srr']
        compare = pd.DataFrame([],columns=fields)
        fields_dict = dict(zip(fields, old_fields))
        for f in fields:
            compare.loc[:,f] = metrics[fields_dict[f]]
        compare.sort_index(inplace=True)
        ax.plot(compare[field][0:years], marker='o')
        
    ax.legend(ticker_list)
    ax.set_xlabel('time')
    ax.invert_xaxis()
    ax.yaxis.set_label_position('right')
    ax.set_ylabel(str(field))
    ax.invert_xaxis()
    ax.tick_params(labeltop=True, labelright=True)
    ax.set_title('('+fields_dict[field]+')')
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    plt.show()

# PLOT from ticker functions
def makeGrowthPlot(ticker, metric, path_='screen' ,years=10):
    
    # get tables
    summary, details = getGrowthMetrics(ticker)
    
    # print table
    print(summary.T[::-1].T.loc[[metric]][::-1])

    file_name = {'roic': '_1_growthROIC.png',
    'equity': '_2_growthEquity.png',
    'eps': '_3_growthEPS.png',
    'revenue': '_4_growthRevenue.png',
    'cash': '_5_growthCash.png',
    'price': '_6_growthPrice.png'}

    # print table
    # plot growthSummary
    _, ax = plt.subplots()
    summary.loc[metric][::-1].T.plot.bar(ax=ax)
    ax.set_xlabel('Period (average)')
    ax.set_ylabel('Rate')
    ax.set_title(metric+' Growth ('+ticker+')')
    ax.xaxis.set_label_position('bottom')
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax2 = ax.twiny()
    ax2.plot(details.loc[metric,:], marker='o',color='orange')
    ax2.set_xlabel('Period (annual)')
    ax2.set_ylabel('Rate')
    ax2.xaxis.set_label_position('top')
    ax2.invert_xaxis()
    ax2.xaxis.tick_top()
    
    if path_ != 'screen':
        plt.savefig(chart_path(path_, ticker+file_name[metric]), dpi=200)
        plt.close()
    else:
        plt.show()
    
    return summary, details

def makeTrendPlot(ticker, years, trend_name, period='Y', path_='screen'):
    
    # get tables
    trends_dict = getTrendMetrics(ticker, years, period)
    incomeTrend = trends_dict['income']
    stockEquityTrend = trends_dict['stockequity']
    liabilityTrend = trends_dict['liability']
    marginTurnoverTrend = trends_dict['margins']
    investmentTrend = trends_dict['investment']
    valuationTrend = trends_dict['valuation']

    # plot incomeTrend
    def plotIncome(ticker, path_='screen'):
        _, ax = plt.subplots()
        trend = incomeTrend.iloc[:,::-1].T
        ax.plot(trend[['earnings','opIncome','cash']], marker='o', label=['earnings','opIncome','cash'])
        ax.legend(loc='upper left')
        ax.set_xlabel('Time')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_ylabel('$ in Millions')
        ax.set_title('Income Trend ('+ticker+')')
        ax2 = ax.twinx()
        ax2.bar(trend.index, trend['revenue'], label='revenue', alpha=0.2)
        ax2.legend(loc='upper right')
        ax2.set_ylabel('$ in Millions')
        if path_ != 'screen':
            plt.savefig(chart_path(path_,ticker+'_trend_1_income.png'), dpi=200)
            plt.close()
        else:
            plt.show()

    # plot stockEquityTrend
    def plotEquity(ticker, path_='screen'):
        _, ax = plt.subplots()
        trend = stockEquityTrend.iloc[:,::-1].T
        ax.plot(trend['equity'], label='equity', marker='o',color='blue')
        ax.legend(loc='upper left')
        ax.set_xlabel('Time')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_ylabel('$ in Millions')
        ax.set_title('Equity and Dilution ('+ticker+')')
        ax2 = ax.twinx()
        ax2.bar(trend.index, trend['sharesOut'], label='sharesOut', alpha=0.4, color='purple')
        ax2.legend(loc='upper right')
        ax2.set_ylabel('Shares Outstanding')
        if path_ != 'screen':
            plt.savefig(chart_path(path_,ticker+'_trend_2_stockequity.png'), dpi=200)
            plt.close()
        else:
            plt.show()


    # plot liabilityTrend
    def plotLiability(ticker, path_='screen'):
        _, ax = plt.subplots()
        trend = liabilityTrend.iloc[:,::-1].T
        ax.plot(trend['Debt-Enterprise'], marker='o', label='Debt-Enterprise')
        ax.set_xlabel('Time')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_ylabel('Ratio')
        ax.set_title('Liability trend ('+ticker+')')
        ax.legend(loc='upper left')
        ax2 = ax.twinx()
        ax2.bar(trend.index, trend['Debt Coverage'], label='Debt Coverage', color='red', alpha=0.2)
        ax2.legend(loc='upper right')
        ax2.set_ylabel('Time (years)')
        if path_ != 'screen':
            plt.savefig(chart_path(path_,+ticker+'_trend_3_liability.png'), dpi=200)
            plt.close()
            if period == 'Q':
                os.remove(chart_path(path_,ticker+'_trend_3_liability.png'))
        else:
            plt.show()

    # plot marginTurnoverTrend
    def plotMargins(ticker, path_='screen'):
        _, ax = plt.subplots()
        trend = marginTurnoverTrend.iloc[:,::-1].T
        ax.plot(trend[['operatingProfitMargin','netIncomeMargin']], marker='o', label=['operatingProfitMargin','netIncomeMargin'])
        ax.set_xlabel('Time')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_ylabel('Ratio')
        ax.set_title('Margins and Inventory ('+ticker+')')
        ax.legend(loc='upper left')
        ax2 = ax.twinx()
        trend[['inventoryTurnover']].plot.bar(ax=ax2, color='green', alpha=0.5)
        ax2.legend(loc='upper right')
        ax2.set_ylabel('Turnover Multiple')
        if path_ != 'screen':
            plt.savefig(chart_path(path_, ticker+'_trend_4_margins.png'), dpi=200)
            plt.close()
        else:
            plt.show()

    # plot investmentTrend
    def plotInvestment(ticker, path_='screen'):
        _, ax = plt.subplots()
        trend = investmentTrend.iloc[:,::-1].T
        ax.plot(trend[['Research-Dev','Plants-Equips','Marketing']], marker='o', label=['Research-Dev','Plants-Equips','Marketing'])
        df = pd.concat([trend['capex'], trend['goodwill']],axis=1)
        if period == 'Q':
            df.plot(y=['capex'], kind='bar',ax=ax, color={'capex':'black'},alpha=0.6)
        else:
            df.plot(y=['capex','goodwill'], kind='bar',ax=ax, color={'capex':'black','goodwill':'red'},alpha=0.6)
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_xlabel('Time')
        ax.set_ylabel('$ in Millions')
        ax.set_title('Investment Activities ('+ticker+')')
        ax.legend()
        if path_ != 'screen':
            plt.savefig(chart_path(path_, ticker+'_trend_5_investment.png'), dpi=200)
            plt.close()
        else:
            plt.show()

    # plot valuationTrend
    def plotValuation(ticker, path_='screen'):
        _, ax = plt.subplots()
        trend = valuationTrend.iloc[:,::-1].T
        trend[['P/E','P/OpI','P/B']].plot(ax=ax, marker='o', color={'P/E':'orange', 'P/OpI':'green', 'P/B':'blue'})
        ax.set_xlabel('Time')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_ylabel('Valuation Multiple')
        ax.set_title('Valuation Metrics ('+ticker+')')
        ax.legend(loc='upper left')
        ax2 = ax.twinx()
        ax2.bar(trend.index, trend['FCFyield'], label='FCF yield',alpha=0.2,color='green')
        ax2.set_ylabel('Yield')
        ax2.legend(loc='upper right')
        if path_ != 'screen':
            plt.savefig(chart_path(path_, ticker+'_trend_6_valuation.png'), dpi=200)
            plt.close()
        else:
            plt.show()

    plotter = {'income': plotIncome,
    'stockequity': plotEquity,
    'liability': plotLiability,
    'margins': plotMargins,
    'investment': plotInvestment,
    'valuation': plotValuation}

    # table dict
    table_dict = {'income': incomeTrend, 'liability': liabilityTrend, 'investment': investmentTrend, 'stockequity': stockEquityTrend, 'margins': marginTurnoverTrend, 'valuation': valuationTrend}
    # print table
    print(table_dict[trend_name])
    # plot trend
    plotter[trend_name](ticker, path_)
    
    return table_dict[trend_name]

################################################################################################################################
# Data TABLE Generators
################################################################################################################################
def getGrowthMetrics(ticker, years=10, period='Y'):

    # uppcase just in-case
    ticker = ticker.upper()

    # get all calculated values from statements
    dict_ = getAllMetrics(ticker, period)
    # check if there are enough years in history
    years = min(len(dict_['revenue'])-1,years)

    # growth year-by-year
    growthDetails = pd.DataFrame([dict_['returnOnInvestedCapital'][0:years], dict_['totalStockholdersEquityGrowth'][0:years], dict_['netIncomeGrowth'][0:years], dict_['revenueGrowth'][0:years], dict_['freeCashFlowGrowth'][0:years], dict_['stockPriceGrowth'][0:years], dict_['sharesRepurchaseRate'][0:years]], index=['roic','equity','eps','revenue','cash','price','sharesRepurchaseRate'])
    growthDetails  = growthDetails.apply(lambda x: round(x,2))
    growthDetails.name = ticker
    
    # 1Y, 3Y, 5Y and 10Y growth averages:
    dict_ = getAllMetrics(ticker, period='Y')
    # check if there are enough years in history
    years = min(len(dict_['revenue'])-1,years)

    growthSummary = pd.DataFrame([], index=['roic','equity','eps','revenue','cash','price'], columns=['1Y','3Y','5Y','10Y'])
    growthSummary.name = ticker

    def compound(FV, PV, n):
        if min(FV,PV) >0 : 
            g = round(((FV/PV)**(1/n) -1),2)
        else:
            g = 0
        return g

    growthSummary.loc['revenue','1Y'] = compound(dict_['revenue'][0],dict_['revenue'][1], 1)
    growthSummary.loc['cash','1Y'] = compound(dict_['freeCashFlow'][0],dict_['freeCashFlow'][1], 1)
    growthSummary.loc['eps','1Y'] = compound(dict_['netIncome'][0],dict_['netIncome'][1], 1)
    growthSummary.loc['equity','1Y'] = compound(dict_['totalStockholdersEquity'][0],dict_['totalStockholdersEquity'][1], 1)
    growthSummary.loc['roic','1Y'] = round(dict_['returnOnInvestedCapital'][0],2)
    growthSummary.loc['price','1Y'] = compound(dict_['stockPrice'][0],dict_['stockPrice'][1], 1)
    
    if years >= 3:
        growthSummary.loc['revenue','3Y'] = compound(dict_['revenue'][0],dict_['revenue'][3], 3)
        growthSummary.loc['cash','3Y'] = compound(dict_['freeCashFlow'][0],dict_['freeCashFlow'][3], 3)
        growthSummary.loc['eps','3Y'] = compound(dict_['netIncome'][0],dict_['netIncome'][3], 3)
        growthSummary.loc['equity','3Y'] = compound(dict_['totalStockholdersEquity'][0],dict_['totalStockholdersEquity'][3], 3)
        growthSummary.loc['roic','3Y'] = round(np.average(dict_['returnOnInvestedCapital'][list(range(3))]),2)
        growthSummary.loc['price','3Y'] = compound(dict_['stockPrice'][0],dict_['stockPrice'][3], 3)

    if years >= 5:
        growthSummary.loc['revenue','5Y'] = compound(dict_['revenue'][0],dict_['revenue'][5], 5)
        growthSummary.loc['cash','5Y'] = compound(dict_['freeCashFlow'][0],dict_['freeCashFlow'][5], 5)
        growthSummary.loc['eps','5Y'] = compound(dict_['netIncome'][0],dict_['netIncome'][5], 5)
        growthSummary.loc['equity','5Y'] = compound(dict_['totalStockholdersEquity'][0],dict_['totalStockholdersEquity'][5], 5)
        growthSummary.loc['roic','5Y'] = round(np.average(dict_['returnOnInvestedCapital'][list(range(5))]),2)
        growthSummary.loc['price','5Y'] = compound(dict_['stockPrice'][0],dict_['stockPrice'][5], 5)

    if years >= 10:
        growthSummary.loc['revenue','10Y'] = compound(dict_['revenue'][0],dict_['revenue'][10], 10)
        growthSummary.loc['cash','10Y'] = compound(dict_['freeCashFlow'][0],dict_['freeCashFlow'][10], 10)
        growthSummary.loc['eps','10Y'] = compound(dict_['netIncome'][0],dict_['netIncome'][10], 10)
        growthSummary.loc['equity','10Y'] = compound(dict_['totalStockholdersEquity'][0],dict_['totalStockholdersEquity'][10], 10)
        growthSummary.loc['roic','10Y'] = round(np.average(dict_['returnOnInvestedCapital'][list(range(10))]),2)
        growthSummary.loc['price','10Y'] =  compound(dict_['stockPrice'][0],dict_['stockPrice'][10], 10)
    return growthSummary, growthDetails

def getTrendMetrics(ticker, years, period='Y'):

    # uppcase just in-case
    ticker = ticker.upper()

    # get all calculated values from statements
    dict_ = getAllMetrics(ticker, period)

    # if years in history are less than requested, update years
    if period == 'Q': 
        q = 4
    else:
        q = 1
    years = int(min(np.floor(len(dict_['revenue'])/q), years) * q)
    
    trends_dict = dict.fromkeys(['income', 'liability', 'stockequity', 'investment', 'margins', 'valuation'])

    # income trend
    revenue_mils = dict_['revenue'] / 1e6
    operatingIncome_mils = dict_['operatingIncome'] / 1e6
    netIncome_mils = dict_['netIncome'] / 1e6
    freeCashFlow_mils = dict_['freeCashFlow'] / 1e6
    incomeTrend = pd.DataFrame([revenue_mils, operatingIncome_mils, freeCashFlow_mils, netIncome_mils], index=['revenue','opIncome','cash','earnings'], columns=dict_['revenuePerShare'].index).iloc[:,list(range(years))].round(2)
    incomeTrend.name = ticker
    trends_dict['income'] = incomeTrend

    # liabilities trend
    longTermDebtCoverage = dict_['longTermDebtCoverage']
    longTermDebtCoverage = longTermDebtCoverage.where(longTermDebtCoverage < 10, 10)
    longTermDebtCoverage = longTermDebtCoverage.where(longTermDebtCoverage > 0, 10)
    liabilityTrend = pd.DataFrame([dict_['debtEnterprise'], longTermDebtCoverage, dict_['netDebt'], dict_['enterpriseValue']], index=['Debt-Enterprise', 'Debt Coverage', 'Net Debt', 'EV'], columns=dict_['inventoryTurnover'].index).iloc[:,list(range(years))].round(2)
    liabilityTrend.name = ticker
    trends_dict['liability'] = liabilityTrend

    # sharesOutstanding trend
    totalStockholdersEquity = dict_['totalStockholdersEquity'] / 1e6
    marketCapitalization = dict_['marketCapitalization'] / 1e6
    stockEquityTrend = pd.DataFrame([dict_['sharesOutstanding'], totalStockholdersEquity, marketCapitalization], index=['sharesOut','equity', 'marketCap'],columns=dict_['sharesOutstanding'].index).iloc[:,list(range(years))]
    stockEquityTrend.name = ticker
    trends_dict['stockequity'] = stockEquityTrend

    # investment and aquasitions
    investmentTrend = pd.DataFrame([dict_['investmentsInPropertyPlantAndEquipment'], dict_['researchDevelopementExpenses'], dict_['sellingAndMarketingExpenses'], dict_['capitalExpenditure'], dict_['goodwill'], dict_['acquisitionsNet']], index=['Plants-Equips', 'Research-Dev','Marketing','capex','goodwill','netAquasitions'], columns=dict_['investmentsInPropertyPlantAndEquipment'].index).iloc[:,list(range(years))]
    investmentTrend = investmentTrend / 1e6
    investmentTrend.name = ticker
    trends_dict['investment'] = investmentTrend

    # turnover trend
    marginTurnoverTrend = pd.DataFrame([dict_['operatingProfitMargin'], dict_['netIncomeMargin'], dict_['inventoryTurnover'], dict_['payablesTurnover'], dict_['receivablesTurnover']], index=['operatingProfitMargin', 'netIncomeMargin', 'inventoryTurnover', 'payablesTurnover', 'receivablesTurnover'], columns=dict_['operatingProfitMargin'].index).iloc[:,list(range(years))].round(2)
    marginTurnoverTrend.name = ticker
    trends_dict['margins'] = marginTurnoverTrend

    # valuation
    valuationTrend = pd.DataFrame([dict_['priceToEarnings'], dict_['priceToOperatingIncome'], dict_['priceToFreeCashFlow'], dict_['priceToBook'], dict_['stockPrice'],dict_['freeCashFlowYield']], index=['P/E','P/OpI','P/FCF','P/B','price','FCFyield'], columns=dict_['priceToEarnings'].index).iloc[:,list(range(years))].round(2)
    valuationTrend.name = ticker
    trends_dict['valuation'] = valuationTrend

    return trends_dict

################################################################################################################################
# preliminary calculations from financial statements
################################################################################################################################
def getAllMetrics(ticker, period='Y'):
    
    fins_ = getFinancialValues(ticker, period)
    ratios_ = calculateRatios(ticker, period)
    growths_ = calculateGrowth(ticker, period)

    return {**fins_, **ratios_, **growths_}

def calculateGrowth(ticker, period='Y'): 

    fins_ = getFinancialValues(ticker, period)
    ratios_ = calculateRatios(ticker, period)

    # growth metrics
    def change(x):
        return ( x - x.shift(-1) ) / np.abs(x.shift(-1)).where(x!=0, np.nan)

    dict_ = {}
    dict_['totalStockholdersEquityGrowth'] = change(fins_['totalStockholdersEquity'])
    dict_['revenueGrowth'] = change(fins_['revenue'])
    dict_['operatingIncomeGrowth'] = change(fins_['operatingIncome'])
    dict_['netIncomeGrowth'] = change(ratios_['netIncomePerShare'])
    dict_['freeCashFlowGrowth'] = change(fins_['freeCashFlow'])
    dict_['stockPriceGrowth'] = change(fins_['stockPrice'])
    dict_['sharesRepurchaseRate'] = change(fins_['sharesOutstanding'])
    
    return dict_

def calculateRatios(ticker, period='Y'): 

    fins_ = getFinancialValues(ticker, period)

    ## calculate metrics ##
    if period == 'Y':
        revenueTTM = fins_['revenue']
        operatingIncomeTTM = fins_['operatingIncome']
        netIncomeTTM = fins_['netIncome']
        freeCashFlowTTM = fins_['freeCashFlow']
        totalStockholdersEquityTTM = fins_['totalStockholdersEquity']
    else:
        ttm = getTTMFinancialValues(ticker)
        revenueTTM = ttm['revenue']
        operatingIncomeTTM = ttm['operatingIncome']
        netIncomeTTM = ttm['netIncome']
        freeCashFlowTTM = ttm['freeCashFlow']
        totalStockholdersEquityTTM = ttm['totalStockholdersEquity']

    def ratio(x,d):
        return x / d.where(d!=0, np.nan)

    dict_ = {}
    # sharesOutstanding, marketCapitalization, revenue, operatingIncome, netIncome, freeCashFlow, totalStockHoldersEquity, grossProfit, netOperatingProfitAfterTax, investedCapital, accountRecievables, costOfRevenue, accountPayables, inventory, ebit, interestExpense, totalCurrentAssets, totalCurrentLiabilities, cashAndShortTermInvestments, enterpriseValue, debtEnterprise, netDebt, longTermDebt, totalDebt
    # Per share
    dict_['revenuePerShare'] = ratio(revenueTTM, fins_['sharesOutstanding'])
    dict_['operatingIncomePerShare'] = ratio(operatingIncomeTTM, fins_['sharesOutstanding'])
    dict_['netIncomePerShare'] = ratio(netIncomeTTM, fins_['sharesOutstanding'])
    dict_['freeCashFlowPerShare'] = ratio(freeCashFlowTTM, fins_['sharesOutstanding'])
    dict_['totalStockholdersEquityPerShare'] = ratio(totalStockholdersEquityTTM, fins_['sharesOutstanding'])

    # margins
    dict_['grossProfitMargin'] = ratio(fins_['grossProfit'], fins_['revenue'])
    dict_['operatingProfitMargin'] = ratio(fins_['operatingIncome'],  fins_['revenue'])
    dict_['netIncomeMargin'] = ratio(fins_['netIncome'], fins_['revenue'])

    # management and efficiency
    dict_['returnOnInvestedCapital'] = ratio(fins_['netOperatingProfitAfterTax'], fins_['investedCapital'])
    dict_['receivablesTurnover'] = ratio(fins_['revenue'], fins_['accountReceivables'])
    dict_['payablesTurnover'] = ratio(fins_['costOfRevenue'], fins_['accountPayables'])
    dict_['inventoryTurnover'] = ratio(fins_['costOfRevenue'], fins_['inventory'])

    # financial health (short)
    dict_['interestCoverage'] = ratio(fins_['ebit'], fins_['interestExpense'])
    dict_['currentRatio'] = ratio(fins_['totalCurrentAssets'], fins_['totalCurrentLiabilities'])
    dict_['quickRatio'] = ratio(fins_['cashAndShortTermInvestments'] + fins_['accountReceivables'], fins_['totalCurrentLiabilities'])
    dict_['cashRatio'] = ratio(fins_['cashAndCashEquivalents'], fins_['totalCurrentLiabilities'])
    # financial health (long) 
    dict_['debtEquity'] = ratio(fins_['netDebt'], fins_['marketCapitalization'])
    dict_['debtEnterprise'] = ratio(fins_['netDebt'], fins_['enterpriseValue'])
    dict_['debtEnterprise'] = dict_['debtEnterprise'].where(dict_['debtEnterprise'] > 0, 0)
    dict_['debtCaptial'] = ratio(fins_['totalDebt'], fins_['totalStockAndTotalDebt'])
    dict_['longTermDebtCoverage'] = ratio(fins_['longTermDebt'], fins_['freeCashFlow'])

    # valuation
    dict_['priceToEarnings'] = ratio(fins_['stockPrice'], dict_['netIncomePerShare'])
    dict_['priceToEarnings'] = dict_['priceToEarnings'].where(dict_['priceToEarnings'] > 0, 0)
    dict_['priceToFreeCashFlow'] = ratio(fins_['stockPrice'], dict_['freeCashFlowPerShare'])
    dict_['priceToFreeCashFlow'] = dict_['priceToFreeCashFlow'].where(dict_['priceToFreeCashFlow'] > 0, 0)
    dict_['priceToBook'] = ratio(fins_['marketCapitalization'], fins_['totalStockholdersEquity'])
    dict_['priceToBook'] = dict_['priceToBook'].where(dict_['priceToBook'] > 0, 0)
    dict_['freeCashFlowYield'] = ratio(1, dict_['priceToFreeCashFlow'])
    dict_['priceToOperatingIncome'] = ratio(fins_['stockPrice'], dict_['operatingIncomePerShare'])
    dict_['priceToOperatingIncome'] = dict_['priceToOperatingIncome'].where(dict_['priceToOperatingIncome'] > 0, 0)

    return dict_

def getTTMFinancialValues(ticker):
    fins_, dict_ = getFinancialValues(ticker, period='Q'), {}
    # aggregate quarters
    for k in fins_.keys():
        aggregate = fins_[k] + fins_[k].shift(-1) + fins_[k].shift(-2) + fins_[k].shift(-3)
        # keep 1st of every 4 aggregates
        dict_[k] = aggregate[::4]

    return dict_
    
def getFinancialValues(ticker, period='Y'):
    # check if /FinMetrics/metrics.txt exists: if True, retrive; else, create file with years
    is_, bs_, cf_, ev_ = getStatements(ticker, period)

    # transform to dataFrames for easier data access
    is_, bs_, cf_, ev_ = pd.DataFrame(is_), pd.DataFrame(bs_), pd.DataFrame(cf_), pd.DataFrame(ev_)

    dict_ = {}
    ## Income Statement:
    # Income
    dict_['revenue'] = is_.loc['revenue']
    dict_['operatingIncome'] = is_.loc['operatingIncome']
    dict_['grossProfit'] = is_.loc['grossProfit']
    dict_['interestIncome'] = is_.loc['interestIncome']
    dict_['ebitda'] = is_.loc['ebitda']
    dict_['incomeBeforeTax'] = is_.loc['incomeBeforeTax']
    dict_['netIncome'] = is_.loc['netIncome']
    # Expense
    dict_['operatingExpenses'] = is_.loc['operatingExpenses']
    dict_['costOfRevenue'] = is_.loc['costOfRevenue']
    dict_['incomeTaxExpense'] = is_.loc['incomeTaxExpense']
    dict_['interestExpense'] = is_.loc['interestExpense']
    dict_['depreciationAndAmortization'] = is_.loc['depreciationAndAmortization']
    dict_['researchDevelopementExpenses'] = is_.loc['researchAndDevelopmentExpenses']
    dict_['sellingAndMarketingExpenses'] = is_.loc['sellingAndMarketingExpenses']
    # other
    dict_['sharesOutstanding'] = is_.loc['weightedAverageShsOut']

    ### Balance Sheet:
    ## Assets
    # short-term
    dict_['cashAndCashEquivalents'] = bs_.loc['cashAndCashEquivalents']
    dict_['cashAndShortTermInvestments'] = bs_.loc['cashAndShortTermInvestments']
    dict_['totalCurrentAssets'] = bs_.loc['totalCurrentAssets']
    dict_['accountReceivables'] = bs_.loc['netReceivables']
    # long-term
    dict_['totalAssets'] = bs_.loc['totalAssets']
    dict_['goodwill'] = bs_.loc['goodwill']
    dict_['totalStockholdersEquity'] = bs_.loc['totalStockholdersEquity']
    ## Liabilities
    # short-term
    dict_['accountPayables'] = bs_.loc['accountPayables']
    dict_['inventory'] = bs_.loc['inventory']
    dict_['shortTermDebt'] = bs_.loc['shortTermDebt']
    dict_['totalCurrentLiabilities'] = bs_.loc['totalCurrentLiabilities']
    # long-term
    dict_['netDebt'] = bs_.loc['netDebt']
    dict_['longTermDebt'] = bs_.loc['longTermDebt']
    dict_['totalDebt'] = bs_.loc['totalDebt']
    dict_['totalLiabilities'] = bs_.loc['totalLiabilities']

    ## CashFlow Statement:
    # Cash from operating activities 
    dict_['operatingCashFlow'] = cf_.loc['operatingCashFlow']
    dict_['changeInWorkingCapital'] = cf_.loc['changeInWorkingCapital']
    dict_['netCashUsedProvidedByFinancingActivities'] = cf_.loc['netCashUsedProvidedByFinancingActivities']
    # Cash from investing activities 
    dict_['capitalExpenditure'] = -cf_.loc['capitalExpenditure']
    dict_['investmentsInPropertyPlantAndEquipment'] = -cf_.loc['investmentsInPropertyPlantAndEquipment']
    dict_['acquisitionsNet'] = cf_.loc['acquisitionsNet']
    # Cash from financing activities
    dict_['commonStockIssued'] = cf_.loc['commonStockIssued']
    dict_['commonStockRepurchased'] = -cf_.loc['commonStockRepurchased']
    dict_['dividendsPaid'] =  -cf_.loc['dividendsPaid']
    dict_['debtRepayment'] = -cf_.loc['debtRepayment']
    dict_['otherFinancingActivites'] = cf_.loc['otherFinancingActivites']
    # other
    dict_['netChangeInCash'] = cf_.loc['netChangeInCash']
    dict_['freeCashFlow'] = cf_.loc['freeCashFlow']

    ## Misc.
    dict_['stockPrice'] = ev_.loc['stockPrice']
    dict_['changeInStockholdersEquity'] = (dict_['netIncome'] - dict_['dividendsPaid']) + (dict_['commonStockIssued'] - dict_['commonStockRepurchased']) 
    dict_['marketCapitalization'] = dict_['sharesOutstanding'] * dict_['stockPrice']
    dict_['enterpriseValue'] = dict_['marketCapitalization'] + dict_['netDebt']
    dict_['ebit'] = dict_['ebitda'] - dict_['depreciationAndAmortization']
    dict_['workingCapital'] = dict_['totalCurrentAssets'] - dict_['totalCurrentLiabilities']
    dict_['investedCapital'] = dict_['totalAssets'] - dict_['totalDebt'] + dict_['netDebt']
    dict_['netOperatingProfitAfterTax'] = dict_['ebit'] - dict_['incomeTaxExpense']
    dict_['totalStockAndTotalDebt'] = dict_['totalStockholdersEquity'] + dict_['totalDebt']

    return dict_
    
if __name__ == '__main__':
    ticker = 'aapl'
    years = 5
    
    # is_, bs_, cf_, ev_ = getStatements(ticker, period='Y')

    # ratios = calculateRatios(ticker, period='Y')
    # metrics = getAllMetrics(ticker, period='Y')
    # trends = getTrendMetrics(ticker, years, period='Y')
    # gsummary, gdetails = getGrowthMetrics(ticker)

    # makeTrendPlot('aapl', 10, trend_name='stockequity', period='Y', path_='screen')
    # makeGrowthPlot(ticker, metric='roic', path_='screen')

    # finvals = getFinancialValues(ticker, period='Y')
    # ttmfinvals = getTTMFinancialValues(ticker)
    # _, ax = plt.subplots()
    # metric = 'revenue'
    # ax.plot(finvals[metric][0:years], color='blue', marker='o')
    # ax2 = ax.twiny()
    # ax2.plot(ttmfinvals[metric][0:years*4], color='orange', marker='o')
    # plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
    # ax.legend(['Y','ttm'])
    # plt.show()

    # print('Running libary checks with ticker: '+ticker) 
    # print(getGrowthMetrics(ticker))
    # print(getTrendMetrics(ticker, years))
    # computeMOS(ticker, onscreen=True)
    
    # check statements:
    # checkStatement(ticker)

    # update database:
    # updateStatement(ticker, period='Q')
    # updateSEC(ticker)
    # updateSECfromPath('example')

    # download data:
    # downloadStatements('sp500', period='Q')
    # downloadHistoricPrices('sp500')

    # web sec filing
    # getSECfiling('msft', '2021', '10K')

    # get historic price
    # sp500 index
    # idx = getHistoricPrice('sp500')
    # p = getHistoricPrice('msft')

    # compare plots
    ticker_list, field, years, period =['aapl','msft'], 'ni', 5, 'Y'
    comparePlots(ticker_list,field, years, period)

    # Valuation models
    # computeMOS(ticker, onscreen=True)
    # writeMOS('example')
    print('End of self-Check Script.')
