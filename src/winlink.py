#!/usr/bin/env python3
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
from gi.repository import GdkPixbuf

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
        self.dialog.set_title("Connect AX25 Pat Winlink")
        if os.path.exists('icon.svg'):
            icon_app_path = 'icon.svg'
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_app_path)
            self.dialog.set_icon(pixbuf)
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
        
    def getCall(self, default=''):
        dialogWindow = Gtk.MessageDialog(self.dialog,
                              Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                              Gtk.MessageType.QUESTION,
                              Gtk.ButtonsType.OK_CANCEL,
                              'What is your callsign?')

        dialogBox = dialogWindow.get_content_area()
        userEntry = Gtk.Entry()
        userEntry.set_size_request(250,0)
        dialogBox.pack_end(userEntry, False, False, 0)
        dialogWindow.show_all()
        response = dialogWindow.run()
        text = userEntry.get_text() 
        dialogWindow.destroy()
        if response == Gtk.ResponseType.OK:
            return text
        else:
            return None

        
    def go(self, btn):
        """ Go button connects, opens browser Pat interface. """
        axsetup = False
        # Is axports set with winlink callsign?
        for line in open('/etc/ax25/axports'):
            if len(line.strip()) >0 and line.strip()[0] != '#' and line.find('wl2k')>-1:
                axsetup = True
        if not axsetup:
            call = self.getCall()
            os.system("echo '\nwl2k  "+call+"  1200  128  7 Winlink\n' | pkexec tee -a /etc/ax25/axports ")
            self.setCallConfig(os.path.expanduser('~/.wl2k/config.json'), call)
            self.setCallConfig(os.path.expanduser('~/.config/pat/config.json'), call)
        
        gtklist = self.builder.get_object('list')
        path = gtklist.get_selected_row().path
        #config = read_json( (os.path.expanduser('~/.wl2k/config.json')) )
        #print(config)
        os.system('pkexec kissattach '+path+' wl2k')
        os.system("xdg-open 'http://localhost:8080'")
        os.system('pat http')
        
    def setCallConfig(self, config, call):
        """ Set a Pat configure file """
        output = ""
        if os.path.exists(config):
            for line in open(config,'r'):
                output += line.replace('"mycall": ""', '"mycall": "'+call+'"')
            with open(config, 'w') as outfile:
                outfile.write(output)
        
    def stop(self, btn):
        """ Stop and quit """
        Gtk.main_quit()
        exit;
        
        
        

if __name__ == '__main__':
    dlg = Listing();
    dlg.show()
    Gtk.main()
