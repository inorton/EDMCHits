HITS - Hostile Interaction Tracking System
===========================================
(c) 3303 CMDR Ian Norton [NULL]

HITS is EDMC Plugin that gives risk assessments for ship safety upon jumping
into a star system.

The Plugin integrates with your built-in Remlok display system. It currently
supports the Windowed and Borderless mode but not yet the "FullScreen" mode
when using the "Windows" model of Remlok.

Demo
-----
[![HITS Video](https://img.youtube.com/vi/NIpqUIM_01I/0.jpg)](https://www.youtube.com/watch?v=NIpqUIM_01I)

Installation
-------------

This is easy, you can simply download the HITSSetup.msi from the github releases tab and run the installer.

Command Mode
-------------

HITS can also respond to text inpit. Simply type "!location" to get the HITS
risk report for your current system.

Configuration
--------------
By default HITS will contact the HITS server and obtain a traffic report, if you only want to
use the graphical overlay you can set "Traffic Reports (on/off)" to "off" and HITS will stop checking for
traffic but will still run the overlay server.

Overlay 
========

HITS depends on the EDMCOverlay plugin, be sure to install that first


Overlay API
=============

If you are writing your own plugin and wish to display using the HITS (EDMCOverlay) visual overlay, you can use
our handy python client. `edmcoverlay.py`  You should copy the file into your own plugin and make simple calls 
from there.

Display Model
--------------
Each thing you want to display is best thought of as an actor, each actor is referred to by an ID you choose.

You tell each actor to be a shape, line or text, if you tell actor "hud" to be a square first, then later be only
text the actor will change, the square will dissapear and be replaced with text.

Each actor will stay on the screen for a short period of time (the TTL) and will automatically vanish when this
timer reaches zero.

You control what to render by using the `Overlay` class.
```
from edmcoverlay import Overlay

client = Overlay()
```
The above will create a client object. All graphics (actors) created using this client will exist in your
own private namespace.  Other plugins won't be able to mess with your graphics (but they can probably paint over 
them)

```
def say_hello():
    client.send_message(
      msgid="hello-message",
      text="Hello Commander!",
      color="#ff0000",
      size="normal",
      x=200,
      y=200,
      ttl=10)
```
The above will display red text saying "Hello Commander!" at 200, 200 for 10 seconds.  If you call this code
again before 10 seconds has passed, it will reset the TTL to 10 again.

Colors
-------

The overlay server understands HTML color codes and a few simple names (red, green, blue, yellow) etc.

Text Size
----------

The overlay server understands only "normal" and "large" as text sizes.

Raw Graphic API
----------------

The overlay server can display more complex graphics, you can render simple rectangles or more complex polygons using a vector shape

```
def draw_rectangle():
    client.send_raw({
      "id": "my-rectangle",
      "color": "yellow",
      "fill": "green",
      "shape": "rect",
      "ttl": 20
      "x": 100,
      "y": 400,
      "h": 100,
      "w": 300
    })
```

The above will draw a 300x100 yellow edged, green filled rectangle at 100,400 with a ttl of 20

```
def draw_triangle():
    client.send_raw({
      "id": "my-triangle",
      "color": "blue",
      "shape": "vect",
      "ttl": 10,
      "vector": [
        {
          "x": 100,
          "y": 200,
          "marker": "cross",
          "color": "red",
          "text": "hello"
        },
        {
          "x": 190,
          "y": 240
        },
        {
          "x": 270,
          "y": 480,
          "marker": "circle",
          "color": "green"
        },
        {
          "x": 100,
          "y": 200
        } 
      ]
    })
```

The above should draw a hollow triangle with blue lines, one corner will have a red "x" and the text "hello", 
another corner will have a green circle.
