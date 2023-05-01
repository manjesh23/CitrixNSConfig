# Import required modules
from thefirstock import thefirstock
import json
import time

# Login details
login = thefirstock.firstock_login(userId='JB1885', password='Cms#4567$',
                                   TOTP='18021985', vendorCode='JB1885_API', apiKey='e8166c98e3daf958972339af552f127e')

# Get user input details for trade
#strikeprice = str(input("Enter Strike Price: "))
#indexenter = int(input("Enter Index Entry value: "))
#target = int(input("Enter Index target value: "))
#stoploss = int(input("Enter Index stoploss value: "))
#putcall = str(input("Enter C / P: "))
#expirydate = str(input("Enter the Expiry Details DDMMMYY: "))
#optionname = int(input("26000 - Nitfy 50 | 26009 - Bank Nifty: "))

# Testing
buystrikeprice = '40000'
indexenter = 39480
target = 40000
stoploss = 38300
putcall = 'C'
expirydate = '13APR23'
optionname = 26009

# Logic home
if optionname == 26009:
    optionexpiryname = 'BANKNIFTY'+expirydate+putcall+buystrikeprice
elif optionname == 26000:
    optionexpiryname = 'NIFTY'+expirydate+putcall+buystrikeprice
else:
    print("Invalid Option Date")
    quit()
if login['status'] == 'Success':
    print("Login Successful")
    while True:
        time.sleep(1)
        index_ltp = int(float(thefirstock.firstock_getQuote(exchange='NSE',  token=optionname)[
            'data']['lastTradedPrice']))
        print(index_ltp)
        if index_ltp >= indexenter:
            print(optionexpiryname)
            strike_price = thefirstock.firstock_OptionChain(
                tradingSymbol=optionexpiryname, exchange='NFO', strikePrice=int(buystrikeprice), count="5")
            print(strike_price)
