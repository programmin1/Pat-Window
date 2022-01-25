#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  A Winlink User interface

import os
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango
import json
from pandas import read_json

class Listing:
    def __init__(self):
        pass
        
    def show(self):
        """ Create GtkDialog """
        self.builder = Gtk.Builder()
        self.builder.add_from_file('Listing.glade')
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object('MainDialog')
        self.dialog.set_default_size(300,300)
        self.refresh(None)
        self.dialog.show_all()
        
    def refresh(self, btn):
        """ Refresh """
        listbox = self.builder.get_object('list')
        for row in listbox.get_children():
            listbox.remove(row)
        if os.path.exists('/dev/serial/by-id'):
            for entry in os.scandir('/dev/serial/by-id'):
                if not entry.name.startswith('.') and not entry.is_dir():
                    path = os.path.normpath(os.path.join(os.path.dirname(entry.path), os.readlink(entry.path)))
                    print(path)
                    self.addEntry(entry.name, path)
        else:
            self.addEntry("No serial devices detected.","")
        listbox.show_all()
        
    def addEntry(self, label, path):
        listbox = self.builder.get_object('list')
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        lbl = Gtk.Label(label=label)
        lbl.set_ellipsize(Pango.EllipsizeMode.END)
        hbox.pack_start( lbl, True, True, 2 )
        row.path = path
        row.add(hbox)
        listbox.add(row)
        
    def go(self, btn):
        """ Go button connects, opens browser Pat interface. """
        gtklist = self.builder.get_object('list')
        path = gtklist.get_selected_row().path
        #config = read_json( (os.path.expanduser('~/.wl2k/config.json')) )
        #print(config)
        os.system('gksudo kissattach '+path+' wl2k')
        os.system("xdg-open 'http://localhost:8080'")
        os.system('pat http')
        
    def stop(self, btn):
        """ Stop and quit """
        Gtk.main_quit()
        exit;
        
        
        

if __name__ == '__main__':
    dlg = Listing();
    dlg.show()
    Gtk.main()
