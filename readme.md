# midware_zabbix

[hackmd document v2.0](https://hackmd.io/@mcnlab538/Bk3V7yDPD)

<!---
[hackmd document v2.1 NYI](https://hackmd.io/@mcnlab538/Sy2gnJeYP)
--->

## Usage
```shell
% python3 zabbix_main.py -h     
usage: zabbix_main.py [-h] [options] {start,stop,restart,daemon}

Transform Zabbix data to AIOPs format.

positional arguments:
  {start,stop,restart,daemon}
                        Instruction for the program

optional arguments:
  -h, --help            show this help message and exit
  -c path, --config path
                        config file path
  -l path, --log path   log file path
  -o path, --out_Dir path
                        output directory path
  -p path, --pidfile path
                        pidfile path
  -v                    logging level
```
## Dev notes

v2.1.0
1. added argparse
2. change config so that some argument would not be passed from config

prep on adding the midware to systemd service

v2.0.2
1. endpoints, including show and update config

v2.0.1
1. added daemonized functions
2. running query with threading
3. basic framework complete

