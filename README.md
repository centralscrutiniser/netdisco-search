# netdisco-search
Netdisco-search is a python flask application which queries the [NetDisco](https://netdisco.org/) API for IP Address/MAC Address information, displaying the results in an HTML table. It is useful for providing IT support staff access to NetDisco data, without providing a login to NetDisco itself.

You can run this application on the NetDisco host itself, or on a remote host. 

## Setup
Edit the ```nbs.py``` file, and amend the following variables -

```
NETDISCO_URL = "http://{netdisco-host}:5000"
NETDISCO_USERNAME = "{netdisco username}"
NETDISCO_PASSWORD = "{netdisco password}"
```

If your NetDisco data contains hosts with a domain name suffix (i.e switch-name.domain.tld), and you wish to remove the domain from the output, find the following two lines and change ```DOMAIN.TLD``` to the domain suffix you want removing. 

```clean_device_name = sighting.get('device', {}).get('name', 'N/A').replace('.DOMAIN.TLD', '')```

```structured_entry['device_name'] = sighting.get('device', {}).get('name', 'N/A').replace('.DOMAIN.TLD', '')```

## SystemD service
Here's an example systemd service file you can use to run as a background service

```
[Unit]
Description=Netdisco Search UI
After=multi-user.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /usr/local/bin/nbs/nbs.py

[Install]
WantedBy=multi-user.target
```

## Service port
The app listens on ```0.0.0.0:10440``` by default. If this does not meet your needs, feel free to change this line in the nbs.py file. 

```app.run(host='0.0.0.0', port=10441, debug=True)```

You can, of course, run this behind an Nginx or Apache reverse proxy if you wish. 

## Operation
Once running, the UI presents a simple lookup form to lookup IP Addresses

<img width="1324" alt="IP" src="https://github.com/user-attachments/assets/f769fb7b-08ee-4d47-9288-c067e2565ef6" />

And MAC Addresses

<img width="1318" alt="MAC" src="https://github.com/user-attachments/assets/c17fda4a-e709-465d-9219-94f01a9a939e" />


