from daemonize import daemon
import json, os, sys, datetime, time, logging
import zabbix_query as zq 


class D(daemon):

	def __init__(self, pwd):
		self.pidfile = pwd+"/.pidfile"
		self.conf_Path = pwd+"/midware.conf"
		self.out_Dir = pwd+"/probe/"
		self.config = ""

	def config_setup(self):
		logging.debug("setting_up_config")
		try:
			fp = open(self.conf_Path)
			self.config = json.load(fp)
			fp.close()
		except:
			logging.exception("config_failed")
			sys.exit(1)
		logging.debug("config_complete")
	
	def run(self):
		self.config_setup()
		zabbix = self.config["zabbix"]
		zq.login(host=zabbix["host"], user=zabbix["user"], password=zabbix["password"])
		
		while(True):
			zq.extend_liftime()
			try:
				zq.bulk_query(self.config, self.out_Dir)
			except:
				logging.exception("Error_while_query")
				exit(1)
			now = datetime.datetime.now()
			delta = datetime.timedelta(minutes=1) - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)
			time.sleep(delta.total_seconds())


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, filename=os.getcwd()+'/midware.log')
	if len(sys.argv)==2:
		APP = D(os.getcwd())
		if sys.argv[1] == "start":
			logging.debug("Send_start_message")
			APP.start()
		if sys.argv[1] == "restart":
			logging.debug("Send_restart_message")
			APP.restart()
		if sys.argv[1] == "stop":
			logging.debug("Send_stop_message")
			APP.stop()
		else :
			logging.error("Unkown argument")
	else:
		print("usage:")
		print("\tpython3 main.py start|restart|stop")