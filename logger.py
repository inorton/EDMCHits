"""
Thread synchronised log recorder for FlatTrack
"""
import datetime
import os
import traceback
from threading import RLock


class LogContext(object):
    """
    A Logger Class
    """

    def __init__(self):
        self.lock = RLock()
        self.count = 0
        self.maxwrite = 3000
        folder = os.path.abspath(os.path.dirname(__file__))
        self.filename = os.path.join(os.path.dirname(folder), "plugin.log")

    def set_filename(self, filename):
        self.filename = filename

    def rotate_log(self):
        """
        Rotate the current log file
        :return:
        """
        with self.lock:
            try:
                self.count = 0
                filename = self.filename
                moved = filename + ".old"

                if os.path.exists(moved):
                    os.unlink(moved)
                if os.path.exists(filename):
                    os.rename(filename, moved)
            except:
                print traceback.format_exc()

            self.write("Log rotated to {}".format(moved))

    def write(self, message):
        """
        Write a log message
        :param message:
        :return:
        """
        with self.lock:
            self.count += 1

            timestamp = datetime.datetime.utcnow().isoformat()
            try:
                with open(self.filename, "a") as logfile:
                    logfile.write(timestamp + " ")
                    logfile.write(message)
                    logfile.write("\n")
            except:
                print traceback.format_exc()

        if self.count > self.maxwrite:
            self.rotate_log()


LOG = LogContext()
