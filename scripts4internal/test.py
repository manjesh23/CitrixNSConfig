import requests
import json

url = "http://10.14.91.111/nitro/v2/config/login"

payload = json.dumps({
  "login": {
    "username": "nsroot",
    "password": "vM@1234"
  }
})
headers = {
  'Accept': '*/*',
  'Accept-Encoding': 'gzip, deflate',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False)

print(response.text)