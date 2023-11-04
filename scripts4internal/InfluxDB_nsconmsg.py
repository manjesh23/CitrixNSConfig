# Get all the hardcoded nsconmsg counter values from InfluxDB copied to file

# obvious imports
# pip install influxdb-client --> Install the influxdb-client using pip
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os, re, time
import subprocess as sp

start_time = time.time()

# Define a list of valid counter values
newnslog_errors_latency  = [
    "ssl_err_cardstatusdown",
    "ssl_error_cvm_cmd_timeout",
    "ssl_error_cavium_device_error",
    "ssl_error_cavium_vip_ec_command_direct",
    "ssl_error_cavium_hsmerror",
    "ssl_err_ssl3_spcb_alloction",
    "ssl_err_nonsb_for_output",
    "ssl_err_ssl_ubsec_command_timeout",
    "ssl_err_vip_smachine_had_timeout",
    "ssl_err_vip_smachine_lkrc_timeout",
    "ssl_cfg_mcmx_clone_timeout_interval",
    "ssl_err_cvm_cmd_timeout_recovered",
    "ssl_tot_held_ctx_timeout_runs",
    "ssl_tot_sslError_FatalAlertRecdCount",
    "ssl_tot_sslError_FatalAlertSentCount",
    "ssl_cur_sslInfo_nsCardInQCount",
    "tcp_err_hole_server",
    "tcp_err_hole_detected",
    "tcp_err_hole_filled",
    "tcp_err_hole_filled_20ms",
    "nstcp_err_hole_free_reasmq",
    "tcp_err_full_retransmit",
    "tcp_err_partial_retransmit",
    "tcp_err_clnt_out_of_order",
    "tcp_err_srvr_out_of_order",
    "tcp_err_ghostack",
    "tcp_err_nobuf",
    "tcp_err_syn_drop",
    "tcp_err_duplicate_packet",
    "tcp_err_no_hole_dup_ack",
    "tcp_err_retransmit_giveups",
    "tcp_err_fin_retransmit",
    "tcp_err_srvr_retransmit",
    "tcp_err_dup_retransmission",
    "tcp_err_fin_dup",
    "tcp_err_SW_init_pktdrop",
    "net_cur_congested",
    "http_err_PipeLinedRequests",
    "ip_err_max_clients",
    "arp_err_dup_pkts",
    "as_err_mem_post_body",
    "si_err_surgeq_timeout",
    "si_err_surgeQ_timeout",
    "tcp_err_surgeQ_timeout",
    "dns_tot_pipeline_dropped",
    "mcmx_err_send_msg",
    "lb_err_selected_svc_not_usable",
    "tcpb_err_bypass",
    "nic_tot_bdg_mac_moved",
    "ip_err_ttl_expired",
    "ip_err_portalloc_failed",
    "dht_err_cache_limit_exceeds",
    "dht_err_entity_get_or_create_failed",
    "dht_err_callback_for_heartbeat_failed",
    "dht_err_update_didnt_find_entry",
    "dht_err_unable_to_put_replica",
    "lb_sess_dht_deserialise_failed_err",
    "dht_err_c2c_send_to_wrong_target",
    "dht_err_cache_entry_allocation_failed",
    "dht_err_app_deserialize_failed",
    "dht_err_c2c_loopback_msg",
    "dht_err_c2c_send_message_retry",
    "dht_err_c2c_send_message_to_owner",
]

# Generate the filter conditions for each valid counter
filter_conditions = ' or '.join([f'r.counter == "{counter}"' for counter in newnslog_errors_latency])
linux_command = "ns 2ts " + " ".join(["-g " + item for item in newnslog_errors_latency]) + " var/nslog/newnslog*"
ns2ts_command = sp.run(linux_command, shell=True, text=True, stderr=sp.PIPE, stdout=sp.PIPE).stdout

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
for table in newnslog_errors_latency_data:
    for record in table.records:
        print(str(record.values['_time']) + " -- " + record.values['counter'] + " -- " + str(record.values['_value']))

end_time = time.time()

elapsed_time = end_time - start_time
print(f'Time taken: {elapsed_time}')