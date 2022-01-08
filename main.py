print_condition = 0
def linreg(X, Y):  
    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in zip(X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    return (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det

def download_price_hist(sy):
    while True:
        try:
            hist = yf.Ticker(sy).history(period="1000d").reset_index()
            hist.drop(columns = ['Dividends','Stock Splits'],inplace = True)
            break
        except:
            print('Cannot get the data, retry again...')
    
    return hist

def bb(data, sma, window):
    std = data.rolling(window).std()
    upper_bb = sma+2*std
    lower_bb = sma-2*std
    return upper_bb, lower_bb

def getstocklist():
    stock_list = []
    table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = table[0]
    df = df['Symbol'].values.tolist()
    for sym in df:
        sym = sym.replace('.','-')
        stock_list.append(sym)
        no_stock = len(stock_list)
    #print('Get stock list successful, total {no_stock} stock in the list.'.format(**locals()))
    return stock_list

def clear_png(file_path):
    file = os.listdir(file_path)
    for f in file:
        extension = f.split(".")
        if extension[1] == 'png':
            os.remove(''.join([file_path,f]))
            
def check_trading(date):
    nyse = mcal.get_calendar('NYSE')
    early = nyse.schedule(start_date=date, end_date=date)
    early.reset_index(inplace = True)
    if len(early) == 1:
        return True
    else:
        return False
    
    

today_date = date.today().strftime('%d-%m-%y')
clear_png('/kaggle/working/')

up=[]
down=[]
sma200_list = []
all_true = []
not_all = []
all_ture_count = 0
not_all_count =0
ref_index = download_price_hist('^gspc')
running_stock = 0
stock_list = getstocklist()

def check_conditions(stock_sy):
    print('Getting stock: {stock_sy}'.format(**locals()))
    hist = download_price_hist(stock_sy)
    sma50 = hist['Close'][-50:].mean()
    sma150 = hist['Close'][-150:].mean()
    sma200 = hist['Close'][-200:].mean()
    week52_high = hist['Close'].max()
    week52_low = hist['Close'].min()
    sma_range = [20,50,100,120,200]
    for sma in sma_range:
        hist['sma'+str(sma)] = round(hist['Close'].rolling(window = sma).mean(),2)

    last_close = hist.iloc[-2,4]
    close_at = round(hist.iloc[-1,4],2)
    up_down = last_close - close_at
    hist['gspc_close'] = ref_index['Close']
    hist['close_ratio'] = hist['Close']/hist['gspc_close']
    if (close_at > sma150) & (sma150>sma200): #close > 150 and close > 200
        condition1 = 'True'
    else:
        condition1 = 'False'
    if(sma50>sma200): # sma50>sma200
        condition2 = 'True'
    else:
        condition2 = 'False'
    sma200_list = hist['sma200'][-30:].tolist()
    a,b = linreg(range(len(sma200_list)),sma200_list)
    if (a > 0): #sma200 trending up
        condition3 = 'True'
    else:
        condition3 = 'False'
    if (sma50 > sma150) & (sma50 > sma200): #sma50 > sma150 and sma50 > sma200
        condition4 = 'True'
    else:
        condition4 = 'False'
    if(close_at>sma50): # close > sma50
        condition5 = 'True'
    else:
        condition5 = 'False'
    if close_at>1.4*week52_low: #close at 1.4 52low
        condition6 = 'True'
    else:
        condition6 = 'False'
    if close_at > 0.75*week52_high: # close at 0.75 52high
        condition7 = 'True'
    else: 
        condition7 = 'False'
    volume = hist.iloc[-1,5].astype(float)
    if  float(volume) > 1000000.00: # volumn > 1.0m
        condition8 = 'True'
    else:
        condition8 = 'False'
    if close_at > 10: #current price >10
        condition9 = 'True'
    else:
        condition9='False'
        
    hist['last_close'] = hist['Close'].shift(1)
    hist['diff_close'] = hist['Close']-hist['last_close']
    hist['UP'] = round(hist['diff_close'].apply(lambda x: x if x> 0  else 0),200)
    hist['DOWN'] = round(hist['diff_close'].apply(lambda x: abs(x) if x< 0  else 0),200)
    hist['EMA_U'] = hist['UP'].ewm(span = 14).mean()
    hist['EMA_D'] = hist['DOWN'].ewm(span = 14).mean()
    hist['RS'] = hist['EMA_U']/ hist['EMA_D']
    hist['RSI'] = 100-(100/(1+hist['RS']))
    rsi = round(hist.iloc[-1,hist.columns.get_loc('RSI')],2)

    if (float(rsi) >  30) & (float(rsi) < 70): #30<rsi<70
        condition10='True'
    else:
        condition10="False"

    last_10_low = hist['Low'][-10:].min()
    last_10_high = hist['High'][-10:].max()
    range_10= last_10_high - last_10_low
    last_close_008 = hist.iloc[-1,hist.columns.get_loc('Close')]*0.08
    if range_10 <=last_close_008:
        condition11 = 'True'
    else:
        condition11 = 'False'
    hist['upper_bb'], hist['lower_bb'] =bb(hist['Close'], hist['sma20'], 20)
    
    print('Ticket: {stock_sy}, close at {close_at}, RSI {rsi}'.format(**locals()))
    isprint =0
    if isprint == 1:
        #print('Number of stock: {running_stock}, Total Stock: {no_stock}'.format(**locals()))
        print('Condition1: {condition1}, close > 150 and close > 200, sma150 = {sma150}, sma200 = {sma200}'.format(**locals()))
        print('Condition2: {condition2}, sma50>sma200,sma50: {sma50}, sma200: {sma200}'.format(**locals()))
        print('Condition3: {condition3}, sma200 trending up, the slope of sma200 = {a}'.format(**locals()))
        print('Condition4: {condition4}, sma50 > sma150 and sma50 > sma200,sma50: {sma50},sma150: {sma150}, sma200: {sma200}'.format(**locals()))
        print('Condition5: {condition5}, close > sma50,sma50: {sma50}'.format(**locals()))
        print('Condition6: {condition6}, 52 week low = {week52_low}'.format(**locals()))
        print('Condition7: {condition7}, 52 week high = {week52_high}'.format(**locals()))
        print('Condition8: {condition8}, volumme = {volume}'.format(**locals()))
        print('Conidtion9: {condition9}, close at {close_at}'.format(**locals()))
        print('Condition10: {condition10}, rsi at {rsi}'.format(**locals()))
        print('Condition11: {condition11}, {range_10} and {last_close_008}'.format(**locals()))
        print('')
        print('')
        print('\t\t\t-----------END-----------\t\t\t')
        print('')
        print('')

    if condition1 == condition2 == condition3 == condition4 == condition5 == condition6 == condition7 == condition8 == condition9 == condition10 == 'True':
        all_true.append(stock_sy)
        plot_data =hist
        for i in range(6,19):
            plot_data =plot_data.drop(hist.columns[i], axis = 1)
        plot_data.set_index('Date', inplace = True)
        plot_data
        s = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.size': 6})
        apds = mpf.make_addplot((hist['close_ratio'][-90:]), panel = 1, color = 'b')
        filename = str(stock_sy) + ' stock chart get from '+ today_date+ '.png'
        mpf.plot(plot_data[-90:], type='candlestick',addplot= apds, style='yahoo',title=str(stock_sy) + ' stock chart', volume = True,  figscale = 1.5,savefig=filename)
        
        return True
    else:
        not_all.append(stock_sy)
        
        return False
    
if __name__ == "__main__":
    time1 = datetime.now()
    today_us = (datetime.today() - timedelta(days =1)).strftime("%Y-%m-%d")
    if check_trading(today_us) ==True:
        issendtg = True
        all_true = []
        not_all = []
        stock_list = getstocklist()
        for stock in stock_list:
            check_conditions(stock)
        count_all_true = len(all_true)
        count_not_true = len(not_all)
        print('The stock that is meet all requirement: {all_true}'.format(**locals()))
        print('')
        print('')
        print('The stock that is not meet all requirement: {not_all}'.format(**locals()))
        print('')
        print('')
        print('There are {count_all_true} stock are strong and {count_not_true} stocks are not all condition match.'.format(**locals()))
        
    else:
        issendtg = False
    
    time2 = datetime.now()
    print(str(time2-time1))
