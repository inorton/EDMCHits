"""
Thread pool system
"""
from queue import Queue
from threading import Thread
import traceback


class Task(object):
    """
    A queuable function/method call
    """
    target = None
    args = ()
    kwargs = {}


class Pool(object):
    def __init__(self, count, logger):
        self.queue = Queue()
        self.logger = logger
        self.workers = []

        while len(self.workers) != count:
            worker = Worker()
            self.workers.append(worker)
            worker.setQueue(self.queue)
            worker.setPool(self)
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
    pool = None
    finish = False
    queue = None

    def setPool(self, pool):
        """
        Sets the pool for this worker
        :param pool:
        :return:
        """
        self.pool = pool

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
                except Exception as err:
                    print("error: logging exception " + str(err))
                    self.pool.logger.write(traceback.format_exc())
