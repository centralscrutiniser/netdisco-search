from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# NetDisco credentials and base URL
NETDISCO_URL = "http://{netdiso-host}:5000"
NETDISCO_USERNAME = "{netdiso username}"
NETDISCO_PASSWORD = "{netdisco password}"

# Function to authenticate and get API key
def get_api_key():
    login_url = f"{NETDISCO_URL}/login"
    auth_response = requests.post(
        login_url,
        auth=(NETDISCO_USERNAME, NETDISCO_PASSWORD),
        headers={'Accept': 'application/json'}
    )

    if auth_response.status_code == 200:
        try:
            return auth_response.json().get('api_key')
        except KeyError:
            print("API key not found in response.")
            return None
    else:
        print("Authentication Failed:", auth_response.text)
        return None

# Function to query NetDisco by IP address or MAC address
def query_netdisco(address, api_key):
    # Using the /api/v1/search/node endpoint for both IP and MAC address queries
    query_url = f"{NETDISCO_URL}/api/v1/search/node"
    
    headers = {'Authorization': f"{api_key}", 'Accept': 'application/json'}
    payload = {'q': address}
    
    response = requests.get(query_url, headers=headers, params=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Query Failed: {response.text}")
        return None

# Function to query NetDisco for MAC address and get the port information
def query_mac_port(mac_address, api_key):
    query_url = f"{NETDISCO_URL}/api/v1/search/node"
    
    headers = {'Authorization': f"{api_key}", 'Accept': 'application/json'}
    payload = {'q': mac_address}
    
    response = requests.get(query_url, headers=headers, params=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Query Failed for MAC: {response.text}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        address = request.form['address']
        
        api_key = get_api_key()
        if not api_key:
            return render_template('index.html', result="Failed to get API key", address=address)

        # **Query NetDisco (MAC or IP)**
        result = query_netdisco(address, api_key)
        if not result:
            return render_template('index.html', result=f"No data found for {address}", address=address)

        structured_data = []

        # **Check if it's an IP Lookup (Contains 'macs')**
        if 'macs' in result and len(result['macs']) > 0:
            mac_address = result['macs'][0]['mac']
            sightings_result = query_netdisco(mac_address, api_key)  # Second query for sightings

            for device in result['macs']:
                structured_entry = {
                    'ip': device.get('ip', 'N/A'),
                    'mac': device.get('mac', 'N/A'),
                    'manufacturer': device.get('manufacturer', {}).get('company', 'Unknown'),
                    'time_first': device.get('time_first', 'N/A'),
                    'time_last': device.get('time_last', 'N/A'),
                    'device_name': 'N/A',
                    'port': 'N/A'
                }

                if sightings_result and 'sightings' in sightings_result:
                    for sighting in sightings_result['sightings']:
                        if sighting['mac'] == structured_entry['mac']:
                            clean_device_name = sighting.get('device', {}).get('name', 'N/A').replace('.DOMAIN.TLD', '')
                            structured_entry['device_name'] = clean_device_name
                            structured_entry['port'] = sighting.get('port', 'N/A')

                structured_data.append(structured_entry)

        # **Check if it's a MAC Lookup (Contains 'ips')**
        elif 'ips' in result and len(result['ips']) > 0:
            for device in result['ips']:
                structured_entry = {
                    'ip': device.get('ip', 'N/A'),
                    'mac': device.get('mac', 'N/A'),
                    'manufacturer': device.get('manufacturer', {}).get('company', 'Unknown'),
                    'time_first': device.get('time_first', 'N/A'),
                    'time_last': device.get('time_last', 'N/A'),
                    'device_name': 'N/A',
                    'port': 'N/A'
                }

                if 'sightings' in result and len(result['sightings']) > 0:
                    sighting = result['sightings'][0]
                    structured_entry['device_name'] = sighting.get('device', {}).get('name', 'N/A').replace('.DOMAIN.TLD', '')
                    structured_entry['port'] = sighting.get('port', 'N/A')

                structured_data.append(structured_entry)

        print("Final Processed Data:", json.dumps(structured_data, indent=2))  # Debugging Output

        return render_template('index.html', result=structured_data, address=address)

    return render_template('index.html', result=None)


if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=10440, debug=True)
    app.run(port=10440, debug=True)
