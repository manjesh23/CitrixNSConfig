from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger


api_key = '2NTuT7eC'
username = 'N55647959'
pwd = '2352'
smartApi = SmartConnect(api_key)


try:
    token = "BHYNPXL6JAY2XNQ7ZB64T22FQA"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
data = smartApi.generateSession(username, pwd, totp)

if data['status'] == False:
    logger.error(data)

else:
    # login api call
    # logger.info(f"You Credentials: {data}")
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    # fetch the feedtoken
    feedToken = smartApi.getfeedToken()
    # fetch User Profile
    res = smartApi.getProfile(refreshToken)
    smartApi.generateToken(refreshToken)
    res=res['data']['exchanges']

################# EOF #####################
    
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger
import websocket  # Import correct WebSocket library

AUTH_TOKEN = "BHYNPXL6JAY2XNQ7ZB64T22FQA"
API_KEY = "2NTuT7eC"
CLIENT_CODE = "N55647959"
FEED_TOKEN = smartApi.getfeedToken()
correlation_id = "abc123"
action = 1
mode = 1
token_list = [
    {
        "exchangeType": 1,
        "tokens": ["26000"]
    }
]
#retry_strategy=0 for simple retry mechanism
sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN,max_retry_attempt=2, retry_strategy=0, retry_delay=10, retry_duration=5)
def on_data(wsapp, message):
    logger.info("Ticks: {}".format(message))
    # close_connection()

def on_control_message(wsapp, message):
    logger.info(f"Control Message: {message}")

def on_open(wsapp):
    logger.info("on open")
    some_error_condition = False
    if some_error_condition:
        error_message = "Simulated error"
        if hasattr(wsapp, 'on_error'):
            wsapp.on_error("Custom Error Type", error_message)
    else:
        sws.subscribe(correlation_id, mode, token_list)
        # sws.unsubscribe(correlation_id, mode, token_list1)

def on_error(wsapp, error):
    logger.error(error)

def on_close(wsapp):
    logger.info("Close")

def close_connection():
    sws.close_connection()


# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close
sws.on_control_message = on_control_message

sws.connect()
####### Websocket V2 sample code ENDS Here #######

########################### SmartWebSocket OrderUpdate Sample Code Start Here ###########################
from SmartApi.smartWebSocketOrderUpdate import SmartWebSocketOrderUpdate
client = SmartWebSocketOrderUpdate(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
client.connect()
