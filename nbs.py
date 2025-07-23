from flask import Flask, render_template, request, Response
import requests, json, csv, io, ipaddress
from urllib.parse import quote

app = Flask(__name__)

NETDISCO_URL = "http://{netdisco-host}:5000"
NETDISCO_USERNAME = "{netdisco username}"
NETDISCO_PASSWORD = "{netdisco password}"

def get_api_key():
    r = requests.post(
        f"{NETDISCO_URL}/login",
        auth=(NETDISCO_USERNAME, NETDISCO_PASSWORD),
        headers={'Accept':'application/json'}
    )
    if r.status_code == 200:
        return r.json().get('api_key')
    return None

def query_netdisco(address, api_key):
    r = requests.get(
        f"{NETDISCO_URL}/api/v1/search/node",
        headers={'Authorization': api_key, 'Accept':'application/json'},
        params={'q': address}
    )
    return r.json() if r.status_code == 200 else None

def query_port_description(switch_ip, port, api_key):
    port_enc = quote(port, safe='')
    r = requests.get(
        f"{NETDISCO_URL}/api/v1/object/device/{switch_ip}/port/{port_enc}",
        headers={'Authorization': api_key, 'Accept':'application/json'}
    )
    if r.status_code == 200:
        return r.json().get('name')
    return None

def build_results(address, api_key):
    data = query_netdisco(address, api_key)
    if not data:
        return None

    rows = []

    # MAC‐lookup branch
    if 'ips' in data and data['ips']:
        for device in data['ips']:
            mac       = device.get('mac')
            ip        = device.get('ip')
            entry = {
                'ip'               : ip or 'N/A',
                'mac'              : mac or 'N/A',
                'manufacturer'     : device.get('manufacturer',{}).get('company','Unknown'),
                'time_last'        : device.get('time_last','N/A'),
                'device_name'      : 'N/A',
                'port'             : 'N/A',
                'port_description' : 'N/A'
            }

            # sightings come in the same payload
            if 'sightings' in data and data['sightings']:
                s = data['sightings'][0]
                entry['device_name'] = s.get('device',{}).get('name','N/A')\
                                            .replace('.uwe.ac.uk','')
                entry['port']        = s.get('port','N/A')
                switch_ip            = s.get('switch')
                if switch_ip and entry['port']!='N/A':
                    desc = query_port_description(switch_ip, entry['port'], api_key)
                    entry['port_description'] = desc or 'N/A'

            rows.append(entry)

    # IP‐lookup (and subnet) branch
    elif 'macs' in data and data['macs']:
        for device in data['macs']:
            mac = device.get('mac')
            entry = {
                'ip'               : device.get('ip','N/A'),
                'mac'              : mac or 'N/A',
                'manufacturer'     : device.get('manufacturer',{}).get('company','Unknown'),
                'time_last'        : device.get('time_last','N/A'),
                'device_name'      : 'N/A',
                'port'             : 'N/A',
                'port_description' : 'N/A'
            }

            # second query for sightings
            sdata = query_netdisco(mac, api_key)
            switch_ip = None
            if sdata and 'sightings' in sdata:
                for s in sdata['sightings']:
                    if s.get('mac') == mac:
                        entry['device_name'] = s.get('device',{})\
                                               .get('name','N/A')\
                                               .replace('.uwe.ac.uk','')
                        entry['port']        = s.get('port','N/A')
                        switch_ip            = s.get('switch')
                        break

            if switch_ip and entry['port']!='N/A':
                desc = query_port_description(switch_ip, entry['port'], api_key)
                entry['port_description'] = desc or 'N/A'

            rows.append(entry)

    else:
        return None

    # sort by numeric IP
    rows.sort(key=lambda x: ipaddress.IPv4Address(x['ip']))
    return rows

@app.route('/', methods=['GET','POST'])
def index():
    if request.method=='POST':
        address = request.form['address']
        api_key  = get_api_key()
        if not api_key:
            return render_template('index.html', error="Auth failed")

        rows = build_results(address, api_key)
        if not rows:
            return render_template('index.html', error=f"No data for {address}")

        return render_template('index.html', address=address, result=rows)

    return render_template('index.html')

@app.route('/export')
def export():
    address = request.args.get('address')
    api_key  = get_api_key()
    rows = build_results(address, api_key)
    if not rows:
        return ("No data to export", 404)

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow([
        "IP Address","MAC Address","Manufacturer",
        "Last Seen","Device Name","Port Description","Switch Port"
    ])
    for e in rows:
        cw.writerow([
            e['ip'], e['mac'], e['manufacturer'],
            e['time_last'], e['device_name'],
            e['port_description'], e['port']
        ])

    return Response(
        si.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition':f'attachment;filename=netdisco_{address.replace("/","_")}.csv'}
    )

if __name__=='__main__':
    app.run(port=10440, debug=True)
