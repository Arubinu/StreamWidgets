#!/usr/bin/python
# -*- coding: utf-8 -*-
# pb audio: WEBENGINE_CONFIG += use_proprietary_codecs

import os
import sys
import time

# since PIP
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QLabel, QAction, QWidgetAction, QSystemTrayIcon

from library import window

# defines
APP_ICON = os.path.dirname( __file__ ) + '/resources/logo.png'
APP_TITLE = 'StreamWidgets'
APP_VERSION = '2.0'

# globals
app = None
win = None
last = None
menu = None
screen = 0
options = {}

def systray( app ):
	global APP_ICON, APP_TITLE, APP_VERSION, options

	tray = QSystemTrayIcon( app )
	tray.setIcon( QIcon( APP_ICON ) )

	menu = QMenu()
	menu.setStyleSheet( 'QMenu::item, QLabel { padding: 3px 6px 3px 6px; } QMenu::item:selected, QLabel:hover { background-color: rgba( 0, 0, 0, .1 ); }' )

	action = menu.addAction( '%s v%s' % ( APP_TITLE, APP_VERSION ) )
	action.setEnabled( False )

	menu.addSeparator()

	action = menu.addAction( 'Next Screen' )
	action.triggered.connect( lambda: next_screen() )

	menu.addSeparator()

	# Configuration
	submenu = menu.addMenu( 'Configurations' )
	#! Configuration

	# Widgets
	submenu = menu.addMenu( 'Widgets' )
	#! Widgets

	menu.addSeparator()

	action = menu.addAction( 'Exit' )
	action.triggered.connect( lambda: app.quit() )

	tray.setContextMenu( menu )
	tray.setVisible( True )

	return ( [ tray, menu ] )

def refresh():
	global win, last, options

	try:
		import json
		options = { 'duration': 2, 'screen': 0, 'default': [], 'configs': {} }
		config = os.path.join( os.path.dirname( __file__ ), 'config.json' )
		with open( config, 'rb' ) as f:
			data = json.loads( f.read() )
			for key, value in data.items():
				set_option( key, value )
	except:
		pass

	if 'default' not in options or type( options[ 'default' ] ) is not list or not options[ 'default' ]:
		options[ 'default' ] = []

	if 'configs' not in options or type( options[ 'configs' ] ) is not dict or not options[ 'configs' ]:
		last = None
		options[ 'configs' ] = {}

	submenu = [ action for action in menu.actions() if action.text() == 'Configurations' ][ 0 ].menu()
	submenu.clear()
	try:
		default_action = submenu.addAction( 'Default' )
		default_action.setCheckable( True )
		default_action.triggered.connect( lambda: toggle_config( 'Default' ) )

		checked = False
		if options[ 'configs' ]:
			submenu.addSeparator()
			for name, config in options[ 'configs' ].items():
				if name == last:
					checked = name

				action = submenu.addAction( name )
				action.setCheckable( True )
				action.setChecked( checked and checked == name )
				( lambda name, action: action.triggered.connect( lambda: toggle_config( name ) ) )( name, action )
	except:
		pass
	finally:
		submenu.addSeparator()
		action = QWidgetAction( submenu )
		button = QLabel()
		button.setAlignment( Qt.AlignCenter )
		button.setText( 'Reload' )
		action.setDefaultWidget( button )
		action.triggered.connect( lambda: refresh() )
		submenu.addAction( action )

		default_action.setChecked( not checked )
		toggle_config( checked )

	if options[ 'screen' ] >= 0:
		next_screen( force = options[ 'screen' ] )

def toggle_config( name = None ):
	global win, last, menu, options

	last = ( name if name and ( name == 'Default' or name in options[ 'configs' ] ) else last )
	config = [ action for action in menu.actions() if action.text() == 'Configurations' ][ 0 ].menu()
	for action in config.actions():
		checked = ( not last and action.text() == 'Default' )
		checked = ( checked or action.text() == last )
		action.setChecked( checked )

	widgets = options[ 'default' ]
	if last in options[ 'configs' ]:
		widgets = options[ 'configs' ][ last ]

	submenu = [ action for action in menu.actions() if action.text() == 'Widgets' ][ 0 ].menu()
	submenu.clear()
	try:
		if widgets:
			for num, widget in enumerate( widgets ):
				action = submenu.addAction( widget[ 'name' ] )
				action.setCheckable( True )
				action.setChecked( True )
				( lambda num, action: action.triggered.connect( lambda: toggle_widget( num ) ) )( num, action )
		else:
			action = submenu.addAction( 'No widget' )
			action.setEnabled( False )
	except:
		submenu.clear()
		action = submenu.addAction( 'No widget' )
		action.setEnabled( False )
	finally:
		submenu.addSeparator()
		action = QWidgetAction( submenu )
		button = QLabel()
		button.setAlignment( Qt.AlignCenter )
		button.setText( 'Reload' )
		action.setDefaultWidget( button )
		action.triggered.connect( lambda: toggle_config() )
		submenu.addAction( action )

	win.set_widget( [ widget.copy() for widget in widgets ] )

def toggle_widget( num ):
	global win, menu

	win.sigtoggle.emit( num )

	submenu = [ action for action in menu.actions() if action.text() == 'Widgets' ][ 0 ].menu()
	action = submenu.actions()[ num ]
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

	win.sigpositions.emit()
	win.sigborder.emit( options[ 'duration' ] )

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

		tray, menu = systray( app )

		refresh()

		window.exec()
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	main()
