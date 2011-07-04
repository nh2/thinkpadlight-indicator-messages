#!/usr/bin/env python

from __future__ import print_function

import sys
import socket
import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop

from thinkpadlight_client import ThinkpadlightClient

def main():
	client = ThinkpadlightClient()

	try:
		with client.connect() as tc:

			# Handler for the "you've got a new message signal" to change the light
			def new_message_changed_handler(status):
				# status is dbus.Boolean and true if there is a new message <=> "envelope green"
				new_message = bool(status)
				if new_message:
					print("Got a new message: turning light on")
				else:
					print("No new messages: turning light off")
				tc.set_light(new_message)

			DBusGMainLoop(set_as_default=True)

			# Subscribe to the currently running session
			bus = dbus.SessionBus()

			# Register handler for the "you've got a new message" signal
			bus.add_signal_receiver(
				new_message_changed_handler,
				dbus_interface='com.canonical.indicator.messages.service',
				signal_name="AttentionChanged",
			)

			gobject.MainLoop().run()

	except socket.error as e:
		if e.errno == 111:  # 111 is "Connection refused"
			print("Connection refused. Please make sure thinkpadlightd is running on %s:%d" % client.addr, file=sys.stderr)
			exit(1)
	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	main()

