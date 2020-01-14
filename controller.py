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
import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

import view
import model

actions = ['heal', 'wound', 'kill', 'betray', 'defend', 'immobilize', 'condemn', 'beg']
emotions = ['happy', 'sad', 'furious', 'motivated', 'disgusted']
energy_level_list = ['manic', 'excited', 'neutral', 'sluggish', 'lethargic']
rational_level_list = ['logical', 'thoughtful', 'neutral', 'irrational', 'idiotic']
caution_level_list = ['reckless', 'confident', 'neutral', 'reserved', 'risk averse']
entries = []

logging.basicConfig(filename='log.log', filemode='w', level=logging.INFO)

class Controller(object):
    def __init__(self, model, view):
        '''        
        ? Do I need to make a new instance of the Model when I load a different file?
        '''
        self.model = model
        self.view = view
        self.connect_signals()

    def connect_signals(self):
        '''
        attach callbacks to all buttons
        '''
        self.view.loadBtn.clicked.connect(self.load_data)
        self.view.newBtn.clicked.connect(self.new)
        self.view.saveBtn.clicked.connect(self.save_data)

        #load the ui file
        pass

    def add_character(self, name, age, *args, **kwargs):
        self.model.add_character(name, age, gender, **kwargs)

    def new(self):
        self.model.start_up()
        return

    def save_prompt(self):
        save_prompt = QtWidgets.QMessageBox()
        save_prompt.setText("Story Project has unsaved changes.")
        save_prompt.setInformativeText("Save before closing?")
        save_prompt.setStandardButtons(QtWidgets.QMessageBox.Save |QtWidgets.QMessageBox.Discard |QtWidgets.QMessageBox.Cancel)
        save_prompt.setDefaultButton(QtWidgets.QMessageBox.Save)
        return save_prompt.exec()

    def message_box(self, title='', message='', icon=''):
        icons = {
        'information':QtWidgets.QMessageBox.Information,
        'question':QtWidgets.QMessageBox.Question,
        'warning':QtWidgets.QMessageBox.Warning,
        'critical':QtWidgets.QMessageBox.Critical,
        }
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText(title)
        msg_box.setInformativeText(message)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok |QtWidgets.QMessageBox.Cancel)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.Ok)
        if icon != '':
            msg_box.setIcon(icons[icon])
        return msg_box.exec()


    def load_data(self):
        if self.model.is_dirty:
            # pop up warning and ask if you'd like to save project
            save_prompt_result = self.save_prompt()
            print(save_prompt_result)

        else:
            pass

        save_dir = self.view.load_window()
        if type(save_dir) == str:
            self.model.load_data(save_dir)
            self.view.clear()
            self.view.default_view()
        elif type(save_dir) == type(None):
            #message box stating load data is not valid.
            # need to have a custom file type or a "save verification" so bad json doesn't get loaded
            self.message_box(title="Load File is not Valid", message="The path provided is not a valid Story Arc save file. Please try a different path", icon='warning')

    def save_data(self):
        if self.model.data['save_dir']:
            self.model.save_data()
        else:
            save_dir = self.view.save_as_window()
            if save_dir:
                self.model.save_data(save_dir=save_dir)

    def add_entry(self, character_uuid):
        '''
        Open the 'New Entry' window in the View to get user's input.
        create a new entry in the Model using the user's input

        ? How do I get the character_uuid? Each new entry button should request it from the model it represents.
        '''
        scale_list = self.view.new_entry_window()
        self.model.add_entry(character_uuid, scale_list)



'''
Program Flow:

Run Script
Load Empty View
->User Choice: Start new or open existing.

'''
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Controller = Controller(model = model.Story_Object(), view = view.View())
    Controller.model.start_up()
    Controller.view.show()
    app.exec_()
