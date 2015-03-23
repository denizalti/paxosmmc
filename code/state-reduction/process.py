import multiprocessing
from threading import Thread

class Process(Thread):
  def __init__(self):
    super(Process, self).__init__()
    self.inbox = multiprocessing.Manager().Queue()

  def run(self):
    try:
      self.body()
      self.env.removeProc(self.me)
    except EOFError:
      print "Exiting.."

  def getNextMessage(self):
    return self.inbox.get()

  def sendMessage(self, dst, msg):
    self.env.sendMessage(dst, msg)

  def deliver(self, msg):
    self.inbox.put(msg)
