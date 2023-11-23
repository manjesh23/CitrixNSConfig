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
    '''
    get_all function helps to get all the values matching the case number and the NSIP for a given list of counters
    -- cname  --> nsconmsg -g Counter name
    
    Note: Data returned is in string format
    
    print(get_all(['mem_tot_alloc_bm16384', 'mem_tot_alloc_bm32']))
    '''
    records_list = []
    influx_out = influx_query(cname)
    for table in influx_out:
        for record in table.records:
            record_dict = {
                '_value': str(record.values['_value']),
                'counter': record.values['counter'],
                '_time': pd.to_datetime(record.values['_time']).strftime('%a %b %d %H:%M:%S %Y')
            }
            records_list.append(record_dict)
    # Create a DataFrame and sort by the '_time' column
    df = pd.DataFrame(records_list)
    df['_time'] = pd.to_datetime(df['_time'])
    df = df.sort_values(by='_time')
    # Convert the '_time' column back to the original timestamp format
    df['_time'] = df['_time'].dt.strftime('%a %b %d %H:%M:%S %Y')
    return df.drop_duplicates().to_string(index=False, header=False)

def get_counter(stime=None, etime=None, cname=[], newnslog=''):
    '''
    get_counter function helps to get all the values matching the case number and the NSIP and the newnslog name for a given list of counters
    -- cname  --> nsconmsg -g Counter name
    -- newnslog --> Name of the newnslog for which a specific timerange values needs to be returned
    
    Note: Data returned is in string format
    
    print(get_counter(cname=['mem_tot_alloc_bm16384', 'mem_tot_alloc_bm32'], newnslog='newnslog'))
    '''
    try:
        # Get start and end times using nsconmsg command
        nsconmsg_output = sp.run("nsconmsg -K var/nslog/"+newnslog+" -d setime | awk '!/Displaying/&&/time/{$1=$2=\"\"; print}'", shell=True, text=True, stdout=sp.PIPE)
        start_end_times = nsconmsg_output.stdout.split('\n')
        if len(start_end_times) < 2:
            print("Error: nsconmsg output does not contain expected start and end times.")
            return pd.DataFrame()
        stime = start_end_times[0].strip() if stime is None else stime
        etime = start_end_times[1].strip() if etime is None else etime
        records_list = []
        influx_out = influx_query(cname)
        for table in influx_out:
            for record in table.records:
                record_dict = {
                    '_value': str(record.values['_value']),
                    'counter': record.values['counter'],
                    '_time': pd.to_datetime(record.values['_time']).strftime('%a %b %d %H:%M:%S %Y')
                }
                records_list.append(record_dict)
        # Create a DataFrame without sorting
        df = pd.DataFrame(records_list).drop_duplicates()
        df['_time'] = pd.to_datetime(df['_time'])
        if stime is not None:
            stime = parser.parse(stime)
            df = df[df['_time'] >= stime]
        if etime is not None:
            etime = parser.parse(etime)
            df = df[df['_time'] <= etime]
        # Convert the '_time' column back to the original timestamp format
        df['_time'] = df['_time'].dt.strftime('%a %b %d %H:%M:%S %Y')
        return df.to_string(index=False, header=False)
    except Exception as e:
        print(f"Error in get_counter: {e}")
        return pd.DataFrame().to_string(index=False, header=False)

def get_min(cname=[]):
    '''
    get_min function helps to get min value and timestamp for all the values matching case number and NSIP
    -- cname  --> nsconmsg -g Counter name

    Note: Data returned is in string format
    
    min_rows = get_min(cname=['mem_tot_alloc_bm16384', 'mem_tot_alloc_bm32'])
    for item in min_rows:
        print(f"{item['min_row']}")
    '''
    records_list = []
    influx_out = influx_query(cname)
    for table in influx_out:
        for record in table.records:
            record_dict = {
                '_value': float(record.values['_value']),
                'counter': record.values['counter'],
                '_time': pd.to_datetime(record.values['_time']).strftime('%a %b %d %H:%M:%S %Y')
            }
            records_list.append(record_dict)
    # Create a DataFrame and sort by the '_time' column
    df = pd.DataFrame(records_list)
    df['_time'] = pd.to_datetime(df['_time'])
    df = df.sort_values(by='_time')
    # Convert the '_time' column back to the original timestamp format
    df['_time'] = df['_time'].dt.strftime('%a %b %d %H:%M:%S %Y')
    min_rows = []
    for counter in df['counter'].unique():
        # Filter DataFrame for each counter
        counter_df = df[df['counter'] == counter]
        # Get the row corresponding to the minimum value of '_value' column
        min_row = counter_df.loc[counter_df['_value'].idxmin()]
        # Format the row as a string
        min_row_str = f"{min_row['_value']} {min_row['counter']} {min_row['_time']}"
        min_rows.append({'counter': counter, 'min_row': min_row_str})
    return min_rows

def get_max(cname=[]):
    '''
    get_max function helps to get max value and timestamp for all the values matching case number and NSIP
    -- cname  --> nsconmsg -g Counter name

    Note: Data returned is in string format
    
    max_rows = get_max(cname=['mem_tot_alloc_bm16384', 'mem_tot_alloc_bm32'])
    for item in max_rows:
        print(f"{item['max_row']}")
    '''
    records_list = []
    influx_out = influx_query(cname)
    for table in influx_out:
        for record in table.records:
            record_dict = {
                '_value': float(record.values['_value']),
                'counter': record.values['counter'],
                '_time': pd.to_datetime(record.values['_time']).strftime('%a %b %d %H:%M:%S %Y')
            }
            records_list.append(record_dict)
    # Create a DataFrame and sort by the '_time' column
    df = pd.DataFrame(records_list)
    df['_time'] = pd.to_datetime(df['_time'])
    df = df.sort_values(by='_time')
    # Convert the '_time' column back to the original timestamp format
    df['_time'] = df['_time'].dt.strftime('%a %b %d %H:%M:%S %Y')
    max_rows = []
    for counter in df['counter'].unique():
        # Filter DataFrame for each counter
        counter_df = df[df['counter'] == counter]
        # Get the row corresponding to the maximum value of '_value' column
        max_row = counter_df.loc[counter_df['_value'].idxmax()]
        # Format the row as a string
        max_row_str = f"{max_row['_value']} {max_row['counter']} {max_row['_time']}"
        max_rows.append({'counter': counter, 'max_row': max_row_str})
    return max_rows

