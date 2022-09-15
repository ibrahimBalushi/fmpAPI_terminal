from processor import *

# TERMINAL API functions -------------------------------------------------------------------------------------------------------------------
def getTrendTable(ticker, trend_name, years, period, pretty=True):
    trends = getTrendMetrics(ticker, years, period)
    if pretty:
        # income
        trends['income'] = (trends['income'] * 1e6).apply(lambda x: fl2str(x))
        # liability
        liability = trends['liability'].drop(['Debt-Enterprise','Debt Coverage'],axis=0).apply(lambda x: fl2str(x))
        trends['liability'].loc['EV'] = liability.loc['EV']
        trends['liability'].loc['Net Debt'] = liability.loc['Net Debt']
        # stockequity
        equity = (trends['stockequity'].drop(['sharesOut'],axis=0) * 1e6).apply(lambda x: fl2str(x))
        sharesOut = trends['stockequity'].loc[['sharesOut']].apply(lambda x: fl2str(x))
        trends['stockequity'].loc['sharesOut'] = sharesOut.loc['sharesOut']
        trends['stockequity'].loc['marketCap'] = equity.loc['marketCap']
        trends['stockequity'].loc['equity'] = equity.loc['equity']
        # investment
        trends['investment'] = (trends['investment'] * 1e6).apply(lambda x: fl2str(x))

    print(trends[trend_name])

    return trends

def maketrend(path_, metric, years ,period):
    ticker_list = getTickerList('charts/'+str(path_))
    for tkr in ticker_list:
    # produce tables and plots
        print('processing',tkr)
        if metric != 'all':
            makeTrendPlot(tkr, int(years), str(metric), period, path_)
        else:
            for tn in ['income', 'stockequity', 'liability', 'margins', 'investment', 'valuation']:
                makeTrendPlot(tkr, int(years), tn, period, path_)

def makegrowth(path_, metric):
    ticker_list = getTickerList('charts/'+str(path_))
    for tkr in ticker_list:
    # produce tables and plots
        print('processing',tkr)
        if metric != 'all':
            makeGrowthPlot(tkr, str(metric), path_)
        else:
            for tn in ['roic','equity','eps','revenue','cash','price']:
                makeGrowthPlot(tkr, tn, path_)
        
def makemos(path_, metric, years):
    writeMOS(str(path_))

def makecompare(ticker_list, field, years, period, list_type):
    if list_type == '-l':
        ticker_list = getTickerList('charts/'+ticker_list[0])
    tkrs = []
    for l in ticker_list:
        tkrs.append(str(l))   
    
    comparePlots(tkrs, field, int(years), period)

def openCompaniesmarketcap(sector):
    file = open('help/sectors.txt','r')
    content = file.readlines()
    if sector == 'list':
        for l in content:
            print(l)
    else:
        wb.open('https://companiesmarketcap.com/'+str(sector)+'/largest-'+str(sector)+'-companies-by-market-cap/')

def getSECfiling(ticker, year, filing):
    period = {'10K':'Y', 'Q1':'Q', 'Q2':'Q', 'Q3':'Q', 'Q4':'Q'}
    is_, _, _, _ = getStatements(ticker, period[filing])
    
    # update year in case of quarter filing
    if filing != '10K':
        year =  year[2::]+filing

    print(is_[year]['link'])
    wb.open(is_[year]['link'])

def prompt(var, run_):
    
    if var[0] == 'exit':
        run_ = False
    else:
            
        # PRINT commands:
        trendtable ='print(getTrendTable(var[1], var[2], int(var[4]), var[5])[var[2]])'
        growthtable = 'print(getGrowthMetrics(var[1])[0])'
        growthdetail = 'print(getGrowthMetrics(var[1])[1])'
        mostable = 'print(computeMOS(var[1]))'
        trendchart = 'makeTrendPlot(var[1], int(var[4]), var[2], var[5])'
        growthchart = 'makeGrowthPlot(var[1], var[2][:-6])'
        roicchart = 'makeGrowthPlot(var[1], var[2])'
        statementstable = 'printStatements(var[1], var[4])'
        print_dict = {'table':{'income':trendtable, 'stockequity':trendtable, 'liability':trendtable, 'margins':trendtable, 'investment':trendtable,'valuation':trendtable,'growth':growthtable, 'growthdetail':growthdetail, 'mos':mostable, 'statements':statementstable}, 'chart':{'income':trendchart, 'stockequity':trendchart, 'liability':trendchart, 'margins':trendchart, 'investment':trendchart,'valuation':trendchart,'roic':roicchart,'equitygrowth':growthchart,'epsgrowth':growthchart,'revenuegrowth':growthchart,'cashgrowth':growthchart,'pricegrowth':growthchart}}

        # MAKE commands:
        call_maketrend = 'maketrend(var[1], var[2], int(var[3]), var[4])'
        call_makegrowth = 'makegrowth(var[1], var[2][:-6])'
        call_makeroic = 'makegrowth(var[1], var[2])'
        call_makealltrends = 'maketrend(var[1], '+'"all"'+', int(var[3]), var[4])'
        call_makeallgrowth = 'makegrowth(var[1], '+'"all"'+')'
        call_makemos = 'writeMOS(var[1])'
        make_dict = {'income':call_maketrend, 'stockequity':call_maketrend, 'liability':call_maketrend, 'margins':call_maketrend, 'investment':call_maketrend,'valuation':call_maketrend,'roic':call_makeroic,'equitygrowth':call_makegrowth,'epsgrowth':call_makegrowth,'revenuegrowth':call_makegrowth,'cashgrowth':call_makegrowth,'pricegrowth':call_makegrowth,'alltrends':call_makealltrends,'allgrowth':call_makeallgrowth,'mos':call_makemos}

        # COMPARE command:[compare, revenue, 10, Q, aapl, msft]
        call_compare = 'makecompare(var[5::], var[1], var[2], var[3], var[4])'

        # GET commands:
        call_download = 'downloadStatements(var[1])'
        get_dict = {'statements':call_download}

        # CHECK database commands:
        call_checkStatements = 'checkStatement(var[1])'
        call_checkListStatements = 'checkListStatements(var[1])'
        check_dict = {'-t':call_checkStatements,'-l':call_checkListStatements}

        # UPDATE database commands
        call_updateStatements = 'updateStatements(var[1],var[3])'
        call_updateStatementsfromList = 'updateStatementsfromList(var[1],var[3])'
        update_dict = {'-t':call_updateStatements, '-l':call_updateStatementsfromList}

        # WEB commands
        call_insider = 'wb.open("https://www.nasdaq.com/market-activity/stocks/"+str(var[2])+"/insider-activity")'
        call_sector = 'openCompaniesmarketcap(str(var[2]))'
        call_holdings = 'wb.open("https://www.nasdaq.com/market-activity/stocks/"+str(var[2])+"/institutional-holdings")'
        call_analyst = 'wb.open("https://finance.yahoo.com/quote/"+str(var[2]).upper()+"/analysis?p="+str(var[2]).upper())'
        call_sec ='getSECfiling(var[2], var[3], var[4])'
        web_dict = {'insider':call_insider, 'sector':call_sector,'holdings':call_holdings,'analyst':call_analyst, 'sec':call_sec}

        # help lists
        call_commands_list = 'os.system("cat help/commands.txt")'
        call_compare_list = 'os.system("cat help/compare.txt")'
        call_sector_list = 'os.system("cat help/sectors.txt")'
        list_dict = {'commands':call_commands_list, 'compare':call_compare_list, 'sectors':call_sector_list}

        # # execute command line:
        cmdln = {'print': 'print_dict[var[3]][var[2]]', 'make':'make_dict[var[2]]', 'compare':'call_compare', 'get':'get_dict[var[2]]','update':'update_dict[var[2]]', 'check':'check_dict[var[2]]','web':'web_dict[var[1]]','list':'list_dict[var[1]]'}
        eval(eval(cmdln[var[0]]))

        return run_

if __name__ == '__main__':
    # TERMINAL INITIATION
    run_ = True
    while run_ == True:
        try:
            # input commandline arguments  
            var = input('fmpAPI terminal$ ').split()
            run_ = prompt(var, run_)
                
        except Exception as e: print(e)