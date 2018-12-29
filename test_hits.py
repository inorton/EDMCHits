"""
Send some test data
"""
import Tkinter as tk
tk.PanedWindow()
import load as hits


def test_check_system_traffic():
    traffic = hits.get_traffic("Lave")
    assert "day" in traffic
    assert "week" in traffic
    assert "total" in traffic
    assert traffic["total"] > 0


def test_check_system_deaths():
    deaths = hits.get_deaths("Lave")
    assert "day" in deaths
    assert "week" in deaths
    assert "total" in deaths
    assert deaths["total"] > 0
