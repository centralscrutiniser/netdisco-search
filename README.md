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

<img width="1283" height="594" alt="Screenshot 2025-07-23 at 18 37 13" src="https://github.com/user-attachments/assets/272c7af3-9ace-40b7-a121-eabcc548485a" />

And MAC Addresses

<img width="1285" height="596" alt="Screenshot 2025-07-23 at 18 38 39" src="https://github.com/user-attachments/assets/795782ef-9eb3-4976-9bd6-d21c21dcac5c" />

As NetDisco will also allow you to search an entire subnet, this is also supported. 

<img width="1318" height="955" alt="Screenshot 2025-07-23 at 18 36 49" src="https://github.com/user-attachments/assets/e62943fd-8379-4767-85a3-c8c00c79d91f" />

The output can be exported to CSV at the click of a button. 




