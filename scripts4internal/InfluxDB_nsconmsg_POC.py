# Obvious imports
# pip install influxdb-client --> Install the influxdb-client using pip
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import re
import time
import subprocess as sp
import pandas as pd

start_time = time.time()

# Define a list of valid counter values
newnslog_errors_latency = ["mem_tot_free_bm128"]

# Generate the filter conditions for each valid counter
filter_conditions = ' or '.join([f'r.counter == "{counter}"' for counter in newnslog_errors_latency])
linux_command = "ns 2ts " + " ".join(["-g " + item for item in newnslog_errors_latency]) + " var/nslog/newnslog*"

# Create a client instance
client = influxdb_client.InfluxDBClient(
    url='http://influx.deva.citrite.net:8086',
    token='f4DtBvmog-ubxhvqFiCUImLdwVVWP6dGh5W6SFiun1Wx6U0XBp4iIW0pvkqEeOQt7HvcT6jIzVUjnYWXDaPSsw==',
    org='netscaler'
)

# Set correct support bundle path
try:
    if (os.popen("pwd").read().index("collector") >= 0):
        os.chdir(re.search('.*\/collecto.*_[0-9]{2}', os.popen("pwd").read()).group(0))
except AttributeError as e:
    print("Collector Bundle not in Correct Naming Convention")
    os.chdir(re.search('.*\/collecto.*_[0-9|_|\-|a-zA-Z|\.]{1,30}', os.popen("pwd").read()).group(0))
except FileNotFoundError as e:
    print("Collector Bundle not in Correct Naming Convention")
    os.chdir(re.search('.*\/collecto.*_[0-9|_|\-|a-z|\.]{1,30}', os.popen("pwd").read()).group(0))
except ValueError:
    print("\nPlease navigate to correct support bundle path")
    print("Available directories with support bundle names: \n\n" + "\n".join(re.findall("collect.*", "\n".join(next(os.walk('.'))[1]))))

# Get the details to build a query
case_number = os.popen("pwd").read().split("/")[3]
bundle_nsip = sp.run("sed -n '/ns config/,/Done/p' shell/showcmds.txt | awk '/NetScaler IP/{printf $3;exit}'", shell=True, text=True, stderr=sp.PIPE, stdout=sp.PIPE).stdout

# Create the Flux query with the dynamic filter conditions
query_api = client.query_api()
def influx_query():
    # Build a query
    query = f'from(bucket:"nscounters")\
    |> range(start: -90d)\
    |> filter(fn:(r) => r._measurement == "dcurrent2")\
    |> filter(fn:(r) => r.case == "n{case_number}")\
    |> filter(fn:(r) => r.nsip == "{bundle_nsip}")\
    |> filter(fn:(r) => r._field == "value")\
    |> filter(fn:(r) => {filter_conditions})'
    return query_api.query(query=query)

newnslog_errors_latency_data = influx_query()

# Create a list to hold the records
data = []

# Populate the list with records
for table in newnslog_errors_latency_data:
    for record in table.records:
        data.append({
            '_time': record.values['_time'],
            'counter': record.values['counter'],
            '_value': record.values['_value']
        })

# Convert the list to a pandas DataFrame
df = pd.DataFrame(data)

# Ensure the timestamps are in a standard format
df['_time'] = pd.to_datetime(df['_time'])

# Print the DataFrame
print(df)

end_time = time.time()

elapsed_time = end_time - start_time
print(f'Time taken: {elapsed_time}')
