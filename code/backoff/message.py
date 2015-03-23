class Message:
    """
    Base class for all messages used in Paxos.
    Every message has a source.
    """
    def __init__(self, src):
        self.src = src

    def __str__(self):
        return str(self.__dict__)

class P1aMessage(Message):
    """
    Sent by Scouts to Acceptors in Phase 1 of Paxos.
    Carries a ballot number.
    """
    def __init__(self, src, ballot_number):
        Message.__init__(self, src)
        self.ballot_number = ballot_number

class P1bMessage(Message):
    """
    Sent by Acceptors to Scouts in Phase 1 of Paxos.
    Carries a ballot number and the set of accepted pvalues.
    """
    def __init__(self, src, ballot_number, accepted):
        Message.__init__(self, src)
        self.ballot_number = ballot_number
        self.accepted = accepted

class P2aMessage(Message):
    """
    Sent by Commanders to Acceptors in Phase 2 of Paxos.
    Carries a ballot number, a slot number and a command.
    """
    def __init__(self, src, ballot_number, slot_number, command):
        Message.__init__(self, src)
        self.ballot_number = ballot_number
        self.slot_number = slot_number
        self.command = command

class P2bMessage(Message):
    """
    Sent by Acceptors to Commanders in Phase 2 of Paxos.
    Carries a ballot number and a slot number.
    """
    def __init__(self, src, ballot_number, slot_number):
        Message.__init__(self, src)
        self.ballot_number = ballot_number
        self.slot_number = slot_number

class PreemptedMessage(Message):
    """
    Sent by Scouts or Commanders to Leaders.
    Carries a ballot number.
    """
    def __init__(self, src, ballot_number):
        Message.__init__(self, src)
        self.ballot_number = ballot_number

class AdoptedMessage(Message):
    """
    Sent by Scouts to Leaders.
    Carries a ballot number and the set of accepted pvalues.
    """
    def __init__(self, src, ballot_number, accepted):
        Message.__init__(self, src)
        self.ballot_number = ballot_number
        self.accepted = accepted

class DecisionMessage(Message):
    """
    Sent by Commanders to Replicas.
    Carries a slot number and a command.
    """
    def __init__(self, src, slot_number, command):
        Message.__init__(self, src)
        self.slot_number = slot_number
        self.command = command

class RequestMessage(Message):
    """
    Sent by Clients to Replicas.
    Carries a command.
    """
    def __init__(self, src, command):
        Message.__init__(self, src)
        self.command = command

class ProposeMessage(Message):
    """
    Sent by Replicas to Leaders.
    Carries a slot number and a command.
    """
    def __init__(self, src, slot_number, command):
        Message.__init__(self, src)
        self.slot_number = slot_number
        self.command = command
