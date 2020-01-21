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
from PyQt5.QtCore import Qt, pyqtSlot

import view
import model

actions = ['heal', 'wound', 'kill', 'betray', 'defend', 'immobilize', 'condemn', 'beg']
emotions = ['happy', 'sad', 'furious', 'motivated', 'disgusted']
energy_level_list = ['manic', 'excited', 'neutral', 'sluggish', 'lethargic']
rational_level_list = ['logical', 'thoughtful', 'neutral', 'irrational', 'idiotic']
caution_level_list = ['reckless', 'confident', 'neutral', 'reserved', 'risk averse']
entries = []

logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG)

class Controller(QtCore.QObject):
    def __init__(self, model, view):
        '''        
        ? Do I need to make a new instance of the Model when I load a different file?
        '''
        QtCore.QObject.__init__(self)
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
        self.view.newCharBtn.clicked.connect(self.add_character_view)
        self.view.charDetailsBtn.clicked.connect(self.request_char_by_uuid)
        pass

    def add_character_view(self):
        '''

        '''
        if hasattr(self.view, 'char_window'):
            self.view.char_window.show()
        else:
            self.view.add_character_window()
            
    def add_or_edit_character_model(self, data):
        self.model.add_or_edit_character(data)
        self.view.char_window.close()
        self.refresh_view()

    def cancel(self):
        print("canceled")
        self.view.char_window.close()

    def refresh_view(self):
        '''
        update the view with new information

        '''
        for x in range(0, self.view.characterList.count()):
            self.view.characterList.takeItem(x)
        name_list = []
        for item in self.model.data['characters']:
            name_list.append((item['name'], item['uuid']))
        sorted_name_list = sorted(name_list, key=lambda x: x[0])
        for name_uuid in sorted_name_list:
            temp_widget = view.CharListWidgetItem(name_uuid[0], uuid=name_uuid[1])
            self.view.characterList.addItem(temp_widget)
        #self.view.refresh_view(self.model.data)

        pass

    def request_char_by_uuid(self):
        '''
        TODO:
        - Currently I am iterating over the data multiple times,
        first in teh controller and then in the view. I want to only do it once
        Implementing MVC is getting to be more complicated than I expected.
        '''
        if self.view.characterList.count() > 0:
            temp_widget = self.view.characterList.currentItem()
            for char_data in self.model.data['characters']:
                if char_data['uuid'] == temp_widget.uuid:
                    self.view.add_character_window(data=char_data)
                    return
            #handle the error if someone with that uuid cannot be found: delete the entry in the listWidget.
        else:
            return



    def new(self):
        '''
        handles new project request. will always ask to save unsaved changes
        '''
        if self.model.is_dirty:
            result = self.save_prompt()
            if result == QtWidgets.QMessageBox.Save:
                self.save_data()
            elif result == QtWidgets.QMessageBox.Cancel:
                return
        else:
            self.model.start_up()
            return

    def save_prompt(self):
        '''
        convenience function for displaying a save prompt
        '''
        save_prompt = QtWidgets.QMessageBox()
        save_prompt.setText("Story Project has unsaved changes.")
        save_prompt.setInformativeText("Save before closing?")
        save_prompt.setStandardButtons(QtWidgets.QMessageBox.Save |QtWidgets.QMessageBox.Discard |QtWidgets.QMessageBox.Cancel)
        save_prompt.setDefaultButton(QtWidgets.QMessageBox.Save)
        return save_prompt.exec()

    def message_box(self, title='', message='', icon=''):
        '''
        convenience function for displaying a yes/no message window
        '''
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
            if save_prompt_result == QtWidgets.QMessageBox.Save:
                self.save_data()
            else:
                pass

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
        #if a save location has been established, save there.
        if self.model.data['save_dir']:
            self.model.save_data()
        #else, ask where to save and set that as the new save dir
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
    Controller.view.set_controller(Controller)
    Controller.view.show()
    app.exec_()
