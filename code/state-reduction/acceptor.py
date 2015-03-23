from utils import PValue
from process import Process
from pvalueset import PValueSet
from message import P1aMessage, P1bMessage, P2aMessage, P2bMessage

class Acceptor(Process):
  def __init__(self, env, me):
    Process.__init__(self)
    self.ballot_number = None
    self.accepted = PValueSet()
    self.me = me
    self.env = env
    self.env.addProc(self)

  def body(self):
    print "Here I am: ", self.me
    while True:
      msg = self.getNextMessage()
      if isinstance(msg, P1aMessage):
        if (self.ballot_number == None or msg.ballot_number > self.ballot_number):
          self.ballot_number = msg.ballot_number
        self.sendMessage(msg.src, P1bMessage(self.me, self.ballot_number, self.accepted))
      elif isinstance(msg, P2aMessage):
        if (self.ballot_number == None or msg.ballot_number >= self.ballot_number):
          self.ballot_number = msg.ballot_number
        self.accepted.add(PValue(msg.ballot_number, msg.slot_number, msg.command))
        self.sendMessage(msg.src, P2bMessage(self.me, self.ballot_number, msg.slot_number))
