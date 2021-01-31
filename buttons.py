from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from core import *
import os



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class ButtonView(QLabel):

    def __init__(self, parent, f):
        super().__init__()
        self.setParent(parent)
        self.f = f
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.hovered = False
        self.pressed = False
        self.pixmap_nohover = None
        self.pixmap_hover = None
        self.pixmap_pressed_nohover = None
        self.pixmap_pressed_hover = None
        self.enabled = True
    
    def set_hovered(self, hovered):
        if self.hovered != hovered:
            self.hovered = hovered
            self.update_pixmap()
    
    def set_pressed(self, pressed):
        if self.hovered and self.pressed and not pressed:
            self.press_action()
        self.pressed = pressed
        self.update_pixmap()
    
    def update_pixmap(self):
        if self.hovered and self.pressed:
            self.setPixmap(self.pixmap_pressed_hover)
        elif self.hovered:
            self.setPixmap(self.pixmap_hover)
        elif self.pressed:
            self.setPixmap(self.pixmap_pressed_nohover)
        else:
            self.setPixmap(self.pixmap_nohover)
        self.raise_()
        self.update()

    def press_action(self):
        if self.f != None:
            self.f()
    
    def set_enabled(self, enabled):
        if enabled != self.enabled:
            if enabled:
                self.setVisible(True)
            else:
                self.setVisible(False)
            self.enabled = enabled



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class CloseButtonView(ButtonView):

    def __init__(self, parent, f=None):
        super().__init__(parent, f)
        self.setGeometry(0,0,VALUES.CLOSE_WIDTH, VALUES.CLOSE_HEIGHT)
        self.pixmap_nohover = QPixmap(PATHS.CLOSE_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_hover = QPixmap(PATHS.CLOSE_HOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_nohover = QPixmap(PATHS.CLOSE_PRESSED_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_hover = QPixmap(PATHS.CLOSE_PRESSED_HOVER).scaled(self.width(),self.height())



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class AcceptButtonView(ButtonView):

    def __init__(self, parent, f=None):
        super().__init__(parent, f)
        self.setGeometry(0,0,VALUES.ACCEPT_WIDTH, VALUES.ACCEPT_HEIGHT)
        self.pixmap_nohover = QPixmap(PATHS.ACCEPT_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_hover = QPixmap(PATHS.ACCEPT_HOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_nohover = QPixmap(PATHS.ACCEPT_PRESSED_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_hover = QPixmap(PATHS.ACCEPT_PRESSED_HOVER).scaled(self.width(),self.height())



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class DeleteButtonView(ButtonView):

    def __init__(self, parent, f=None):
        super().__init__(parent, f)
        self.setGeometry(0,0,VALUES.DELETE_WIDTH, VALUES.DELETE_HEIGHT)
        self.pixmap_nohover = QPixmap(PATHS.DELETE_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_hover = QPixmap(PATHS.DELETE_HOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_nohover = QPixmap(PATHS.DELETE_PRESSED_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_hover = QPixmap(PATHS.DELETE_PRESSED_HOVER).scaled(self.width(),self.height())



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class SaveButtonView(ButtonView):

    def __init__(self, parent, f=None):
        super().__init__(parent, f)
        self.setGeometry(0,0,VALUES.SAVE_WIDTH, VALUES.SAVE_HEIGHT)
        self.pixmap_nohover = QPixmap(PATHS.SAVE_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_hover = QPixmap(PATHS.SAVE_HOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_nohover = QPixmap(PATHS.SAVE_PRESSED_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_hover = QPixmap(PATHS.SAVE_PRESSED_HOVER).scaled(self.width(),self.height())



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class LoadButtonView(ButtonView):

    def __init__(self, parent, f=None):
        super().__init__(parent, f)
        self.setGeometry(0,0,VALUES.LOAD_WIDTH, VALUES.LOAD_HEIGHT)
        self.pixmap_nohover = QPixmap(PATHS.LOAD_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_hover = QPixmap(PATHS.LOAD_HOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_nohover = QPixmap(PATHS.LOAD_PRESSED_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_hover = QPixmap(PATHS.LOAD_PRESSED_HOVER).scaled(self.width(),self.height())



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class EditButtonView(ButtonView):

    def __init__(self, parent, f=None):
        super().__init__(parent, f)
        self.setGeometry(0,0,VALUES.EDIT_WIDTH, VALUES.EDIT_HEIGHT)
        self.pixmap_nohover = QPixmap(PATHS.EDIT_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_hover = QPixmap(PATHS.EDIT_HOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_nohover = QPixmap(PATHS.EDIT_PRESSED_NOHOVER).scaled(self.width(),self.height())
        self.pixmap_pressed_hover = QPixmap(PATHS.EDIT_PRESSED_HOVER).scaled(self.width(),self.height())