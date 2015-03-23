from utils import PValue
from process import Process
from message import P1aMessage,P1bMessage,P2aMessage,P2bMessage

class Acceptor(Process):
    """
    Acceptors in Paxos maintain the fault tolerant memory of Paxos and
    reply to p1a and p2a messages received from leaders. The Acceptor
    state consists of two variables:
    - ballot_number: a ballot number, initially None.
    - accepted: a set of pvalues, initially empty.
    """
    def __init__(self, env, id):
        Process.__init__(self, env, id)
        self.ballot_number = None
        self.accepted = set()
        self.env.addProc(self)

    def body(self):
        """
        Acceptor receives either p1a or p2a messages:

        - Upon receiving a P1a request message from a leader for a
        ballot number msg.ballot_number, an acceptor makes the
        following transition. First, the acceptor adopts
        msg.ballot_number if and only if it exceeds its current ballot
        number. Then it returns to the leader a p1b response message
        containing its current ballot number and all pvalues accepted
        thus far by the acceptor.

        - Upon receiving a p2a request message from a leader with pvalue
        (b, s, c), an acceptor makes the following transition. If its
        current ballot number equals b, then the acceptor accepts (b,
        s, c). The acceptor returns to the leader a p2b response
        message containing its current ballot number.
        """
        print "Here I am: ", self.id
        while True:
            msg = self.getNextMessage()
            if isinstance(msg, P1aMessage):
                if msg.ballot_number > self.ballot_number:
                    self.ballot_number = msg.ballot_number
                self.sendMessage(msg.src, P1bMessage(self.id, self.ballot_number, self.accepted))
            elif isinstance(msg, P2aMessage):
                if msg.ballot_number == self.ballot_number:
                    self.accepted.add(PValue(msg.ballot_number,msg.slot_number,msg.command))
                self.sendMessage(msg.src, P2bMessage(self.id, self.ballot_number, msg.slot_number))
