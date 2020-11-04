"""Generic linux daemon base class for python 3.x."""
import sys, os, time, atexit, signal, logging

def sigHandler(signo, frame):
    sys.exit(0)

class daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method."""

    def __init__(self):
        self.pidfile = "pidfile"
        signal.signal(signal.SIGTERM, sigHandler) # calls sys.exit when receiving SIGTERM

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""
        logging.debug("start_daemonize")

        try: 
            pid = os.fork() 
            logging.debug("fork_#1_Process_Hi_"+str(os.getpid()))
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)
    
        # do second fork
        try: 
            pid = os.fork()
            logging.debug("fork_#2_Process_Hi_"+str(os.getpid()))
            if pid > 0:
                # exit from second parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1) 
        
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        logging.debug("End_of_dup2")

        # write pidfile
        pid = str(os.getpid())
        try:
            with open(self.pidfile,'w+') as f:
                f.write(pid + '\n')
        except:
            logging.exception("Write_pidfile_failed")
        atexit.register(self.delpid) # clear pidfile when exiting

        logging.info("Daemon_is_now_running_on_"+pid)

    def delpid(self):
        logging.info("Daemon_Goodbye_"+str(os.getpid()))

        try:
            os.remove(self.pidfile)
        except:
            pass

    def start(self, if_daemon=True):
        """Start the daemon."""
        logging.info("Starting...")
        if if_daemon:

            # Check for a pidfile to see if the daemon already runs
            try:
                with open(self.pidfile,'r') as pf:

                    pid = int(pf.read().strip())

            except IOError:
                pid = None
            logging.debug("PID="+str(pid))
            if pid:
                message = "pidfile {0} already exist. " + \
                        "Daemon already running?\n"
                sys.stderr.write(message.format(self.pidfile))
                sys.exit(1)
            
            # Start the daemon
            self.daemonize()
            logging.info("Daemonize_complete")
        else:
            logging.info("Daemonize_off")
        self.run()

    def stop(self):
        """Stop the daemon."""
        logging.info("Stopping...")
        # Get the pid from the pidfile
        try:
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
    
        if not pid:
            message = "pidfile {0} does not exist. " + \
                    "Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))
            return # not an error in a restart

        # Try killing the daemon process    
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print (str(err.args))
                sys.exit(1)
        logging.info("Daemon_has_stoped")

    def restart(self):
        """Restart the daemon."""
        logging.info("Restarting...")
        self.stop()
        self.start()

    def run(self):
        logging.critical("run_function_Not_Defined?")
        """You should override this method when you subclass Daemon.
        
        It will be called after the process has been daemonized by 
        start() or restart()."""

