from collections import namedtuple

WINDOW = 5

class BallotNumber(namedtuple('BallotNumber',['round','leader_id'])):
  __slots__ = ()
  def __str__(self):
    return "BN(%d,%s)" % (self.round, str(self.leader_id))

class PValue(namedtuple('PValue',['ballot_number',
                                  'slot_number',
                                  'command'])):
  __slots__ = ()
  def __str__(self):
    return "PV(%s,%s,%s)" % (str(self.ballot_number),
                             str(self.slot_number),
                             str(self.command))

class Command(namedtuple('Command',['client',
                                    'req_id',
                                    'op'])):
  __slots__ = ()
  def __str__(self):
    return "Command(%s,%s,%s)" % (str(self.client),
                                  str(self.req_id),
                                  str(self.op))

class ReconfigCommand(namedtuple('ReconfigCommand',['client',
                                                    'req_id',
                                                    'config'])):
  __slots__ = ()
  def __str__(self):
    return "ReconfigCommand(%s,%s,%s)" % (str(self.client),
                                          str(self.req_id),
                                          str(self.config))

class Config(namedtuple('Config',['replicas',
                                  'acceptors',
                                  'leaders'])):
  __slots__ = ()
  def __str__(self):
    return "%s;%s;%s" % (','.join(self.replicas),
                         ','.join(self.acceptors),
                         ','.join(self.leaders))

