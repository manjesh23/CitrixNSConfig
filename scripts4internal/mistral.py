import requests
import json

# API endpoint
url = "http://10.110.7.9:11434/api/generate"

# Raw log data
raw_logs = """
19768    85 PPE-0 interface(25/4): EXPIRED              Thu Dec 19 22:18:43 2024
19769     0 PPE-0 interface(25/4): COLLECTING           Thu Dec 19 22:18:43 2024
19770     0 PPE-0 interface(25/4): ATTACHED             Thu Dec 19 22:18:43 2024
19771     0 PPE-0 'interface(25/4)' migrated            Thu Dec 19 22:18:43 2024
19776     0 PPE-0 interface(25/4): CURRENT              Thu Dec 19 22:18:44 2024
19777     0 PPE-0 interface(25/4): COLLECTING           Thu Dec 19 22:18:44 2024
19778     0 PPE-0 interface(25/4): DISTRIBUTING         Thu Dec 19 22:18:44 2024

19799     0 PPE-0 interface(25/3): EXPIRED              Thu Dec 19 22:18:49 2024
19800     0 PPE-0 interface(25/3): COLLECTING           Thu Dec 19 22:18:49 2024
19801     0 PPE-0 interface(25/3): ATTACHED             Thu Dec 19 22:18:49 2024
19802     0 PPE-0 'interface(25/3)' migrated            Thu Dec 19 22:18:49 2024
19803     0 PPE-0 interface(25/4): EXPIRED              Thu Dec 19 22:18:49 2024
19804     0 PPE-0 interface(25/4): COLLECTING           Thu Dec 19 22:18:49 2024
19805     0 PPE-0 interface(25/4): ATTACHED             Thu Dec 19 22:18:49 2024
19806     0 PPE-0 'interface(25/4)' migrated            Thu Dec 19 22:18:49 2024
19807     0 PPE-0 'interface(LA/2)' DOWN                Thu Dec 19 22:18:49 2024
19808     0 PPE-0 interface(25/3): CURRENT              Thu Dec 19 22:18:49 2024
19809     0 PPE-0 interface(25/3): COLLECTING           Thu Dec 19 22:18:49 2024
19810     0 PPE-0 interface(25/3): DISTRIBUTING         Thu Dec 19 22:18:49 2024
19811     0 PPE-0 interface(25/4): CURRENT              Thu Dec 19 22:18:49 2024
19812     0 PPE-0 interface(25/4): COLLECTING           Thu Dec 19 22:18:49 2024
19813     0 PPE-0 interface(25/4): DISTRIBUTING         Thu Dec 19 22:18:49 2024
19814     0 (PART-1) PPE-0 10474: DOWN                           Thu Dec 19 22:18:49 2024

19816     0 PPE-0 'interface(LA/2)' UP                  Thu Dec 19 22:18:50 2024

"""

# Prepare payload
payload = {
    "model": "mistral",
    "prompt": f"These are the NetScaler logs, summarize this:\n{raw_logs}"
}
headers = {"Content-Type": "application/json"}

# Send POST request
response = requests.post(url, json=payload, stream=True)

# Process the response
full_response = ""
for line in response.iter_lines():
    if line:
        data = line.decode("utf-8")
        try:
            json_data = json.loads(data)
            full_response += json_data.get("response", "")
        except json.JSONDecodeError:
            pass

# Print the summary
print("Summary:", full_response)
