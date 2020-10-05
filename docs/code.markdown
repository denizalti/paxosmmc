---
layout: page
title: Code
permalink: /code/
---

The Python source code corresponding to the pseudo-code we present in this website is available in the following [git repository](https://github.com/denizalti/paxosmmc):

<pre>https://github.com/denizalti/paxosmmc</pre>

You can clone the repo as follows:
<pre><code>$ git clone https://github.com/denizalti/paxosmmc.git
</code></pre>

The source code includes the Replica, Acceptor, Commander, Scout and Leader codes as well as Utilities, Message, Process and Environment codes that implement the functionality to run the processes.

# Replica

A replica runs in an infinite loop, receiving messages. Replicas receive two kinds of messages: requests and decisions. When it receives a request for command c from a client, the replica adds the request to set requests. Next, the replica invokes the function <span style="font-family:Courier New">propose()</span>.

Function <span style="font-family:Courier New">propose()</span> tries to transfer requests from the set <span style="font-family:Courier New">requests</span> to <span style="font-family:Courier New">proposals</span>. It uses <span style="font-family:Courier New">slot_in</span> to look for unused slots within the window of slots with known configurations. For each such slot s, it first checks if the configuration for s is different from the prior slot by checking if the decision in slot <span style="font-family:Courier New">s−WINDOW</span> is a reconfiguration command. If so, the function updates the set of leaders for slot s. Then the function removes a request r from requests and adds proposal (s,r) to the set proposals. Finally, it sends a ⟨propose, s, c⟩ message to all leaders in the configuration of slot s.

Decisions may arrive out-of-order and multiple times. For each decision message, the replica adds the decision to the set decisions. Then, in a loop, it considers which decisions are ready for execution before trying to receive more messages. If there is a decision c' corresponding to the current slot_out, the replica first checks to see if it has proposed a command c'' for that slot. If so, the replica removes ⟨<span style="font-family:Courier New">slot_out</span>,c''⟩ from the set proposals. If c''≠ c', that is, the replica proposed a different command for that slot, the replica returns c'' to set requests so c'' is proposed again at a later time. Next, the replica invokes <span style="font-family:Courier New">perform(</span>c'<span style="font-family:Courier New">)</span>.

The function <span style="font-family:Courier New">perform()</span> is invoked with the same sequence of commands at all replicas. First, it checks to see if it has already performed the command. Different replicas may end up proposing the same command for different slots, and thus the same command may be decided multiple times. The corresponding operation is evaluated only if the command is new and it is not a reconfiguration request. If so, <span style="font-family:Courier New">perform()</span> applies the requested operation to the application state. In either case, the function increments <span style="font-family:Courier New">slot_out</span>.

<pre><code>from process import Process
from message import ProposeMessage,DecisionMessage,RequestMessage
from utils import *
import time

class Replica(Process):
  def __init__(self, env, id, config):
    Process.__init__(self, env, id)
    self.slot_in = self.slot_out = 1
    self.proposals = {}
    self.decisions = {}
    self.requests = []
    self.config = config
    self.env.addProc(self)

  def propose(self):
    while len(self.requests) != 0 and self.slot_in < self.slot_out+WINDOW:
      if self.slot_in > WINDOW and self.slot_in-WINDOW in self.decisions:
        if isinstance(self.decisions[self.slot_in-WINDOW],ReconfigCommand):
          r,a,l = self.decisions[self.slot_in-WINDOW].config.split(';')
          self.config = Config(r.split(','),a.split(','),l.split(','))
          print self.id, ": new config:", self.config
      if self.slot_in not in self.decisions:
        cmd = self.requests.pop(0)
        self.proposals[self.slot_in] = cmd
        for ldr in self.config.leaders:
          self.sendMessage(ldr, ProposeMessage(self.id,self.slot_in,cmd))
      self.slot_in +=1

  def perform(self, cmd):
    for s in range(1, self.slot_out):
      if self.decisions[s] == cmd:
        self.slot_out += 1
        return
    if isinstance(cmd, ReconfigCommand):
      self.slot_out += 1
      return
    print self.id, ": perform",self.slot_out, ":", cmd
    self.slot_out += 1

  def body(self):
    print "Here I am: ", self.id
    while True:
      msg = self.getNextMessage()
      if isinstance(msg, RequestMessage):
        self.requests.append(msg.command)
      elif isinstance(msg, DecisionMessage):
        self.decisions[msg.slot_number] = msg.command
        while self.slot_out in self.decisions:
          if self.slot_out in self.proposals:
            if self.proposals[self.slot_out]!=self.decisions[self.slot_out]:
              self.requests.append(self.proposals[self.slot_out])
            del self.proposals[self.slot_out]
          self.perform(self.decisions[self.slot_out])
      else:
        print "Replica: unknown msg type"
      self.propose()
</code></pre>      

# Acceptor
An **acceptor** runs in an infinite loop, receiving two kinds of request messages from leaders:

* **P1aMessage**: Upon receiving a “Phase 1a” request message from a leader for a ballot number, an acceptor makes the following transition. First, the acceptor adopts <span style="font-family:Courier New">msg.ballot_number</span> if and only if it exceeds its current ballot number. Then it returns to the leader a “Phase 1b” response message containing its current ballot number and all pvalues accepted thus far by the acceptor.

* **P2aMessage**: Upon receiving a “Phase 2a” request message from a leader with a pvalue, an acceptor makes the following transition. If <span style="font-family:Courier New">msg.ballot_number</span> equals the current ballot number, then the acceptor accepts the pvalue. The acceptor returns to the leader a “Phase 2b” response message containing its current ballot number.


<pre><code>from utils import PValue
from process import Process
from message import P1aMessage, P1bMessage, P2aMessage, P2bMessage

class Acceptor(Process):
  def __init__(self, env, id):
    Process.__init__(self, env, id)
    self.ballot_number = None
    self.accepted = set()
    self.env.addProc(self)

  def body(self):
    print "Here I am: ", self.id
    while True:
      msg = self.getNextMessage()
      if isinstance(msg, P1aMessage):
        if msg.ballot_number > self.ballot_number:
          self.ballot_number = msg.ballot_number
        self.sendMessage(msg.src,
                         P1bMessage(self.id,
                                    self.ballot_number,
                                    self.accepted))
      elif isinstance(msg, P2aMessage):
        if msg.ballot_number == self.ballot_number:
          self.accepted.add(PValue(msg.ballot_number,
                                   msg.slot_number,
                                   msg.command))
        self.sendMessage(msg.src,
                         P2bMessage(self.id,
                                    self.ballot_number,
                                    msg.slot_number))
</code></pre>

# Scout
Scouts send and track the P1a and P1b messages, handling the first part of
a round.

<pre><code>from process import Process
from message import P1aMessage, P1bMessage, PreemptedMessage, AdoptedMessage

class Scout(Process):
  def __init__(self, env, id, leader, acceptors, ballot_number):
    Process.__init__(self, env, id)
    self.leader = leader
    self.acceptors = acceptors
    self.ballot_number = ballot_number
    self.env.addProc(self)

  def body(self):
    waitfor = set()
    for a in self.acceptors:
      self.sendMessage(a, P1aMessage(self.id, self.ballot_number))
      waitfor.add(a)

    pvalues = set()
    while True:
      msg = self.getNextMessage()
      if isinstance(msg, P1bMessage):
        if self.ballot_number == msg.ballot_number and msg.src in waitfor:
          pvalues.update(msg.accepted)
          waitfor.remove(msg.src)
          if len(waitfor) < float(len(self.acceptors))/2:
            self.sendMessage(self.leader,
                             AdoptedMessage(self.id,
                                            self.ballot_number,
                                            pvalues))
            return
        else:
          self.sendMessage(self.leader,
                           PreemptedMessage(self.id,
                                            msg.ballot_number))
          return
      else:
        print "Scout: unexpected msg"
</code></pre>

# Commander
Commanders send and track the P2a and P2b messages, handling the first part of
a round.

from message import P2aMessage, P2bMessage, PreemptedMessage, DecisionMessage
from process import Process
from utils import Command

<pre><code>
class Commander(Process):
  def __init__(self, env, id, leader, acceptors, replicas,
               ballot_number, slot_number, command):
    Process.__init__(self, env, id)
    self.leader = leader
    self.acceptors = acceptors
    self.replicas = replicas
    self.ballot_number = ballot_number
    self.slot_number = slot_number
    self.command = command
    self.env.addProc(self)

  def body(self):
    waitfor = set()
    for a in self.acceptors:
      self.sendMessage(a, P2aMessage(self.id, self.ballot_number,
                                     self.slot_number, self.command))
      waitfor.add(a)

    while True:
      msg = self.getNextMessage()
      if isinstance(msg, P2bMessage):
        if self.ballot_number == msg.ballot_number and msg.src in waitfor:
          waitfor.remove(msg.src)
          if len(waitfor) < float(len(self.acceptors))/2:
            for r in self.replicas:
              self.sendMessage(r, DecisionMessage(self.id,
                                                  self.slot_number,
                                                  self.command))
            return
        else:
          self.sendMessage(self.leader, PreemptedMessage(self.id, msg.ballot_number))
          return
</code></pre>    

# Leader
The Leader code is executed by the Replica that becomes the leader for a given
round after the P1 and P2 rounds are completed successfully.

<pre><code>from utils import BallotNumber
from process import Process
from commander import Commander
from scout import Scout
from message import ProposeMessage,AdoptedMessage,PreemptedMessage

class Leader(Process):
  def __init__(self, env, id, config):
    Process.__init__(self, env, id)
    self.ballot_number = BallotNumber(0, self.id)
    self.active = False
    self.proposals = {}
    self.config = config
    self.env.addProc(self)

  def body(self):
    print "Here I am: ", self.id
    Scout(self.env, "scout:%s:%s" % (str(self.id), str(self.ballot_number)),
          self.id, self.config.acceptors, self.ballot_number)
    while True:
      msg = self.getNextMessage()
      if isinstance(msg, ProposeMessage):
        if msg.slot_number not in self.proposals:
          self.proposals[msg.slot_number] = msg.command
          if self.active:
            Commander(self.env,
                      "commander:%s:%s:%s" % (str(self.id),
                                              str(self.ballot_number),
                                              str(msg.slot_number)),
                      self.id, self.config.acceptors, self.config.replicas,
                      self.ballot_number, msg.slot_number, msg.command)

      elif isinstance(msg, AdoptedMessage):
        if self.ballot_number == msg.ballot_number:
          pmax = {}
          for pv in msg.accepted:
            if pv.slot_number not in pmax or \
                  pmax[pv.slot_number] < pv.ballot_number:
              pmax[pv.slot_number] = pv.ballot_number
              self.proposals[pv.slot_number] = pv.command
          for sn in self.proposals:
            Commander(self.env,
                      "commander:%s:%s:%s" % (str(self.id),
                                              str(self.ballot_number),
                                              str(sn)),
                      self.id, self.config.acceptors, self.config.replicas,
                      self.ballot_number, sn, self.proposals.get(sn))
          self.active = True
      elif isinstance(msg, PreemptedMessage):
        if msg.ballot_number > self.ballot_number:
          self.ballot_number = BallotNumber(msg.ballot_number.round+1,
                                            self.id)
          Scout(self.env, "scout:%s:%s" % (str(self.id),
                                           str(self.ballot_number)),
                self.id, self.config.acceptors, self.ballot_number)
        self.active = False
      else:
        print "Leader: unknown msg type"
</code></pre>        

# Environment
This is the main code in which all processes are created and run. This code also simulates a set of clients submitting requests.

<pre><code>import os, signal, sys, time
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
NCONFIGS = 2

class Env:
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
    for i in r in initialconfig.replicas:
        cmd = Command(pid,0,"operation %d.%d" %.sleep(1)

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
        cmd = ReconfigCommand(pid,0,str(config))
        self.sendMessage(r, RequestMessage(pid, cmd))
        time.sleep(1)
      for i in range(WINDOW-1):
        pid = "master: %d.%d" % (c,i)
        for r in config.replicas:
          cmd = Command(pid,0,"operation noop")
          self.sendMessage(r, RequestMessage(pid, cmd))
          time.sleep(1)
      for i in range(NREQUESTS):
        pid = "client: %d.%d" % (c,i)
        for r inconfig.replicas:
          cmd = Command(pid,0,(1)

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
</code></pre>

# Process
A process is a thread with a process identifier, a queue of incoming messages, and an “environment” that keeps track of all processes and queues.

<pre><code>import multiprocessing
from threading import Thread

class Process(Thread):
  def __init__(self, env, id):
    super(Process, self).__init__()
    self.inbox = multiprocessing.Manager().Queue()
    self.env = env
    self.id = id

  def run(self):
    try:
      self.body()
      self.env.removeProc(self.id)
    except EOFError:
      print "Exiting.."

  def getNextMessage(self):
    return self.inbox.get()

  def sendMessage(self, dst, msg):
    self.env.sendMessage(dst, msg)

  def deliver(self, msg):
    self.inbox.put(msg)
</code></pre>

#Message
Paxos uses a large variety of message types. They are collected below.

<pre><code>class Message:
  def __init__(self, src):
    self.src = src

  def __str__(self):
    return str(self.__dict__)

class P1aMessage(Message):
  def __init__(self, src, ballot_number):
    Message.__init__(self, src)
    self.ballot_number = ballot_number

class P1bMessage(Message):
  def __init__(self, src, ballot_number, accepted):
    Message.__init__(self, src)
    self.ballot_number = ballot_number
    self.accepted = accepted

class P2aMessage(Message):
  def __init__(self, src, ballot_number, slot_number, command):
    Message.__init__(self, src)
    self.ballot_number = ballot_number
    self.slot_number = slot_number
    self.command = command

class P2bMessage(Message):
  def __init__(self, src, ballot_number, slot_number):
    Message.__init__(self, src)
    self.ballot_number = ballot_number
    self.slot_number = slot_number

class PreemptedMessage(Message):
  def __init__(self, src, ballot_number):
    Message.__init__(self, src)
    self.ballot_number = ballot_number

class AdoptedMessage(Message):
  def __init__(self, src, ballot_number, accepted):
    Message.__init__(self, src)
    self.ballot_number = ballot_number
    self.accepted = accepted

class DecisionMessage(= slot_number
    self.command = command

class RequestMessage(Message):
  def __init__(self, src, command):
    Message.__init__(self, src)
    self.command = command

class ProposeMessage(Message):
  def __init__(self, src, slot_number, command):
    Message.__init__(self, src)
    self.slot_number = slot_number
    self.command = command
</code></pre>

# Utilities
A ballot number is a lexicographically ordered pair of an integer and the identifier of the ballot's leader.
A pvalue consists of a ballot number, a slot number, and a command.
A command consists of the process identifier of the client submitting the request, a client-local request identifier, and an operation (which can be anything).
A reconfiguration command consists of the process identifier of the client submitting the request, a client-local request identifier, and a configuration.
A configuration consists of a list of replicas, a list of acceptors and a list of leaders.

<pre><code>from collections import namedtuple

WINDOW = 5

class BallotNumber(namedtuple('BallotNumber',['round','leader_id'])):
  __slots__ = ()
  def __str__(self):
    return "BN(%d,%s)" % (self.round, str(self.leader_id))

class PValue(namedtuple('PValue',['ballot_number','slot_number','command'])):
  __slots__ = ()
  def __str__(self):
    return "PV(%s,%s,%s)" % (str(self.ballot_number),
                             str(self.slot_number),
                             str(self.command))

class Command(namedtuple('Command',['client','req_id','op'])):
  __slots__ = ()
  def __str__(self):
    return "Command(%s,%s,%s)" % (str(self.client),
                                  str(self.req_id),
                                  str(self.op))

class ReconfigCommand(namedtuple('ReconfigCommand',['client','req_id','config'])):
  __slots__ = ()
  def __str__(self):
    return "ReconfigCommand(%s,%s,%s)" % (str(self.client),
                                          str(self.req_id),
                                          str(self.config))

class Config(namedtuple('Config',['replicas','acceptors','leaders'])):
  __slots__ = ()
  def __str__(self):
    return "%s;%s;self.leaders))
</code></pre>    
