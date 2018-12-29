"""
Thread pool system
"""
from Queue import Queue
from threading import Thread
import traceback
from logger import LOG


class Task(object):
    """
    A queuable function/method call
    """
    target = None
    args = ()
    kwargs = {}


class Pool(object):
    def __init__(self, count):
        self.queue = Queue()
        self.workers = []

        while len(self.workers) != count:
            worker = Worker()
            self.workers.append(worker)
            worker.setQueue(self.queue)
            worker.start()

    def begin(self, target, *args, **kwargs):
        """
        Start an operation on the background threads
        :param target:
        :param args:
        :param kwargs:
        :return:
        """
        task = Task()
        task.target = target
        task.args = args
        task.kwargs = kwargs
        self.queue.put_nowait(task)


class Worker(Thread):
    """
    A worker thread
    """

    finish = False
    queue = None

    def setQueue(self, queue):
        """
        Set the queue for this worker
        :param Queue queue:
        :return:
        """
        self.queue = queue

    def start(self):
        self.daemon = True
        super(Worker, self).start()

    def run(self):
        """
        Start processing tasks
        :return:
        """
        while not self.finish:
            task = self.queue.get()
            if task:
                try:
                    task.target(*task.args, **task.kwargs)
                except Exception:
                    LOG.write(traceback.format_exc())
