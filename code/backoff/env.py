import os, signal, sys, time
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from process import Process
from replica import Replica
from utils import *

NACCEPTORS = 3
NREPLICAS = 2
NLEADERS = 2
NREQUESTS = 40
NCONFIGS = 3

class Env:
    """
    This is the main code in which all processes are created and run. This
    code also simulates a set of clients submitting requests.
    """
    def __init__(self):
        self.procs = {}

    def sendMessage(self, dst, msg):
        if dst in self.procs:
            self.procs[dst].deliver(msg)

    def addProc(self, proc):
        self.procs[proc.id] = proc
        proc.start()

    def removeProc(self, pid):
        del self.procs[pid]

    def run(self):
        initialconfig = Config([], [], [])
        c = 0

        # Create replicas
        for i in range(NREPLICAS):
            pid = "replica %d" % i
            Replica(self, pid, initialconfig)
            initialconfig.replicas.append(pid)
        # Create acceptors (initial configuration)
        for i in range(NACCEPTORS):
            pid = "acceptor %d.%d" % (c,i)
            Acceptor(self, pid)
            initialconfig.acceptors.append(pid)
        # Create leaders (initial configuration)
        for i in range(NLEADERS):
            pid = "leader %d.%d" % (c,i)
            Leader(self, pid, initialconfig)
            initialconfig.leaders.append(pid)
        # Send client requests to replicas
        for i in range(NREQUESTS):
            pid = "client %d.%d" % (c,i)
            for r in initialconfig.replicas:
                cmd = Command(pid,0,"operation %d.%d" % (c,i))
                self.sendMessage(r, RequestMessage(pid,cmd))
                time.sleep(1)

        # Create new configurations. The configuration contains the
        # leaders and the acceptors (but not the replicas).
        for c in range(1, NCONFIGS):
            config = Config(initialconfig.replicas, [], [])
            # Create acceptors in the new configuration
            for i in range(NACCEPTORS):
                pid = "acceptor %d.%d" % (c,i)
                Acceptor(self, pid)
                config.acceptors.append(pid)
            # Create leaders in the new configuration
            for i in range(NLEADERS):
                pid = "leader %d.%d" % (c,i)
                Leader(self, pid, config)
                config.leaders.append(pid)
            # Send reconfiguration request
            for r in config.replicas:
                pid = "master %d.%d" % (c,i)
                cmd = ReconfigCommand(pid,0,str(config))
                self.sendMessage(r, RequestMessage(pid, cmd))
                time.sleep(1)
            # Send WINDOW noops to speed up reconfiguration
            for i in range(WINDOW-1):
                pid = "master %d.%d" % (c,i)
                for r in config.replicas:
                    cmd = Command(pid,0,"operation noop")
                    self.sendMessage(r, RequestMessage(pid, cmd))
                    time.sleep(1)
            # Send client requests to replicas
            for i in range(NREQUESTS):
                pid = "client %d.%d" % (c,i)
                for r in config.replicas:
                    cmd = Command(pid,0,"operation %d.%d"%(c,i))
                    self.sendMessage(r, RequestMessage(pid, cmd))
                    time.sleep(1)

    def terminate_handler(self, signal, frame):
        self._graceexit()

    def _graceexit(self, exitcode=0):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(exitcode)

def main():
    e = Env()
    e.run()
    signal.signal(signal.SIGINT, e.terminate_handler)
    signal.signal(signal.SIGTERM, e.terminate_handler)
    signal.pause()


if __name__=='__main__':
    main()
