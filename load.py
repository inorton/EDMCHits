"""
Plugin for "HITS"
"""
import os
import traceback
import requests
import Tkinter as tk
try:
    import myNotebook as nb
    from config import config
    from EDMCOverlay import edmcoverlay
except ImportError:  ## test mode
    nb = None
    config = dict()
    edmcoverlay = None

from worker import Pool
from logger import LOG
LOG.set_filename(os.path.join(os.path.abspath(os.path.dirname(__file__)), "plugin.log"))

HITS_VERSION = "1.1.0"
EDSM_SERVER = "https://www.edsm.net"
DEFAULT_OVERLAY_MESSAGE_DURATION = 4

PREFNAME_SERVER = "HITSServer"
PREFNAME_OVERLAY_DURATION = "HITSOverlayDuration"
PREFNAME_OVERLAY_HITS_MODE = "HITSOverlayMode"

OVERLAY_MESSAGE_DURATION = tk.StringVar(value=config.get(PREFNAME_OVERLAY_DURATION))
OVERLAY_HITS_MODE = tk.StringVar(value=config.get(PREFNAME_OVERLAY_HITS_MODE))
_overlay = None


def get_display_ttl():
    try:
        return 2 + int(OVERLAY_MESSAGE_DURATION.get())
    except:
        return DEFAULT_OVERLAY_MESSAGE_DURATION


def plugin_start():
    """
    Start up our EDMC Plugin
    :return:
    """
    LOG.write("Loading HITS {}".format(HITS_VERSION))
    global _overlay
    _overlay = edmcoverlay.Overlay()
    notify("ED:HITS Plugin Loaded")

    if not OVERLAY_MESSAGE_DURATION.get():
        OVERLAY_MESSAGE_DURATION.set(str(DEFAULT_OVERLAY_MESSAGE_DURATION))
        config.set(PREFNAME_OVERLAY_DURATION, str(DEFAULT_OVERLAY_MESSAGE_DURATION))
    try:
        OVERLAY_HITS_MODE.get()
    except:
        OVERLAY_HITS_MODE.set("on")

    LOG.write("HITS Overlay mode '{}'".format(OVERLAY_HITS_MODE.get()))


def plugin_stop():
    """
    Edmc is going to exit.
    :return:
    """
    _overlay.send_raw({
        "command": "exit"
    })


HEADER = 380
INFO = 420
DETAIL1 = INFO + 25
DETAIL2 = DETAIL1 + 25
DETAIL3 = DETAIL2 + 25

HTTP_HEADERS = {
    "User-Agent": "EDMC-HITS-" + HITS_VERSION
}

WORKERS = Pool(1)


def display(text, row=HEADER, col=80, color="yellow", size="large"):
    try:
        _overlay.send_message("hits_{}_{}".format(row, col),
                              text,
                              color,
                              80, row, ttl=get_display_ttl(), size=size)
    except:
        pass


def header(text):
    display(text, row=HEADER, size="normal")


def notify(text):
    display(text, row=INFO, color="#00ff00", col=95)


def warn(text):
    display(text, row=INFO, color="red", col=95)


def info(line1, line2=None, line3=None):
    if line1:
        display(line1, row=DETAIL1, col=95, size="normal")
    if line2:
        display(line2, row=DETAIL2, col=95, size="normal")
    if line3:
        display(line3, row=DETAIL3, col=95, size="normal")


def plugin_prefs(parent):
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    nb.Label(frame, text="HITS Configuration").grid(padx=10, row=8, sticky=tk.W)

    nb.Label(frame, text="Overlay Duration (sec)").grid(padx=10, row=11, sticky=tk.W)
    nb.Entry(frame, textvariable=OVERLAY_MESSAGE_DURATION).grid(padx=10, row=11, column=1, sticky=tk.EW)

    nb.Label(frame, text="Traffic Reports (on/off)").grid(padx=10, row=12, sticky=tk.W)
    nb.Entry(frame, textvariable=OVERLAY_HITS_MODE).grid(padx=10, row=12, column=1, sticky=tk.EW)

    return frame


def prefs_changed():
    config.set(PREFNAME_OVERLAY_DURATION, OVERLAY_MESSAGE_DURATION.get())
    config.set(OVERLAY_HITS_MODE, OVERLAY_HITS_MODE.get())


STAR_SYSTEM = None
CURRENT_CMDR = None


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
    global STAR_SYSTEM
    STAR_SYSTEM = system
    global CURRENT_CMDR
    CURRENT_CMDR = cmdr
    LOG.write("Got {} entry".format(entry["event"]))
    if entry["event"] in ["StartJump"] and entry['JumpType'] in ['Hyperspace']:
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


def get_deaths(system):
    """
    Return the death values for the given system
    :param system:
    :return:
    """
    url = "{}/api-system-v1/deaths".format(EDSM_SERVER)

    resp = requests.get(url, params={"systemName": system})
    if resp.status_code == 200:
        return resp.json()["deaths"]

    return {
        "day": 0,
        "week": 0,
        "total": 0,
    }


def get_traffic(system):
    """
    Return the traffic values for the given system
    :param system:
    """
    url = "{}/api-system-v1/traffic".format(EDSM_SERVER)

    resp = requests.get(url, params={"systemName": system})
    if resp.status_code == 200:
        return resp.json()["traffic"]

    return {
        "day": 0,
        "week": 0,
        "total": 0,
    }


def _check_location(system):
    """
    Check EDSM.net for location (may block)
    :param system:
    :return:
    """
    LOG.write("(thread) checking {}...".format(system))
    info(None, line2="Checking location {}..".format(system))
    try:
        deaths = get_deaths(system)
        traffic = get_traffic(system)

        if deaths["day"] > 2:
            warn("Danger: multiple ships lost!")
        else:
            notify("System '{}' is verified low risk.".format(system))

        info("Data for last 24hrs",
             "{} destroyed".format(deaths["day"]),
             "{} passed safely".format(traffic["day"]))
        LOG.write("(thread) ok")
    except Exception as err:
        info(None, line3="Error.. {} {}".format(type(err), err.message))
        LOG.write(traceback.format_exc())
        print type(err)
        print err.message
        print traceback.format_exc()


def check_location(system):
    """
    Get a status report for a system
    :param system:
    :return:
    """
    LOG.write("Check {}".format(system))
    if OVERLAY_HITS_MODE.get() != "off":
        WORKERS.begin(_check_location, system)
