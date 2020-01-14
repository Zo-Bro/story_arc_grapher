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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

actions = ['heal', 'wound', 'kill', 'betray', 'defend', 'immobilize', 'condemn', 'beg']
emotions = ['happy', 'sad', 'furious', 'motivated', 'disgusted']
energy_level_list = ['manic', 'excited', 'neutral', 'sluggish', 'lethargic']
rational_level_list = ['logical', 'thoughtful', 'neutral', 'irrational', 'idiotic']
caution_level_list = ['reckless', 'confident', 'neutral', 'reserved', 'risk averse']
entries = []

logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG)

ui_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClss = uic.loadUiType(ui_file)
class View(QtWidgets.QMainWindow, Ui_MainWindow):
    '''
    This needs to be initialized as a PyQt View object.

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

    def new_entry_window(self):
        pass

    def edit_entry_window(self, entry_int):
        pass

    def new_scale_window(self):
        pass

    def new_character_window(self):
        pass

    def save_as_window(self):
        print("saved!")
        save_path = QFileDialog.getSaveFileName(self,"Story Project", "./save_files", "Story Arcs (*.json)")
        if save_path:
            logging.debug("Save Story Path: {}".format(save_path))
            return save_path

    def load_window(self):
        print("load")
        load_data = QFileDialog.getOpenFileName(self, "Story Project", "./save_files", "Story Arcs (*.json)")
        
        try:
            ext = os.path.splitext(load_data)[1]
            assert ext == '.json'
            logging.debug("Load Story Path: {}".format(load_data))
            return load_data

        except AssertionError:
            logging.debug("File type for save data to load is not .json")
            return None
        pass

