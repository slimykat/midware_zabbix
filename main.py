from daemonize import daemon
from c2v import json2csv
import json, os, sys, datetime, time, threading
import zabbix_query as zq 


class D(daemon):

	def config_setup(self):
		fp = open(self.conf_Path)
		self.config = json.load(fp)
		fp.close()

	def query(self):
		# record the query time (AKA current time)
	    t = datetime.datetime.now()
	    now = t.strftime("%Y%m%d_%H_%M")

	    # request for all the data within the one minute
	    time_till = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0)
	    time_till = int(time_till.timestamp())
	    time_from = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0) - datetime.timedelta(minutes=1)
	    time_from = int(time_from.timestamp())

	    # login
	    zabbix= self.config["zabbix"]
	    zq.login(host=zabbix["host"],User=zabbix["user"],Password=zabbix["password"])

	    # bulk query for each group
	    config = self.config['probe']
	    for probe_type, groups in config.items():		# for the definition of the layout
	    	for dtype, itemlist in groups.items():	# plz check the document
	   
	    		# send query message, arguments contains these information:
	    		# 		target(s), group, start_time, end_time
	    		itemids = itemlist.keys()
	    		payload = zq.item_hist_get(itemids, dtype, time_from=time_from, time_till=time_till)

	    		# set up for file IO
	    		file_name = str(probe_type)+"@"+now

	    		# assign the task to another thread
	    		t = threading.Thread(
	    			target=json2csv, 
	    			arg=(payload, itemlist, file_name),
	    			kwargs={"attr_entry":zabbix["kwargs"][0], "clock_entry":zabbix["kwargs"][1]}
	    			)
	    		t.start() # no need to join

	def run(self):
		self.config_setup()

		logging.debug("config_safe")
		while(True):
			logging.debug("running...")
			time.sleep(3)

		while(True):
	        self.query()
	        now = datetime.datetime.now()
	        delta = datetime.timedelta(minutes=1) - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)
	        time.sleep(delta.total_seconds())


if __name__ == "__main__":
	if len(sys.argv)==2:
		APP = D("pidfile")
		APP.conf_Path = os.getcwd()+"/miware.conf"
		if sys.argv[1] == "start":
			APP.start()
		if sys.argv[1] == "restart":
			APP.restart()
		if sys.argv[1] == "stop":
			APP.stop()
	else:
		print("usage:")
		print("\tpython3 main.py start|restart|stop")