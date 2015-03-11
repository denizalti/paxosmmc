class Message:
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

class DecisionMessage(Message):
  def __init__(self, src, slot_number, command):
    Message.__init__(self, src)
    self.slot_number = slot_number
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
