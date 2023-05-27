<h1>==>To make script autorun follow this</h1>

<b>Create a systemd service file:</b> <br>
`sudo nano /etc/systemd/system/dronefly.service`

<br>Add the following content to the service file:</b> <br>
`[Unit]`<br>
`Description=Dronefly Service`<br>
`After=network.target`<br>
<br>
`[Service]`<br>
`ExecStart=/usr/bin/python3 /home/pi/Desktop/autocode/dronefly/__main__.py`<br>
`WorkingDirectory=/home/pi/Desktop/autocode/dronefly`<br>
`StandardOutput=file:/home/pi/Desktop/output.log`<br>
`StandardError=file:/home/pi/Desktop/error.log`<br>
`Restart=always`<br>
`User=pi`<br>
<br>
`[Install]`<br>
`WantedBy=multi-user.target`

<br>Enable and start the service:</b> <br>
`sudo systemctl enable dronefly.service
sudo systemctl start dronefly.service`

<br>Stop the service:</b> <br>
`sudo systemctl stop dronefly.service`

<br>Restart the service:</b> <br>
`sudo systemctl restart dronefly.service`

<br>Disable the service (won't start on boot):</b> <br>
`sudo systemctl disable dronefly.service`

<br>Check the status of the service:</b> <br>
`sudo systemctl status dronefly.service`
