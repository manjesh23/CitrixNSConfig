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
#putcall = str(input("Enter C / P: "))
#expirydate = str(input("Enter the Expiry Details DDMMMYY: "))
#optionname = int(input("26000 - Nitfy 50 | 26009 - Bank Nifty: "))
#quantity = int(input("Enter actual quantity: "))

# Testing
#buystrikeprice = '17200'
#indexenter = 18200
#target = 18200
#stoploss = 18300
putcall = 'P'
expirydate = '01JUN23'
optionname = 26000
quantity = 50

# Logic home
if optionname == 26009:
    optionexpiryname = 'BANKNIFTY'+expirydate+putcall+buystrikeprice
elif optionname == 26000:
    optionexpiryname = 'NIFTY'+expirydate+putcall+buystrikeprice
    print(optionexpiryname)

else:
    print("Invalid Option Date")
    quit()
if login['status'] == 'Success':
    print("Login Successful")
    PB = thefirstock.firstock_PositionBook()

# Logic home
def quantity_check_PB():
    all_PB_quantity = []
    for i in PB['data']:
        all_PB_quantity.append((i['tradingSymbol'], i['netQuantity']))
    print(all_PB_quantity)
    if int(PB['data'][0]['netQuantity']) == quantity:
        print("Quantity check matched")
        return True
    else:
         print("Quantity check match failed")
         return False

def name_check_PB():
    all_PB_name = []
    for i in PB['data']:
        all_PB_name.append(i['tradingSymbol'])
    for index, symbol in enumerate(all_PB_name):
        if symbol == optionexpiryname:
            print(f"Match found at index {index}")
            return True
    else:
        print("No match found")
        return False

def call_option():
    while True:
        time.sleep(2)
        index_ltp = int(float(thefirstock.firstock_getQuote(exchange='NSE',  token=optionname)['data']['lastTradedPrice']))
        if index_ltp <= indexenter:
            print("Index_LTP is less than or equal to (" + str(index_ltp) + ")" + " index entry price (" + str(indexenter) + ")")
            placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='', product='I', transactionType='B', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
            print("Buy Trade executed at " + str(index_ltp))
            print(placeOrder)
            if placeOrder['status'] == "Success":
                while True:
                    time.sleep(2)
                    index_ltp = int(float(thefirstock.firstock_getQuote(exchange='NSE',  token=optionname)['data']['lastTradedPrice']))
                    print("Index LTP: " + str(index_ltp) + " Index entry: " + str(indexenter))
                    if index_ltp >= target:
                        placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='', product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
                        print("You have achieved your target !!!")
                        quit()
                    elif index_ltp <= stoploss:
                        placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='', product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
                        print("You have hit the stoploss :(")
                        quit()
            else:
                print("Market is not touched your entry point")
def put_option():
    while True:
        time.sleep(2)
        print("I came here as well")        
        index_ltp = int(float(thefirstock.firstock_getQuote(exchange='NSE',  token=optionname)['data']['lastTradedPrice']))
        if index_ltp >= indexenter:
            print("Index_LTP is less than or equal to (" + str(index_ltp) + ")" + " index entry price (" + str(indexenter) + ")")
            placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='', product='I', transactionType='B', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
            print("Buy Trade executed at " + str(index_ltp))
            print(placeOrder)
            if placeOrder['status'] == "Success":
                while True:
                    time.sleep(2)
                    index_ltp = int(float(thefirstock.firstock_getQuote(exchange='NSE',  token=optionname)['data']['lastTradedPrice']))
                    print("Index LTP: " + str(index_ltp) + " Index entry: " + str(indexenter))
                    if index_ltp <= target:
                        placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='', product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
                        print("You have achieved your target !!!")
                        quit()
                    elif index_ltp >= stoploss:
                        placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='', product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
                        print("You have hit the stoploss :(")
                        quit()
            else:
                print("Market is not touched your entry point")
while True:
    time.sleep(1)
    index_ltp = int(float(thefirstock.firstock_getQuote(exchange='NSE',  token=optionname)['data']['lastTradedPrice']))
    print(index_ltp)
    if name_check_PB() and quantity_check_PB():
        if index_ltp <= target:
            placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='',product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
            print("You have achieved your target !!!")
            quit()
        elif index_ltp >= stoploss:
            placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='', product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
            print("You have hit the stoploss :(")
            print(placeOrder)
            quit()
    else:
        print("I am in PUTCALL")
        if putcall == 'C':
            call_option()
            print("I am in CALL")
            if index_ltp >= target:
                placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='',product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
                print("You have achieved your target !!!")
                quit()
            elif index_ltp <= stoploss:
                placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='', product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
                print("You have hit the stoploss :(")
                quit()
        elif putcall == 'P':
            put_option()
            print("I am in PUT")
            if index_ltp <= target:
                    placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='',product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
                    print("You have achieved your target !!!")
                    quit()
            elif index_ltp >= stoploss:
                placeOrder = thefirstock.firstock_placeOrder(exchange='NFO', tradingSymbol=optionexpiryname, quantity=quantity, price='', product='I', transactionType='S', priceType='MKT', retention='DAY', triggerPrice=0, remarks='Strategy1',)
                print("You have hit the stoploss :(")
                quit()