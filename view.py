# story arc grapher. Allows you to plot out a character's mental state on each story beat,
# use graphing abilities to observe their changes overtime, and how their changes interact
'''
Turn this into a Video Game Narrative Design Tool:
This could eventually be useful in videogame design by adding parameters for production time projections, creating possible asset sheets, and other game-relevant info.
'''


import math
import json
import logging
import uuid
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFileDialog
import pyqtgraph as pyqtgraph

actions = ['heal', 'wound', 'kill', 'betray', 'defend', 'immobilize', 'condemn', 'beg']
emotions = ['happy', 'sad', 'furious', 'motivated', 'disgusted']
energy_level_list = ['manic', 'excited', 'neutral', 'sluggish', 'lethargic']
rational_level_list = ['logical', 'thoughtful', 'neutral', 'irrational', 'idiotic']
caution_level_list = ['reckless', 'confident', 'neutral', 'reserved', 'risk averse']
entries = []

logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG)

ui_file = "mainwindow.ui"
add_char_ui_file = "add_character_window.ui"
edit_char_ui_file = "character_details_window.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(ui_file)
Ui_AddCharacterWindow, QtBaseClass = uic.loadUiType(add_char_ui_file)
Ui_EditCharacterWindow, QtBaseClass = uic.loadUiType(edit_char_ui_file)

class View(QtWidgets.QMainWindow, Ui_MainWindow):
    '''
    App Name: Storiograph
    - This Graph will keep track of the arc as you plot it
    -In the model-controller-view system, this is a view object.
    - Add character arcs
    - Change the level of each point
    - Add a "tension" arc that tracks overall story development

    '''
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        

    def set_controller(self, controller):
        self.controller = controller

    def new(self):
        '''
        start a new project
        '''

    def clear(self):
        '''
        remove all content from the view
        '''
        pass

    def default_view(self):
        '''
        the standard view of the first character and one scale, if either exist
        '''
        pass

    def refresh_view(self, data):
        '''
        refresh all widgets with up to date information

        '''
        self.refresh_character_view(data)
        self.refresh_beat_view(data)
        pass

    def refresh_character_view(self, data):
        pass

    def refresh_beat_view(self, data):
        pass

    def graph_styling(self, grid_x=True, grid_y=True, **kwargs):
        '''
        set the formatting of the graph
        '''
        self.graphWidget.setBackground(kwargs['bg'])
        self.graphWidget.setLabel('left', kwargs['left_label'])
        self.graphWidget.setLabel('bottom', kwargs['bottom_label'])
        self.graphWidget.addLegend()
        self.graphWidget.showGrid(x=grid_x, y=grid_y)
        pass

    def graph_data(self, character_names=[], y_axis_per_character=[]):
        '''
        refresh the graph with data about a character
        Controller will gather data from model and insert into this func.
        How should controller handle that?
        '''
        len_per_char = [len(char) for char in y_axis_per_character]
        x_len = max(len_per_char)
        x_axis = [i+1 for i in range(0, x_len)]
        max_per_char = [max(char) for char in y_axis_per_character]
        y_len = max(max_per_char)

        self.graphWidget.setXRange(0,x_len, padding=1)
        self.graphWidget.setYRange(0, y_len, padding=1)

        for char in y_axis_per_character:
            name = y_axis_per_character.index()
            self.graphWidget.plot(x_axis, char, ) # x, y, legend, color
        pass

    def new_entry_window(self):
        pass

    def edit_entry_window(self, entry_int):
        pass

    def new_scale_window(self):
        pass

    def character_details_window(self, character):
        '''
        show character details/ allow editing.

        '''

    def add_character_window(self, data=None):
        '''
        load a pop up window that lets you edit a character or add a new one,
         depending on if you passed in data or not
        returns the window object.
        '''
        if data:
            self.char_window = EditCharacterView(view = self, data=data)
        else:
            self.char_window = AddCharacterView(view = self)

        self.char_window.send_character_data.connect(self.controller.add_or_edit_character_model)
        self.char_window.canceled.connect(self.controller.cancel)
        self.char_window.show()
        return self.char_window

    def save_as_window(self):
        print("saved!")
        save_path, _filter = QFileDialog.getSaveFileName(self,"Story Project", "./save_files", "Story Arcs (*.json)")
        if save_path:
            logging.debug("Save Story Path: {}".format(save_path))
            return save_path

    def load_window(self):
        print("load")
        load_data, _filter = QFileDialog.getOpenFileName(self, "Story Project", "./save_files", "Story Arcs (*.json)")
        try:
            ext = os.path.splitext(load_data)[1]
            assert ext == '.json'
            logging.debug("Load Story Path: {}".format(load_data))
            return load_data

        except AssertionError:
            logging.debug("File type for save data to load is not .json")
            return None
        pass

class AddCharacterView(QtWidgets.QWidget, Ui_AddCharacterWindow):
        
        send_character_data = pyqtSignal(dict)
        canceled = pyqtSignal()

        def __init__(self, view=None):
            QtWidgets.QWidget.__init__(self)
            Ui_AddCharacterWindow.__init__(self)
            self.setupUi(self)
            self.view = view
            self.connect_signals()

        def connect_signals(self):
            self.addBtn.clicked.connect(self.create_character)
            self.cancelBtn.clicked.connect(self.cancel)

        def create_character(self):
            self.data = {}
            self.data['name']= self.nameLineEdit.text()
            self.data['age'] = self.ageLineEdit.text()
            self.data['desc'] = self.descTextEdit.toPlainText()
            self.send_character_data.emit(self.data)
            print("set point")

        def cancel(self):
            self.canceled.emit()


class EditCharacterView(QtWidgets.QWidget, Ui_EditCharacterWindow):
    send_character_data = pyqtSignal(dict)
    canceled = pyqtSignal()

    def __init__(self, view = None, data = dict):
        QtWidgets.QWidget.__init__(self)
        Ui_AddCharacterWindow.__init__(self)
        self.view = view
        self.setupUi(self)
        self.connect_signals()
        self.fill_data(data)

    def connect_signals(self):
        self.addBtn.clicked.connect(self.create_character)
        self.cancelBtn.clicked.connect(self.cancel)

    def fill_data(self, data):
        self.nameLineEdit.setText(data['name'])
        self.ageLineEdit.setText(data['age'])
        self.descTextEdit.setPlainText(data['desc'])

    def create_character(self):
        self.data = {}
        self.data['name'] = self.nameLineEdit.text()
        self.data['age'] = self.ageLineEdit.text()
        self.data['desc'] = self.descTextEdit.toPlainText()
        self.send_character_data.emit(self.data)
        print("set point")

    def cancel(self):
        self.canceled.emit()


class CharListWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, *args, uuid='', **kwargs ):
        super().__init__(*args, **kwargs)
        self.uuid = uuid


