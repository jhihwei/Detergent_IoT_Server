sudo apt install -y python-psycopg2

sudo echo -e "
[Unit]
  Description=Recorder Sales
  After=network.target
  [Service]
  User=user
  ExecStart=/usr/bin/python3 /home/user/Detergent_IoT_Server/recorder/Sales.py
  ExecReload=/bin/kill -HUP $MAINPID
  KillMode=process
  IgnoreSIGPIPE=true
  Restart=always
  RestartSec=3
  Type=simple
  [Install]
  WantedBy=multi-user.target" > /etc/systemd/system/recorder.sales.service
sudo systemctl enable recorder.sales.service
sudo systemctl restart recorder.sales.service

sudo echo -e "
[Unit]
  Description=Terminal Info
  After=network.target
  [Service]
  User=user
  ExecStart=/usr/bin/python3 /home/user/Detergent_IoT_Server/recorder/Terminal_info.py
  ExecReload=/bin/kill -HUP $MAINPID
  KillMode=process
  IgnoreSIGPIPE=true
  Restart=always
  RestartSec=3
  Type=simple
  [Install]
  WantedBy=multi-user.target" > /etc/systemd/system/recorder.terminal_info.service
sudo systemctl enable recorder.terminal_info.service
sudo systemctl restart recorder.terminal_info.service
