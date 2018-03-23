from utils import BallotNumber
from process import Process
from commander import Commander
from scout import Scout
from message import ProposeMessage, AdoptedMessage, PreemptedMessage

class Leader(Process):
    def __init__(self, env, me, config):
        Process.__init__(self)
        self.active = False
        self.proposals = {}
        self.env = env
        self.me = me
        self.ballot_number = BallotNumber(0, self.me)
        self.config = config
        self.env.addProc(self)

    def body(self):
        print "Here I am: ", self.me

        Scout(self.env, "scout:%s:%s" % (str(self.me), str(self.ballot_number)),
              self.me, self.config.acceptors, self.ballot_number)
        while True:
            msg = self.getNextMessage()
            if isinstance(msg, ProposeMessage):
                if msg.slot_number not in self.proposals:
                    self.proposals[msg.slot_number] = msg.command
                    if self.active:
                        Commander(self.env,
                                  "commander:%s:%s:%s" % (str(self.me),
                                                          str(self.ballot_number),
                                                          str(msg.slot_number)),
                                  self.me, self.config.acceptors, self.config.replicas,
                                  self.ballot_number, msg.slot_number, msg.command)
            elif isinstance(msg, AdoptedMessage):
                if self.ballot_number == msg.ballot_number:
                    for slot_number in msg.accepted.pvalues:
                        self.proposals[slot_number] = msg.accepted.pvalues[slot_number].command
                    for sn in self.proposals:
                        Commander(self.env,
                                  "commander:%s:%s:%s" % (str(self.me),
                                                          str(self.ballot_number),
                                                          str(sn)),
                                  self.me, self.config.acceptors, self.config.replicas,
                                  self.ballot_number, sn, self.proposals.get(sn))
                    self.active = True
            elif isinstance(msg, PreemptedMessage):
                if self.ballot_number < msg.ballot_number:
                    self.active = False
                    self.ballot_number = BallotNumber(msg.ballot_number.round + 1, self.me)
                    Scout(self.env, "scout:%s:%s" % (str(self.me), str(self.ballot_number)),
                          self.me, self.config.acceptors, self.ballot_number)
            else:
                print "Leader: unknown msg type"
