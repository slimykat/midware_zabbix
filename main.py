from daemonize import daemon
from c2v import json2csv
import json, os, sys, datetime, time, threading, logging
import zabbix_query as zq 


class D(daemon):

	def __init__(self, pwd):
		self.pidfile = pwd+"/.pidfile"
		self.conf_Path = pwd+"/midware.conf"
		self.out_Dir = pwd+"/probe/"

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

	def query(self):
		# record the query time (AKA current time)
		t = datetime.datetime.now()
		now = t.strftime("%Y%m%d_%H_%M")

		# request for all the data within the one minute
		time_till = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0)
		time_till = int(time_till.timestamp())
		time_from = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0) - datetime.timedelta(minutes=1)
		time_from = int(time_from.timestamp())
		logging.debug("time_set")

		# login
		zabbix = self.config["zabbix"]
		probe = self.config["probe"]
		try:
			zq.login(host=zabbix["host"],user=zabbix["user"], password=zabbix["password"])
		except:
			logging.exception("Login_error")

		logging.debug("prepared_to_query")
		# bulk query for each group
		for probe_type, groups in probe.items():		# for the definition of the layout
			for dtype, itemlist in groups.items():	# plz check the document

				# send query message, arguments contains these information:
				# 		target(s), group, start_time, end_time
				itemids = list(itemlist.keys())
				payload = zq.item_hist_get(itemids, dtype, time_from=time_from, time_till=time_till)

				# set up for file IO
				file_name = self.out_Dir+str(probe_type)+"@"+now

				# assign the task to another thread
				t = threading.Thread(
					target=json2csv, 
					args=(payload, itemlist, file_name),
					kwargs={"attr_entry":zabbix["kwargs"][0], "clock_entry":zabbix["kwargs"][1]}
				)
				t.start() # no need to join
		logging.debug("Query_complete")

	def run(self):
		self.config_setup()
		while(True):
			#zq.login()
			self.query()
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