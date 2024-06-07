import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


client = influxdb_client.InfluxDBClient(
   url='http://influx.deva.citrite.net:8086',
   token='f4DtBvmog-ubxhvqFiCUImLdwVVWP6dGh5W6SFiun1Wx6U0XBp4iIW0pvkqEeOQt7HvcT6jIzVUjnYWXDaPSsw==',
   org='netscaler'
)

query_api = client.query_api()

query = 'from(bucket:"nscounters")\
|> range(start: -30d)\
|> filter(fn:(r) => r._measurement == "dcurrent2")\
|> filter(fn:(r) => r.case == "n82618102")\
|> filter(fn:(r) => r.nsip == "172.20.31.162")\
|> filter(fn:(r) => r.counter == "cc_cpu_use")\
|> filter(fn:(r) => r._field == "value")'

org='netscaler'


result = query_api.query(org=org, query=query)

print(result)