#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re
import sys
import time

# since PIP
from PyQt5.QtGui import QIcon, QPixmap, QMouseEvent
from PyQt5.QtCore import Qt, QUrl, QEvent, QPoint, pyqtSignal
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget, QLabel
from PyQt5.QtWebEngineWidgets import *

# globals
app = None
win = None
widgets = [
	{
		'x':		'( 100 - 15 )',
		'y':		'( ( 100 - 50 ) / 2 )',
		'width':	12,
		'height':	50,
		'name':		'Test',
		'url':		'https://google.fr',
		'code': 	'<body style=\"background-color: #5aa;\"></body>'
	}
]

class Window( QMainWindow ):
	_icon = ''
	_title = ''
	_timers = []

	sigborder = pyqtSignal( int )
	sigtoggle = pyqtSignal( int )
	sigrefresh = pyqtSignal( int )
	sigpositions = pyqtSignal()

	def __init__( self, widgets, icon = None, title = None, parent = None ):
		super( Window, self ).__init__( parent )

		self._icon = icon
		self._title = ( title or 'Widgets' )
		self._widgets = widgets

	def setup( self ):
		self.setWindowTitle( self._title )
		self.setWindowFlags( Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput | Qt.WindowDoesNotAcceptFocus | Qt.Tool )
		self.setAttribute( Qt.WA_TranslucentBackground, True )
		self.setAutoFillBackground( False )

		if self._icon:
			icon = QIcon()
			icon.addPixmap( QPixmap( self._icon ), QIcon.Normal, QIcon.Off )
			self.setWindowIcon( icon )

		layout = QGridLayout()
		layout.setContentsMargins( 0, 0, 0, 0 )

		self.centralWidget = QWidget( self )
		self.centralWidget.setAutoFillBackground( False )
		self.centralWidget.setLayout( layout )
		self.setCentralWidget( self.centralWidget )

		self.sigborder.connect( self.border )
		self.sigtoggle.connect( self.toggle_widget )
		self.sigrefresh.connect( self.refresh )
		self.sigpositions.connect( self.positions )

		self.show()
		self.center()
		self.set_widget( self._widgets )

	def center( self ):
		self.move( QPoint( 0, 0 ) )

		size = QApplication.desktop().screenGeometry().size()
		self.setFixedSize( size.width(), size.height() )

		self.positions()

	def positions( self ):
		for num, widget in enumerate( self._widgets ):
			self.set_position( num )

	def border( self, duration = 2 ):
		self.centralWidget.setStyleSheet( 'border: 2px solid #f1c40f;' )

		for i in range( duration * 10 ):
			QApplication.processEvents()
			time.sleep( .1 )

		self.centralWidget.setStyleSheet( 'border: none;' )

	def loaded( self, num, ok = True ):
		widget = self._widgets[ num ]
		if 'browser' in widget:
			if 'background' in widget and widget[ 'background' ]:
				script = ( 'document.body.style.backgroundColor = "%s";' % widget[ 'background' ] )
				widget[ 'browser' ].page().runJavaScript( script, QWebEngineScript.ApplicationWorld )

			#geometry = self.get_geometry( num )
			#event = QMouseEvent( QEvent.MouseMove, QPoint( 1, 1 ), Qt.NoButton, Qt.NoButton, Qt.NoModifier )
			#widget[ 'browser' ].mouseMoveEvent( event )
			#QApplication.instance().sendEvent( widget[ 'browser' ], event )

			widget[ 'browser' ].show()

	def refresh( self, num = -1 ):
		for _num, widget in enumerate( self._widgets ):
			if num < 0 or num == _num:
				widget[ 'browser' ].reload()

	def get_geometry( self, num ):
		swidth = self.width()
		sheight = self.height()
		widget = self._widgets[ num ]

		geometry = {}
		for key in [ 'x', 'y', 'width', 'height' ]:
			val = ( widget[ key ] if key in widget else None )
			if isinstance( val, ( int, str ) ):
				if type( val ) is str:
					for px in re.findall( '[0-9]+px', val ):
						size = swidth
						if key in [ 'y', 'height' ]:
							size = sheight

						rpx = str( ( float( px.replace( 'px', '' ) ) / size ) * 100 )
						val = val.replace( px, rpx )

					if re.compile( '[\s0-9()+*/-]+' ).match( val ):
						val = eval( val )
					else:
						val = None
			else:
				val = None

			if val is None:
				if key in [ 'x', 'y' ]:
					val = 0
				elif key == 'width':
					val = ( 100 - geometry[ 'x' ] )
				elif key == 'height':
					val = ( 100 - geometry[ 'y' ] )

			geometry[ key ] = val

		return ( geometry )

	def set_position( self, num ):
		swidth = self.width()
		sheight = self.height()
		geometry = self.get_geometry( num )

		x = int( swidth * ( geometry[ 'x' ] / 100 ) )
		y = int( sheight * ( geometry[ 'y' ] / 100 ) )
		width = int( swidth * ( geometry[ 'width' ] / 100 ) )
		height = int( sheight * ( geometry[ 'height' ] / 100 ) )

		widget = self._widgets[ num ]
		if 'browser' in widget:
			widget[ 'browser' ].setGeometry( x, y, width, height )

	def set_widget( self, widgets ):
		for num, widget in enumerate( self._widgets ):
			if 'browser' in widget:
				widget[ 'browser' ].setParent( None )
				del widget[ 'browser' ]

		self._widgets = widgets
		for num, widget in enumerate( self._widgets ):
			self.init_browser( num )

	def init_browser( self, num ):
		widget = self._widgets[ num ]
		if 'init' in widget and widget[ 'init' ]:
			return
		widget[ 'init' ] = True

		browser = QWebEngineView( self )
		page = browser.page()
		settings = page.settings()

		page.setBackgroundColor( Qt.transparent )
		settings.setAttribute( QWebEngineSettings.ShowScrollBars, False )
		settings.setAttribute( QWebEngineSettings.ErrorPageEnabled, False )
		#settings.setAttribute( QWebEngineSettings.PrintElementBackgrounds, False )
		settings.setAttribute( QWebEngineSettings.JavascriptCanOpenWindows, False )
		settings.setAttribute( QWebEngineSettings.FocusOnNavigationEnabled, True )
		settings.setAttribute( QWebEngineSettings.LocalContentCanAccessRemoteUrls, True )
		settings.setAttribute( QWebEngineSettings.AllowWindowActivationFromJavaScript, True )

		if 'mute' in widget:
			page.setAudioMuted( widget[ 'mute' ] )

		if 'code' in widget and widget[ 'code' ]:
			url = QUrl( 'http://localhost' )
			browser.setHtml( widget[ 'code' ], url );
		elif 'url' in widget and widget[ 'url' ]:
			url = QUrl( widget[ 'url' ] )
			browser.setUrl( url )

		page.setFeaturePermission( page.url(), QWebEnginePage.MediaAudioVideoCapture, QWebEnginePage.PermissionGrantedByUser )
		widget[ 'browser' ] = browser
		self.set_position( num )

		browser.loadFinished.connect( lambda ok: self.loaded( num, ok ) )

	def toggle_widget( self, num ):
		widget = self._widgets[ num ]
		visible = widget[ 'browser' ].isVisible()

		if visible:
			widget[ 'browser' ].hide()
		else:
			widget[ 'browser' ].show()

		return ( not visible )

def init( wigets, icon = None, title = None ):
	global app, win

	app = QApplication( [] )

	win = Window( wigets, icon, title )
	win.setup()

def exec():
	global app, win

	sys.exit( app.exec_() )

def main( wigets, icon = None, title = None ):
	global win

	init( wigets, icon, title )
	win.sigborder.emit( 2 )
	exec()

if __name__ == '__main__':
	main( widgets, os.path.dirname( __file__ ) + '/../resources/logo.png' )
