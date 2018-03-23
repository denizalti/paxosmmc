from utils import BallotNumber
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
          self.active = False
          self.ballot_number = BallotNumber(msg.ballot_number.round+1,
                                            self.id)
          Scout(self.env, "scout:%s:%s" % (str(self.id),
                                           str(self.ballot_number)),
                self.id, self.config.acceptors, self.ballot_number)
      else:
        print "Leader: unknown msg type"
