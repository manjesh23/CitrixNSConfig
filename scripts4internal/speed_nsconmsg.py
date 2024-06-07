import pandas as pd
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os, re
import subprocess as sp
from dateutil import parser

# Set pandas to show full rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Set correct support bundle path
try:
    pwd_output = os.popen("pwd").read()
    if "collector" in pwd_output:
        os.chdir(re.search('.*\/collector.*_[0-9]{2}', pwd_output).group(0))
except (AttributeError, FileNotFoundError, ValueError) as e:
    print("Collector Bundle not in Correct Naming Convention")
    print("\nPlease navigate to the correct support bundle path")
    print("Available directories with support bundle names: \n\n" + "\n".join(re.findall("collect.*", "\n".join(next(os.walk('.'))[1]))))

# Get the details to build a query
case_number = pwd_output.split("/")[3]
bundle_nsip = sp.run("sed -n '/ns config/,/Done/p' shell/showcmds.txt | awk '/NetScaler IP/{printf $3;exit}'", shell=True, text=True, stderr=sp.PIPE, stdout=sp.PIPE).stdout.strip()

# Create a client instance
client = influxdb_client.InfluxDBClient(
   url='http://influx.deva.citrite.net:8086',
   token='f4DtBvmog-ubxhvqFiCUImLdwVVWP6dGh5W6SFiun1Wx6U0XBp4iIW0pvkqEeOQt7HvcT6jIzVUjnYWXDaPSsw==',
   org='netscaler'
)

# Create the Flux query with the dynamic filter conditions
query_api = client.query_api()
def influx_query(cname):
    # Build a query
    filter_conditions = ' or '.join([f'r.counter == "{counter}"' for counter in cname])
    query = f'from(bucket:"nscounters")\
    |> range(start: -90d)\
    |> filter(fn:(r) => r._measurement == "dcurrent2")\
    |> filter(fn:(r) => r.case == "n{case_number}")\
    |> filter(fn:(r) => r.nsip == "{bundle_nsip}")\
    |> filter(fn:(r) => r._field == "value")\
    |> filter(fn:(r) => {filter_conditions})'
    return query_api.query(query=query)

def get_all(cname = []):
    records_list = []
    influx_out = influx_query(cname)
    for table in influx_out:
        for record in table.records:
            record_dict = {
                '_value': float(record.values['_value']),
                'counter': record.values['counter'],
                '_time': pd.to_datetime(record.values['_time'])
            }
            records_list.append(record_dict)
    df = pd.DataFrame(records_list)
    df = df.sort_values(by='_time').drop_duplicates()
    return df

def get_counter(stime=None, etime=None, cname=[], newnslog=''):
    try:
        # Get start and end times using nsconmsg command
        nsconmsg_output = sp.run("nsconmsg -K var/nslog/"+newnslog+" -d setime | awk '!/Displaying/&&/time/{$1=$2=\"\"; print}'", shell=True, text=True, stdout=sp.PIPE)
        start_end_times = nsconmsg_output.stdout.split('\n')
        if len(start_end_times) < 2:
            print("Error: nsconmsg output does not contain expected start and end times.")
            return pd.DataFrame()
        stime = start_end_times[0].strip() if stime is None else stime
        etime = start_end_times[1].strip() if etime is None else etime
        stime = pd.to_datetime(parser.parse(stime))
        etime = pd.to_datetime(parser.parse(etime))
        records_list = []
        influx_out = influx_query(cname)
        for table in influx_out:
            for record in table.records:
                record_dict = {
                    '_value': float(record.values['_value']),
                    'counter': record.values['counter'],
                    '_time': pd.to_datetime(record.values['_time'])
                }
                records_list.append(record_dict)
        df = pd.DataFrame(records_list).drop_duplicates()
        df['_time'] = pd.to_datetime(df['_time'])
        # Ensure both stime and etime are timezone-aware
        if stime.tzinfo is None:
            stime = stime.tz_localize('UTC')
        if etime.tzinfo is None:
            etime = etime.tz_localize('UTC')
        df = df[(df['_time'] >= stime) & (df['_time'] <= etime)]
        return df
    except Exception as e:
        print(f"Error in get_counter: {e}")
        return pd.DataFrame()

def get_min(cname=[]):
    records_list = []
    influx_out = influx_query(cname)
    for table in influx_out:
        for record in table.records:
            record_dict = {
                '_value': float(record.values['_value']),
                'counter': record.values['counter'],
                '_time': pd.to_datetime(record.values['_time'])
            }
            records_list.append(record_dict)
    df = pd.DataFrame(records_list)
    df['_time'] = pd.to_datetime(df['_time'])
    df = df.sort_values(by='_time')
    min_rows = []
    for counter in df['counter'].unique():
        counter_df = df[df['counter'] == counter]
        min_row = counter_df.loc[counter_df['_value'].idxmin()]
        min_rows.append(min_row)
    return pd.DataFrame(min_rows)

def get_max(cname=[]):
    records_list = []
    influx_out = influx_query(cname)
    for table in influx_out:
        for record in table.records:
            record_dict = {
                '_value': float(record.values['_value']),
                'counter': record.values['counter'],
                '_time': pd.to_datetime(record.values['_time'])
            }
            records_list.append(record_dict)
    df = pd.DataFrame(records_list)
    df['_time'] = pd.to_datetime(df['_time'])
    df = df.sort_values(by='_time')
    max_rows = []
    for counter in df['counter'].unique():
        counter_df = df[df['counter'] == counter]
        max_row = counter_df.loc[counter_df['_value'].idxmax()]
        max_rows.append(max_row)
    return pd.DataFrame(max_rows)

