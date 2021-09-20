#!/usr/bin/python
# -*- coding: utf-8 -*-
# pb audio: WEBENGINE_CONFIG += use_proprietary_codecs

import os
import sys
import time

# since PIP
import pyautogui
from PyQt5.QtCore import Qt

from library import window

# defines
APP_ICON = os.path.dirname( __file__ ) + '/resources/logo.png'
APP_TITLE = 'StreamWidgets'
APP_VERSION = '1.0'

# globals
app = None
tcs = None
win = None
last = 0
menu = None
screen = 0
options = {}

def systray( app ):
	global APP_ICON, APP_TITLE, APP_VERSION, options

	from PyQt5.QtGui import QIcon
	from PyQt5.QtWidgets import QMenu, QAction, QSystemTrayIcon

	tray = QSystemTrayIcon( app )
	tray.setIcon( QIcon( APP_ICON ) )

	menu = QMenu()
	menu.setStyleSheet( 'QMenu::item, QLabel { padding: 3px 6px 3px 6px; } QMenu::item:selected { background-color: rgba( 0, 0, 0, .1 ); }' )

	action = menu.addAction( '%s v%s' % ( APP_TITLE, APP_VERSION ) )
	action.setEnabled( False )

	menu.addSeparator()

	action = menu.addAction( 'Next Screen' )
	action.triggered.connect( lambda: next_screen() )

	menu.addSeparator()

	# Refresh
	submenu = menu.addMenu( 'Refresh' )

	action = submenu.addAction( 'Widgets' )
	action.triggered.connect( lambda: refresh() )

	action = submenu.addAction( 'Configurations' )
	action.triggered.connect( lambda: refresh( True ) )
	#! Refresh

	# Toggle
	submenu = menu.addMenu( 'Toggle' )
	#! Toggle

	menu.addSeparator()

	action = menu.addAction( 'Exit' )
	action.triggered.connect( lambda: app.quit() )

	tray.setContextMenu( menu )
	tray.setVisible( True )

	return ( [ tray, menu ] )

def refresh( config = False, without_set = False ):
	global win, options

	if not config:
		win.sigrefresh.emit( -1 )
		pyautogui.hotkey( 'alt', 'tab' ) # fix blackscreen
		return

	try:
		import json
		options = { 'duration': 2, 'screen': 0, 'widgets': [] }
		config = os.path.join( os.path.dirname( __file__ ), 'config.json' )
		with open( config, 'rb' ) as f:
			data = json.loads( f.read() )
			for key, value in data.items():
				set_option( key, value )
	except:
		pass

	if 'widgets' not in options or type( options[ 'widgets' ] ) is not list or not options[ 'widgets' ]:
		print( 'No widgets.' )
		return

	if not without_set:
		toggle = [ action for action in menu.actions() if action.text() == 'Toggle' ][ 0 ].menu()
		toggle.clear()
		try:
			if options[ 'widgets' ]:
				for num, widget in enumerate( options[ 'widgets' ] ):
					action = toggle.addAction( widget[ 'name' ] )
					action.setCheckable( True )
					action.setChecked( True )
					( lambda num, action: action.triggered.connect( lambda: toggle_widget( num ) ) )( num, action )
			else:
				action = toggle.addAction( 'No widget' )
				action.setEnabled( False )
		except:
			toggle.clear()
			action = toggle.addAction( 'No widget' )
			action.setEnabled( False )

		if options[ 'screen' ] >= 0:
			next_screen( force = options[ 'screen' ] )

		win.set_widget( options[ 'widgets' ] )

def toggle_widget( num ):
	win.sigtoggle.emit( num )

	toggle = [ action for action in menu.actions() if action.text() == 'Toggle' ][ 0 ].menu()
	action = toggle.actions()[ num ]
	action.toggle()
	action.toggle() # fix toggle

def next_screen( force = None ):
	global app, win, screen

	screen += 1
	screens = app.screens()
	if type( force ) is int and force >= 0:
		screen = force

	screen = ( screen % len( screens ) )
	geometry = screens[ screen ].availableGeometry()

	win.windowHandle().setScreen( screens[ screen ] )
	win.setGeometry( geometry )
	win.showFullScreen()
	pyautogui.hotkey( 'alt', 'tab' ) # fix blackscreen

	win.sigpositions.emit()
	win.sigborder.emit( options[ 'duration' ] )
	win.signotice.emit()

def set_option( name, value ):
	global options

	if name in options and type( options[ name ] ) == type( value ):
		options[ name ] = value

def main():
	global app, win, menu, options

	try:
		window.init( [], APP_ICON, APP_TITLE )
		app = window.app
		win = window.win

		win.setWindowFlags( win.windowFlags() | Qt.Tool )

		tray, menu = systray( app )

		refresh( True )

		window.exec()
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	main()
