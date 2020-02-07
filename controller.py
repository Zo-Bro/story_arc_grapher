# story arc grapher. Allows you to plot out a character's mental state on each story beat,
# use graphing abilities to observe their changes overtime, and how their changes interact
'''
Turn this into a Video Game Narrative Design Tool:
This could eventually be useful in videogame design by adding parameters for production time projections, creating possible asset sheets, and other game-relevant info.
'''
# TODO
# + Need to have a is_dirty flag that gets set when the text in a character entry tab changes.
# + Before letting you move the plot slider, need to check if there are unsaved changes in the character tabs.
# + If so, put up a prompt asking to save the changes. If they deny the prompt,

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
        self.view.saveAsBtn.clicked.connect(lambda: self.save_data(force_save_as=True))
        self.view.newCharBtn.clicked.connect(self.add_character_view)
        self.view.charDetailsBtn.clicked.connect(self.request_char_by_uuid)
        self.view.addEntryBtn.clicked.connect(self.add_beat_to_end_view)
        self.view.plotSlider.valueChanged.connect(lambda: self.view.editEntriesCheckBox.setChecked(False))
        self.view.plotSlider.valueChanged.connect(lambda: self.view.refresh_synopsis_view(self.model.data))
        self.view.plotSlider.valueChanged.connect(self.refresh_tabWidget_edit_state)
        self.view.moveBeatLeftBtn.clicked.connect(self.move_beat_left)
        self.view.moveBeatRightBtn.clicked.connect(self.move_beat_right)
        self.view.insertBeatBtn.clicked.connect(self.insert_beat_view)
        self.view.editEntriesCheckBox.stateChanged.connect(self.refresh_tabWidget_edit_state)
        self.view.applyEditsBtn.clicked.connect(self.apply_entry_edits)
        pass

    def apply_entry_edits(self):
        pass

    def refresh_tabWidget_edit_state(self):
        editable = self.view.editEntriesCheckBox.isChecked()
        if self.view.tabWidget is not None:
            self.view.tabWidget.refresh_edit_state(editable)
            self.view.applyEditsBtn.setEnabled(editable)

    def move_beat_left(self):
        logging.info("inside move_beat_left")
        if len(self.model.data["beats"]) > 0:
            beat_index = self.view.plotSlider.value()
            logging.debug("beat info is {}".format(str(beat_index)))
            if beat_index > 0:
                logging.debug("beat_index is greater than zero")
                beat_to_move = self.model.data["beats"].pop(beat_index)
                self.model.data["beats"].insert(beat_index-1, beat_to_move)
                self.refresh_view()

    def move_beat_right(self):

        beats_max = len(self.model.data["beats"])
        if len(self.model.data["beats"]) > 0:
            beat_index = self.view.plotSlider.value()
            logging.debug("beat info is {}".format(str(beat_index)))
            if beat_index < beats_max:
                logging.debug("beat_index is less than max")
                beat_to_move = self.model.data["beats"].pop(beat_index)
                self.model.data["beats"].insert(beat_index+1, beat_to_move)
                self.refresh_view()

    def add_character_view(self):
        '''
        opens the window for creating a new character
        '''
        if hasattr(self.view, 'char_window'):
                self.view.char_window.refresh_view()
                self.view.char_window.show()
        else:
            self.view.add_character_window()

    def edit_character_view(self):
        if self.view.characterList.count() > 0:
            temp_widget = self.view.characterList.currentItem()
            if temp_widget is not None:
                char_data = self.model.data['characters'][temp_widget.uuid]
                if hasattr(self.view, 'edit_char_window'):
                    self.view.edit_char_window.refresh_view()
                    self.view.edit_char_window.show()
                else:
                    self.view.edit_character_window()
            #handle the error if someone with that uuid cannot be found: delete the entry in the listWidget.
        else:
            return


    def add_character_to_model(self, char_data):
        """

        :param char_data:
        :return:
        """
        self.model.add_character(char_data)
        self.view.char_window.close()
        #create empty entries for all characters that dont have them.
        for char_uuid, char_data in self.model.data['characters'].items():
            for beat_index in range(0, len(self.model.data["beats"])):
                if char_uuid not in self.model.data["beats"][beat_index]["characters"].keys():
                    self.model.create_empty_entry(char_uuid, beat_index)
        self.refresh_view()

    def edit_character_in_model(self, data):
        self.model.edit_character(data)
        self.view.edit_char_window.close()
        self.refresh_view()

    def cancel(self, window_to_close):
        print("canceled")
        window_to_close.close()

    def edit_beat_view(self):
        entry_value = self.view.plotSlider.value()
        self.view.edit_entry_window(append = False, x=entry_value)

    def insert_beat_view(self):
        if self.model.data["characters"]:
            # update the plot slider to the new beat number
            beat_num = self.view.plotSlider.value() + 1
            # open the beat view
            if hasattr(self.view, 'insert_beat_window'):
                self.view.insert_beat_window.refresh_view(self.model.data, beat_num)
                self.view.insert_beat_window.show()
                return
            self.view.insert_beat_at_cursor_window(beat_num)
        else:
            self.message_box(title="No Characters Exist",
                             message="Please create at least one character before adding an entry",
                             icon="warning"
                             )


    def add_beat_to_end_view(self):

        if self.model.data["characters"]:
            # update the plot slider to the new beat number
            beat_num = self.view.plotSlider.maximum()
            # open the beat view
            if hasattr(self.view, 'beat_window'):
                self.view.beat_window.refresh_view(self.model.data, beat_num)
                self.view.beat_window.show()
                return
            self.view.add_beat_to_end_window(beat_num)
        else:
            self.message_box(title="No Characters Exist",
                             message="Please create at least one character before adding an entry",
                             icon="warning"
                             )

    def add_beat_to_end_model(self, beat_data):
        """

        :param beat_data: a dict that contains beat data (see model.beat_entry)
        :return:
        """
        self.model.add_beat(beat_data, append=True)
        self.view.beat_window.close()
        self.view.refresh_view(self.model.data)

    def insert_beat_in_model(self, beat_data, beat_num):

        self.model.add_beat(beat_data, index = beat_num)
        self.view.insert_beat_window.close()
        self.view.refresh_view(self.model.data)

    def refresh_view(self):
        '''
        update the view with new information

        '''
        #update the Tab Widget
        if len(self.model.data["beats"]) > 0:
            if self.view.tabHolder.count() < 0:
                self.view.tabHolder.addWidget(view.EntryPerCharWidget(view = self.view,
                                                                      data = self.model.data,
                                                                      beat_num = self.view.plotSlider.value(),
                                                                      editable = False
                                                                      )
                                              )
            else:
                pass
        self.view.refresh_view(self.model.data)

    def request_char_by_uuid(self):
        '''
        TODO:
        - Currently I am iterating over the data multiple times,
        first in teh controller and then in the view. I want to only do it once
        Implementing MVC is getting to be more complicated than I expected.
        '''
        if self.view.characterList.count() > 0:
            temp_widget = self.view.characterList.currentItem()
            if temp_widget is not None:
                char_data = self.model.data['characters'][temp_widget.uuid]
                self.view.edit_character_window(char_data)
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
            self.view.refresh_view(self.model.data)
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
            self.refresh_view()
        elif type(save_dir) == type(None):
            #message box stating load data is not valid.
            # need to have a custom file type or a "save verification" so bad json doesn't get loaded
            self.message_box(title="Load File is not Valid", message="The path provided is not a valid Story Arc save file. Please try a different path", icon='warning')

    def save_data(self, force_save_as=False):
        # was the save_as button pressed?
        result = None
        if force_save_as:
            save_dir = self.view.save_as_window()
            if save_dir:
                result = self.model.save_data(save_dir=save_dir)
        # if a save location has been established, save there.
        elif self.model.data['save_dir']:
            result = self.model.save_data()
        # else, ask where to save and set that as the new save dir
        else:
            save_dir = self.view.save_as_window()
            if save_dir:
                result = self.model.save_data(save_dir=save_dir)
        # handle assertions
        if result == "success":
            return
        elif result == "not_exist":
            self.message_box("containing folder does not exist",
                             "The containing folder you selected does not exist on disk.",
                             "warning"
                             )
        elif result == "wrong_type":
            self.message_box("file path given not .json",
                             "the file path you gave does not end with '.json', and will not work",
                             "warning"
                             )

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
