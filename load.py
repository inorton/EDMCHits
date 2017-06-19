"""
Plugin for "HITS"
"""
import json
import os
import urllib

import requests
import sys
import time

import Tkinter as tk
import myNotebook as nb
from config import config

HITS_VERSION = "0.2.5"
DEFAULT_SERVER = "edmc.edhits.space"
SERVER = tk.StringVar(value=config.get("HITSServer"))


_thisdir = os.path.abspath(os.path.dirname(__file__))
_overlay_dir = os.path.join(_thisdir, "EDMCOverlay")
if _overlay_dir not in sys.path:
    print "adding {} to sys.path".format(_overlay_dir)
    sys.path.append(_overlay_dir)

try:
    import edmcoverlay
except ImportError:
    print sys.path
    raise Exception(str(sys.path))
_overlay = None


def plugin_start():
    """
    Start up our EDMC Plugin
    :return:
    """
    global _overlay
    global SERVER
    _overlay = edmcoverlay.Overlay()
    time.sleep(2)
    notify("ED:HITS Plugin Loaded")

    if not SERVER.get():
        SERVER.set(DEFAULT_SERVER)
        config.set("HITSServer", DEFAULT_SERVER)

    try:
        check_update()
    except:
        notify("Could not connect to server {}".format(SERVER.get()))


HEADER = 380
INFO = 420
DETAIL1 = INFO + 25
DETAIL2 = DETAIL1 + 25
DETAIL3 = DETAIL2 + 25

HTTP_HEADERS = {
    "User-Agent": "EDMC-HITS-" + HITS_VERSION
}


def display(text, row=HEADER, col=80, color="yellow", size="large"):
    try:
        _overlay.send_message("hits_{}_{}".format(row, col),
                              text,
                              color,
                              80, row, ttl=4, size=size)
    except:
        pass


def header(text):
    display(text, row=HEADER, size="normal")


def notify(text):
    display(text, row=INFO, color="#00ff00", col=95)


def warn(text):
    display(text, row=INFO, color="red", col=95)


def info(line1, line2=None, line3=None):
    display(line1, row=DETAIL1, col=95, size="normal")
    if line2:
        display(line2, row=DETAIL2, col=95, size="normal")
    if line3:
        display(line3, row=DETAIL3, col=95, size="normal")


def plugin_prefs(parent):
    global SERVER
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    nb.Label(frame, text="HITS Configuration").grid(padx=10, row=8, sticky=tk.W)

    nb.Label(frame, text="Server Address").grid(padx=10, row=10, sticky=tk.W)
    nb.Entry(frame, textvariable=SERVER).grid(padx=10, row=10, column=1, sticky=tk.EW)

    return frame


def prefs_changed():
    config.set("HITSServer", SERVER.get())


def journal_entry(cmdr, system, station, entry, state):
    """
    Check a system for advice
    :param cmdr:
    :param system:
    :param station:
    :param entry:
    :param state:
    :return:
    """
    if entry["event"] in ["StartJump"]:
        sysname = entry["StarSystem"]
        header("Checking HITS for {}".format(sysname))
        check_location(sysname)
    if entry["event"] in ["SendText"]:
        if entry["Message"]:
            cmd = entry["Message"]
            if cmd.startswith("!location"):
                if " " in cmd:
                    cmd, system = cmd.split(" ", 1)
                check_location(system)


def compare_versions(ours, other):
    """
    Compare two version strings
    :param ours:
    :param other:
    :return: True if other is greater than ours
    """
    us = ours.split(".", 2)
    thiers = other.split(".", 2)

    if thiers[0] > us[0]:
        return True
    if thiers[0] == us[0]:
        if thiers[1] > us[1]:
            return True
        if thiers[1] == us[1]:
            if thiers[2] > us[2]:
                return True
    return False


def check_update():
    """
    Ask the server if there is an update
    :return:
    """
    resp = requests.get("http://{}/hits/v1/latest".format(
        SERVER.get()),
        headers=HTTP_HEADERS)
    if resp and resp.ok:
        newversion = resp.content
        if compare_versions(HITS_VERSION, newversion):
            info(None, None, "HITS version {} availible".format(newversion))


def check_location(system):
    """
    Get a status report for a system
    :param system:
    :return:
    """
    resp = requests.get("http://{}/hits/v1/location/{}?hours=24".format(
        SERVER.get(), urllib.quote(system)),
        headers=HTTP_HEADERS)

    if resp and resp.status_code == 200:
        data = json.loads(resp.content)
        if "advice" in data:
            if data["advice"]:
                warn(data["advice"])
            else:
                notify("System '{}' is verified low risk.".format(system))

        if "totalVisits" in data:
            info("Data for last {} hrs".format(data["periodHours"]),
                 "{} destroyed".format(data["destroyed"]),
                 "{} arrived safely".format(data["arrived"]))
