from utils import *
from process import Process
from commander import Commander
from scout import Scout
from message import ProposeMessage, AdoptedMessage, PreemptedMessage
from time import sleep

class Leader(Process):
    """
    Leader receives requests from replicas, serializes requests and
    responds to replicas. Leader maintains four state variables:
    - ballot_number: a monotonically increasing ballot number
    - active: a boolean flag, initially false
    - proposals: a map of slot numbers to proposed commands in the form
    of a set of (slot number, command) pairs, initially empty. At any
    time, there is at most one entry per slot number in the set.
    - timeout: time in seconds the leader waits between operations
    """
    def __init__(self, env, id, config):
        Process.__init__(self, env, id)
        self.ballot_number = BallotNumber(0, self.id)
        self.active = False
        self.proposals = {}
        self.timeout = 1.0
        self.config = config
        self.env.addProc(self)

    def body(self):
        """
        The leader starts by spawning a scout for its initial ballot
        number, and then enters into a loop awaiting messages. There
        are three types of messages that cause transitions:

        - Propose: A replica proposes given command for given slot number

        - Adopted: Sent by a scout, this message signifies that the
        current ballot number has been adopted by a majority of
        acceptors. (If an adopted message arrives for an old ballot
        number, it is ignored.) The set pvalues contains all pvalues
        accepted by these acceptors prior to the adopted ballot
        number.

        - Preempted: Sent by either a scout or a commander, it means
        that some acceptor has adopted the ballot number that is
        included in the message. If this ballot number is higher than
        the current ballot number of the leader, it may no longer be
        possible to use the current ballot number to choose a command.
        """
        print "Here I am: ", self.id
        Scout(self.env, "scout:%s:%s" % (str(self.id), str(self.ballot_number)),
                    self.id, self.config.acceptors, self.ballot_number)
        while True:
            msg = self.getNextMessage()
            if isinstance(msg, ProposeMessage):
                if msg.slot_number not in self.proposals:
                    self.proposals[msg.slot_number] = msg.command
                    if self.active:
                        Commander(self.env,"commander:%s:%s:%s" % (str(self.id),
                                                                   str(self.ballot_number),
                                                                   str(msg.slot_number)),
                                  self.id, self.config.acceptors, self.config.replicas,
                                  self.ballot_number, msg.slot_number, msg.command)
            elif isinstance(msg, AdoptedMessage):
                # Decrease timeout since the leader does not seem to
                # be competing with another leader.
                if self.timeout > TIMEOUTSUBTRACT:
                    self.timeout = self.timeout - TIMEOUTSUBTRACT
                    print self.id, "Timeout decreased: ", self.timeout
                if self.ballot_number == msg.ballot_number:
                    pmax = {}
                    # For every slot number add the proposal with
                    # the highest ballot number to proposals
                    for pv in msg.accepted:
                        if pv.slot_number not in pmax or \
                              pmax[pv.slot_number] < pv.ballot_number:
                            pmax[pv.slot_number] = pv.ballot_number
                            self.proposals[pv.slot_number] = pv.command
                    # Start a commander (i.e. run Phase 2) for every
                    # proposal (from the beginning)
                    for sn in self.proposals:
                        Commander(self.env,
                                  "commander:%s:%s:%s" % (str(self.id),
                                                          str(self.ballot_number),
                                                          str(sn)),
                                  self.id, self.config.acceptors, self.config.replicas,
                                  self.ballot_number, sn, self.proposals.get(sn))
                    self.active = True
            elif isinstance(msg, PreemptedMessage):
                # The leader is competing with another leader
                if msg.ballot_number.leader_id > self.id:
                    # Increase timeout because the other leader has priority
                    self.timeout = self.timeout * TIMEOUTMULTIPLY
                    print self.id, "Timeout increased: ", self.timeout
                if msg.ballot_number > self.ballot_number:
                    self.active = False
                    self.ballot_number = BallotNumber(msg.ballot_number.round+1,
                                                      self.id)
                    Scout(self.env, "scout:%s:%s" % (str(self.id),
                                                     str(self.ballot_number)),
                          self.id, self.config.acceptors, self.ballot_number)

            else:
                print "Leader: unknown msg type"
            sleep(self.timeout)
