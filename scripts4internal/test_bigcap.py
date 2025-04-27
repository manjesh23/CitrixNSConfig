import os
import subprocess as sp
import re
from collections import defaultdict
from datetime import datetime

# Define the log directory and counter name
log_dir = "./var/nslog"
counter_name = "nic_tot_tx_packets"

# Get all newnslog files
newnslog_files = [f for f in os.listdir(log_dir) if f.startswith("newnslog")]

# This will store the names of all generated HTML files
generated_html_files = []

# Process each newnslog file
for newnslog in newnslog_files:
    newnslog_path = os.path.join(log_dir, newnslog)

    # Run the nsconmsg command to fetch data
    cmd = ["nsconmsg", "-K", newnslog_path, "-s", "disptime=1", "-d", "current", "-f", counter_name]
    result = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, text=True)

    # Define regex pattern for matching data
    pattern = re.compile(r"^\s*\d+\s+\d+\s+(?P<totalcount>\d+)\s+(?P<delta>-?\d+)\s+(?P<rate>-?\d+)\s+(?P<counter>\S+)(?:\s+(?P<device>\S+))?\s+(?P<date>\w+ \w+ \d+ \d+:\d+:\d+ \d+)")

    adchostname = sp.run("awk '{print $2}' shell/uname-a.out", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip()
    collector_bundle_name = re.search(r"(collector_\S+)", sp.run('pwd', shell=True, capture_output=True, text=True).stdout)
    collector_bundle_name = collector_bundle_name.group(1) if collector_bundle_name else None
    start_time = sp.run(f"nsconmsg -K {newnslog_path} -d setime | awk '/start time/{{print $4, $5, $6, $7}}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip()
    end_time = sp.run(f"nsconmsg -K {newnslog_path} -d setime | awk '/end   time/{{print $4, $5, $6, $7}}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip()
    start_end = f'{start_time} to {end_time}'
    
    data, time_device_metric_map = [], defaultdict(lambda: defaultdict(dict))
    for line in result.stdout.splitlines():
        match = pattern.search(line)
        if match:
            g = match.groupdict()
            dt = datetime.strptime(g["date"], "%a %b %d %H:%M:%S %Y")
            device = g.get("device") or "default"
            data.append({"datetime": dt, "device": device, "totalcount": int(g["totalcount"]), "delta": int(g["delta"]), "rate": int(g["rate"])})

    if not data:
        print(f"No data found for counter: {counter_name} in {newnslog}")
        continue

    times = sorted(set(d["datetime"] for d in data))
    devices = sorted(set(d["device"] for d in data))

    for d in data:
        for metric in ["totalcount", "delta", "rate"]:
            time_device_metric_map[d["datetime"]][d["device"]][metric] = d[metric]

    # === Build HTML ===
    def build_rows(metric):
        rows = []
        for t in times:
            ts = t.strftime("%b %d,%Y %H:%M:%S")
            vals = [str(time_device_metric_map[t].get(dev, {}).get(metric, "null")) for dev in devices]
            row = f"[new Date('{ts}'), {', '.join(vals)}]"
            rows.append(row)
        return ",\n".join(rows)

    html = f"""<html><head>
    <script src="https://www.gstatic.com/charts/loader.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/manjesh23/CitrixNSConfig@9bc88cdd9bf82282eacd2babf714a1d8a5d00358/scripts4internal/conFetch.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/manjesh23/CitrixNSConfig@9bc88cdd9bf82282eacd2babf714a1d8a5d00358/scripts4internal/conFetch.css">
    <script>google.charts.load('current',{{'packages':['annotationchart']}});
    google.charts.setOnLoadCallback(()=>drawChart());
    var data_all={{"totalcount":[{build_rows('totalcount')}],"delta":[{build_rows('delta')}],"rate":[{build_rows('rate')}] }};
    function drawChart(metric="totalcount"){{
    var data=new google.visualization.DataTable();
    data.addColumn('date','Timestamp');
    {''.join([f"data.addColumn('number','{d}');" for d in devices])}
    data_all[metric].forEach(r=>data.addRow(r));
    var chart=new google.visualization.AnnotationChart(document.getElementById('chart_div'));
    chart.draw(data,{{displayAnnotations:true,displayZoomButtons:false,dateFormat:'HH:mm:ss MMM dd, yyyy',thickness:2,scaleType:'allfixed'}});
    }}
    function changeMetric(){{drawChart(document.getElementById('metric_selector').value);}}


    </script></head><body>
    <h1 class="txt-primary">{counter_name}</h1><hr>
    <p class="txt-title">
    Collector_Bundle_Name: {collector_bundle_name}<br>
    Device_Name: {adchostname}<br>
    Log_file: {newnslog}<br>
    Log_Timestamp: {start_end}
    </p><hr>
    <div style="margin-bottom:10px;">
    <label for="metric_selector">Select Metric: </label>
    <select id="metric_selector" onchange="changeMetric()">
    <option value="totalcount" selected>Total Count</option>
    <option value="delta">Delta</option>
    <option value="rate">Rate/sec</option>
    </select></div>
    <div style="width:100%">
    <p class="txt-primary">{counter_name} Graph</p>
    <div id="chart_div" style="height:450px"></div>
    </div>
    <div class="footer">Project conFetch</div>
    </body></html>"""

    # Build chart filename properly
    chart_filename = f"{counter_name}_{newnslog}.html"
    with open(chart_filename, "w") as f:
        f.write(html)

    generated_html_files.append(chart_filename)
    print(f"Minified Chart generated for {newnslog}! Open '{chart_filename}'.")

# Now create the master HTML file that allows selection of the charts
master_html_content = """
<html>
<head>
    <title>Master Graph Viewer</title>
    <script>
        function loadChart() {
            var chartFile = document.getElementById("chart_selector").value;
            if (chartFile) {
                var iframe = document.getElementById("chart_iframe");
                iframe.src = chartFile;
            }
        }
    </script>
    <style>
        body, html { margin: 0; padding: 0; height: 100%; width: 100%; }
        iframe { 
            width: 100%; 
            height: 100%; 
            border: none; 
            overflow: hidden; /* Prevent scrolling */
        }
    </style>
</head>
<body>
    <h1>Project conFetch Graph</h1>
    <h1>Select a newnslog file to View graph</h1>
    <label for="chart_selector">Select newnslog file: </label>
    <select id="chart_selector" onchange="loadChart()">
        <option value="">-- Select --</option>
"""

# Filter generated HTML files that match the counter name
for html_file in generated_html_files:
    # Check if the chart file matches the counter name
    if counter_name in html_file:
        master_html_content += f'        <option value="{html_file}">{html_file}</option>\n'

# Continue building the rest of the master HTML
master_html_content += """
    </select>

    <div style="margin-top: 20px;">
        <iframe id="chart_iframe" scrolling="no"></iframe>
    </div>
</body>
</html>
"""

# Save the master HTML file
master_html_filename = f"master_{counter_name}_graph.html"
with open(master_html_filename, "w") as f:
    f.write(master_html_content)

print(f"Master HTML file '{master_html_filename}' created successfully!")
