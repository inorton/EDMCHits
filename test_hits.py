"""
Send some test data
"""
import Tkinter as tk
tk.PanedWindow()
import load as hits


def test_submit_interdicted():
    """
    We have been interdicted
    :return:
    """
    hits.SERVER.set("localhost:8080")
    msg = {"timestamp": "2016-06-10T14:32:03Z",
           "event": "Interdicted",
           "Submitted": False,
           "Interdictor": "Test data cmdr",
           "IsPlayer": True,
           "Faction": "Timocani Purple Posse"}

    hits.journal_entry("Not a Real Cmdr", "Lave", None, msg, None)


def test_submit_killed():
    """
    We have been killed
    :return:
    """
    hits.SERVER.set("localhost:8080")
    msg = {"timestamp": "2016-06-10T14:32:03Z",
           "event": "Died",
           "KillerName": "Cmdr test data cmdr",
           "KillerShip": "viper",
           "KillerRank": "Deadly"}

    hits.journal_entry("Not a Real Cmdr", "Lave", None, msg, None)


def test_submit_killedwing():
    """
    We have been killed by a wing
    :return:
    """
    hits.SERVER.set("localhost:8080")
    msg = {"timestamp": "2016-06-10T14:32:03Z",
           "event": "Died",
           "Killers":
               [
                   {
                       "Name": "Cmdr test data cmdr",
                       "Ship": "viper",
                       "Rank": "Deadly"
                   },
                   {
                       "Name": "Cmdr test data cmdr2",
                       "Ship": "viper",
                       "Rank": "Deadly"
                   }
               ]
           }

    hits.journal_entry("Not a Real Cmdr", "Lave", None, msg, None)

