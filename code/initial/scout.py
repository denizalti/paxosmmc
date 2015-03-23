from process import Process
from message import P1aMessage,P1bMessage,PreemptedMessage,AdoptedMessage

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

