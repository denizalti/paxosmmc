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
NREQUESTS = 10
NCONFIGS = 3

class Env:
  def __init__(self):
    self.procs = {}

  def sendMessage(self, dst, msg):
    if dst in self.procs:
      self.procs[dst].deliver(msg)

  def addProc(self, proc):
    self.procs[proc.me] = proc
    proc.start()

  def removeProc(self, pid):
    del self.procs[pid]

  def run(self):
    initialconfig = Config([], [], [])
    c = 0

    for i in range(NREPLICAS):
      pid = "replica: %d" % i
      Replica(self, pid, initialconfig)
      initialconfig.replicas.append(pid)
    for i in range(NACCEPTORS):
      pid = "acceptor: %d.%d" % (c,i)
      Acceptor(self, pid)
      initialconfig.acceptors.append(pid)
    for i in range(NLEADERS):
      pid = "leader: %d.%d" % (c,i)
      Leader(self, pid, initialconfig)
      initialconfig.leaders.append(pid)
    for i in range(NREQUESTS):
      pid = "client: %d.%d" % (c,i)
      for r in initialconfig.replicas:
        self.sendMessage(r, RequestMessage(pid,Command(pid,0,"operation %d.%d" % (c,i))))
        time.sleep(1)

    for c in range(1, NCONFIGS):
      # Create new configuration
      config = Config(initialconfig.replicas, [], [])
      for i in range(NACCEPTORS):
        pid = "acceptor: %d.%d" % (c,i)
        Acceptor(self, pid)
        config.acceptors.append(pid)
      for i in range(NLEADERS):
        pid = "leader: %d.%d" % (c,i)
        Leader(self, pid, config)
        config.leaders.append(pid)
      # Send reconfiguration request
      for r in config.replicas:
        pid = "master: %d.%d" % (c,i)
        self.sendMessage(r, RequestMessage(pid,ReconfigCommand(pid,0,str(config))))
        time.sleep(1)
      for i in range(WINDOW-1):
        pid = "master: %d.%d" % (c,i)
        for r in config.replicas:
          self.sendMessage(r, RequestMessage(pid,Command(pid,0,"operation noop")))
          time.sleep(1)
      for i in range(NREQUESTS):
        pid = "client: %d.%d" % (c,i)
        for r in config.replicas:
          self.sendMessage(r, RequestMessage(pid,Command(pid,0,"operation %d.%d"%(c,i))))
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
