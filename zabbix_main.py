from daemonize import daemon
from flask import request
import json, os, sys, datetime, time, logging, atexit, threading
import zabbix_query as zq 
import zabbix_UI as zui

class D(daemon):

	def __init__(self, pwd):
		self.pidfile = pwd+"/.pidfile"
		self.conf_Path = pwd+"/midware.conf"
		self.log_path = pwd+"/.midware.log"
		self.config = {}

	def config_setup(self):
		try:
			with open(self.conf_Path) as fp:
				self.config = json.load(fp)
			atexit.register(self._config_record)
		except:
			logging.exception("config_failed")
			sys.exit(1)
		if not os.path.is_dir(self.config["zabbix"]["out_Dir"]):
			logging.error("Output_Directory_DNE")
			sys.exit(1)
		logging.debug("config_complete")
	
	def _config_record(self):
		if self.config:
			with open(self.conf_Path, "w") as fp:
				json.dump(self.config,fp, indent=4)

	def run(self):
		# set up config and login to zabbix
		self.config_setup()
		zabbix = self.config["zabbix"]
		zq.login(host=zabbix["host"], user=zabbix["user"], password=zabbix["password"])
		
		# start ui thread
		try:
			zui.app._config = self.config
			ui = threading.Thread(target=zui.app.run, kwargs=zabbix["UI_address"])
			ui.start()
		except:
			logging.exception("UI_error")
			sys.exit(1)
		logging.info("UI_is_now_running")

		while(True):
			zq.extend_liftime()
			try:
				zq.bulk_query(self.config)
			except:
				logging.exception("Error_while_query")
				sys.exit(1)

			now = datetime.datetime.now()
			delta = datetime.timedelta(minutes=1) - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)
			time.sleep(delta.total_seconds())


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, filename=os.getcwd()+'/midware.log')
	if len(sys.argv)==2:
		APP = D(os.getcwd())
		if sys.argv[1] == "daemon":
			logging.debug("Send_daemon_message")
			APP.start()
		elif sys.argv[1] == "restart":
			logging.debug("Send_restart_message")
			APP.restart()
		elif sys.argv[1] == "stop":
			logging.debug("Send_stop_message")
			APP.stop()
		elif sys.argv[1] == "start":
			logging.debug("Send_start_message")
			APP.start(if_daemon=False)
		else :
			logging.error("Unkown argument")
	else:
		print("usage:")
		print("\tpython3 main.py start|restart|stop|daemon")