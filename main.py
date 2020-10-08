from daemonize import daemon
from c2v import json2csv
import json, os, sys, datetime, time, threading
import zabbix_query as zq 


class D(daemon):

	def config_setup(self):
		fp = open(self.conf_Path)
		self.config = json.load(fp)
		fp.close()

	def query(selt):
		# record the query time (AKA current time)
	    t = datetime.datetime.now()
	    now = t.strftime("%Y%m%d_%H_%M")

	    # request for all the data within the one minute
	    time_till = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0)
	    time_till = int(time_till.timestamp())
	    time_from = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0) - datetime.timedelta(minutes=1)
	    time_from = int(time_from.timestamp())

	    # login
	    zq.login(host)

	    # bulk query for each group
	    config = self.config['probe']
	    for probe_type, groups in config.items():		# for the definition of the layout
	    	for dtype, attributes in groups.items():	# plz check the document
	    		file_name = str(probe_type)+"@"+now
	    		t = threading.Thread(target=json2csv, arg=())
	    		t.start()

	def run(self):
		self.config_setup()

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