# Import required modules
from thefirstock import thefirstock
import json
import time

# Login details
login = thefirstock.firstock_login(userId='JB1885', password='Cms#4567$',
                                   TOTP='18021985', vendorCode='JB1885_API', apiKey='e8166c98e3daf958972339af552f127e')

# Get user input details for trade
buystrikeprice = str(input("Enter Strike Price: "))
indexenter = int(input("Enter Index Entry value: "))
target = int(input("Enter Index target value: "))
stoploss = int(input("Enter Index stoploss value: "))
putcall = str(input("Enter C / P: "))
expirydate = str(input("Enter the Expiry Details DDMMMYY: "))
optionname = int(input("26000 - Nitfy 50 | 26009 - Bank Nifty: "))
quantity = int(input("Enter actual quantity: "))

# Testing
#buystrikeprice = '17500'
#indexenter = 18200
#target = 18200
#stoploss = 18300
#putcall = 'C'
#expirydate = '11MAY23'
#optionname = 26000
#quantity = 500

# Logic home
if optionname == 26009:
    optionexpiryname = 'BANKNIFTY'+expirydate+putcall+buystrikeprice
    print(optionexpiryname)
elif optionname == 26000:
    optionexpiryname = 'NIFTY'+expirydate+putcall+buystrikeprice
else:
    print("Invalid Option Date")
    quit()
if login['status'] == 'Success':
    print("Login Successful")
    PB = thefirstock.firstock_PositionBook()
    while True:
        time.sleep(1)
        index_ltp = int(float(thefirstock.firstock_getQuote(exchange='NSE',  token=optionname)[
            'data']['lastTradedPrice']))
        print(index_ltp)
        # if str(PB['data'][0]['tradingSymbol']) = str(optionexpiryname):
        if int(PB['data'][0]['netQuantity']) != quantity:
            # Treat this a new trade
            if putcall == "C":
                # This is a Call option logic
                if index_ltp <= indexenter:
                    print("Index_LTP is less than or equal to (" + str(index_ltp) + ")" +
                          " index entry price (" + str(indexenter) + ")")
                    strike_price = thefirstock.firstock_OptionChain(
                        tradingSymbol=optionexpiryname, exchange='NFO', strikePrice=int(buystrikeprice), count="5")
                    placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='',
                                                                 product='C', transactionType='B', priceType='MKT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                    print("Buy Trade executed at " + str(index_ltp))
                    print(placeOrder)
                    if placeOrder['status'] == "Success":
                        oB = thefirstock.firstock_orderBook()  # This order book is for future use
                        while True:
                            if PB['data'][0]['tradingSymbol'] == optionexpiryname:
                                if index_ltp >= target:
                                    placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='MKT',
                                                                                 product='C', transactionType='S', priceType='LMT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                                    print("You have achieved your target !!!")
                                    quit()
                                elif index_ltp <= stoploss:
                                    placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='MKT',
                                                                                 product='C', transactionType='S', priceType='LMT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                                    print("You have hit the stoploss :(")
                                    quit()
                            else:
                                print(
                                    "You do not have any option position with the name " + optionexpiryname)
                                quit()
                    else:
                        print("Market is not touched your entry point")
            elif putcall == 'P':
                # This is a Put option logic
                if index_ltp >= indexenter:
                    print("Index_LTP is less than or equal to (" + str(index_ltp) + ")" +
                          " index entry price (" + str(indexenter) + ")")
                    strike_price = thefirstock.firstock_OptionChain(
                        tradingSymbol=optionexpiryname, exchange='NFO', strikePrice=int(buystrikeprice), count="5")
                    placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='',
                                                                 product='C', transactionType='B', priceType='MKT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                    print("Buy Trade executed at " + str(index_ltp))
                    if placeOrder['status'] == "Success":
                        oB = thefirstock.firstock_orderBook()  # This order book is for future use
                        while True:
                            if PB['data'][0]['tradingSymbol'] == optionexpiryname:
                                if index_ltp <= target:
                                    placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='MKT',
                                                                                 product='C', transactionType='S', priceType='LMT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                                    print("You have achieved your target !!!")
                                    quit()
                                elif index_ltp >= stoploss:
                                    placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='MKT',
                                                                                 product='C', transactionType='S', priceType='LMT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                                    print("You have hit the stoploss :(")
                                    quit()
                            else:
                                print(
                                    "You do not have any option position with the name " + optionexpiryname)
                                quit()
                    else:
                        print("Market is not touched your entry point")
        else:
            # This is a existing trade
            while True:
                if putcall == "C":
                    if PB['data'][0]['tradingSymbol'] == optionexpiryname:
                        if index_ltp >= target:
                            placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='MKT',
                                                                         product='C', transactionType='S', priceType='LMT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                            print("You have achieved your target !!!")
                            print("This is not a new trade")
                            quit()
                        elif index_ltp <= stoploss:
                            placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='MKT',
                                                                         product='C', transactionType='S', priceType='LMT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                            print("You have hit the stoploss :(")
                            quit()
                        else:
                            quit()
                    else:
                        print(
                            "Invalid option exiry name matched with position book name")
                        quit()
                elif putcall == 'P':
                    if PB['data'][0]['tradingSymbol'] == optionexpiryname:
                        if index_ltp <= target:
                            placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='MKT',
                                                                         product='C', transactionType='S', priceType='LMT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                            print("You have achieved your target !!!")
                            print("This is not a new trade")
                            quit()
                        elif index_ltp >= stoploss:
                            placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='MKT',
                                                                         product='C', transactionType='S', priceType='LMT', retention='DAY', triggerPrice='', remarks='Strategy1',)
                            print("You have hit the stoploss :(")
                            quit()
                        else:
                            quit()
                    else:
                        print(
                            "Invalid option exiry name matched with position book name")
                        quit()
