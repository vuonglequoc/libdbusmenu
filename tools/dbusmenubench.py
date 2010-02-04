#!/usr/bin/env python
"""
A library to communicate a menu object set accross DBus and
track updates and maintain consistency.

Copyright 2010 Canonical Ltd.

Authors:
    Aurélien Gâteau <aurelien.gateau@canonical.com>

This program is free software: you can redistribute it and/or modify it 
under the terms of either or both of the following licenses:

1) the GNU Lesser General Public License version 3, as published by the 
Free Software Foundation; and/or
2) the GNU Lesser General Public License version 2.1, as published by 
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranties of 
MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR 
PURPOSE.  See the applicable version of the GNU Lesser General Public 
License for more details.

You should have received a copy of both the GNU Lesser General Public 
License version 3 and version 2.1 along with this program.  If not, see 
<http://www.gnu.org/licenses/>
"""
import time
import sys
from optparse import OptionParser
from xml.etree import ElementTree as ET

import dbus

DBUS_INTERFACE = "org.ayatana.dbusmenu"
DBUS_SERVICE = "org.dbusmenu.test"
DBUS_PATH = "/MenuBar"


class Chrono(object):
    def __init__(self):
        self._time = 0
        self.restart()

    def restart(self):
        new_time = time.time()
        delta = new_time - self._time
        self._time = new_time
        return delta

    def elapsed(self):
        return time.time() - self._time


def dump_properties(properties, prepend=""):
    for key, value in properties.items():
        print "%s- %s: %s" % (prepend, key, value)


def run_test_sequence(menu, dump=False):
    """
    Runs the test sequence and returns a dict of method_name: seconds
    """
    property_names = ["type", "label", "enabled", "icon-name"]
    times = dict()
    chrono = Chrono()
    revision, layout = menu.GetLayout(dbus.Int32(0))
    times["GetLayout"] = chrono.elapsed()
    if dump:
        print "revision:", revision
        print "layout:"
        print layout

    # Get ids
    tree = ET.fromstring(layout)
    root_id = int(tree.attrib["id"])
    child_element = tree.find("menu")
    assert child_element is not None
    child_id = int(child_element.attrib["id"])

    chrono.restart()
    children = menu.GetChildren(dbus.Int32(root_id), property_names)
    times["GetChildren"] = chrono.elapsed()
    if dump:
        print "children:"
        for child in children:
            id, properties = child
            print "- %d:" % id
            dump_properties(properties, prepend=" ")

    chrono.restart()
    properties = menu.GetProperties(dbus.Int32(child_id), property_names)
    times["GetProperties"] = chrono.elapsed()
    if dump:
        print "properties:"
        dump_properties(properties)

    return times


def main():
    parser = OptionParser(usage = "%prog [options]")

    parser.add_option("-c", "--count", dest="count", type=int, default=1,
                      help="repeat calls COUNT times", metavar="COUNT")
    parser.add_option("-d", "--dump", dest="dump", action="store_true", default=False,
                      help="dump call output to stdout")

    (options, args) = parser.parse_args()

    bus = dbus.SessionBus()
    proxy = bus.get_object(DBUS_SERVICE, DBUS_PATH)
    menu = dbus.Interface(proxy, dbus_interface=DBUS_INTERFACE)

    if options.dump:
        run_test_sequence(menu, dump=True)
        return

    cumulated_timings = dict()
    for x in range(options.count):
        timings = run_test_sequence(menu)
        for name, timing in timings.items():
            cumulated_timings[name] = cumulated_timings.get(name, 0) + timing

    for name, timing in cumulated_timings.items():
        print name, timing / options.count

    return 0


if __name__=="__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et tw=0
