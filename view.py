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
from model import UUID
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFileDialog
#import pyqtgraph as pyqtgraph

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
add_entry_ui_file = "add_entry_window.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(ui_file)
Ui_AddCharacterWindow, QtBaseClass = uic.loadUiType(add_char_ui_file)
Ui_EditCharacterWindow, QtBaseClass = uic.loadUiType(edit_char_ui_file)
Ui_AddEntryWindow, QtBaseClass = uic.loadUiType(add_entry_ui_file)


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
        self.tabWidget = EntryPerCharWidget(view=self)
        self.tabHolder.addWidget(self.tabWidget)
        

    def set_controller(self, controller):
        self.controller = controller

    def connect_signals(self):
        """

        :return:
        """

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
        self.refresh_synopsis_view(data)

    def refresh_character_view(self, data):

        #take all items
        # for x in range(0, self.characterList.count() + 1):
        #     self.characterList.takeItem(x)
        #     print(self.characterList.count())
        self.characterList.clear()
        name_list = []
        for key, value in data['characters'].items():
            name_list.append((value['name'], key))
        sorted_name_list = sorted(name_list, key=lambda x: x[0])
        for name_uuid in sorted_name_list:
            temp_widget = CharListWidgetItem(name_uuid[0], uuid=name_uuid[1])
            self.characterList.addItem(temp_widget)

    def refresh_beat_view(self, data):
        if len(data["beats"]) > 1:
            self.plotSlider.setMaximum(len(data["beats"])-1)
        else:
            self.plotSlider.setMaximum(0)

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

    def refresh_synopsis_view(self, data):
        '''
        show what is happening before, now , and next in the story
        based on the position of the plotSlider
        data = the data variable of a model.StoryObject
        '''
        # prep vars
        if len(data["beats"]) == 0:
            return
        prev_entry = True
        next_entry = True
        slider_val = self.plotSlider.value()
        # check if the plot slider is at max or min position
        # so we know whether prev or next text exists in data
        if slider_val == 0:
            prev_entry = False
        else:
            prev_entry_val = slider_val -1

        # slider value starts at 1, beats len starts at 1
        if slider_val == len(data["beats"])-1:
            next_entry = False
        else:
            next_entry_val = slider_val + 1

        # edit the text widgets based on availability of data
        if prev_entry:
            self.prevNameLabel.setText(data["beats"][prev_entry_val]["name"])
            self.prevTextEdit.setPlainText(data["beats"][prev_entry_val]["synopsis"])
        else:
            self.prevNameLabel.setText("...")
            self.prevTextEdit.setPlainText("")
        if next_entry:
            self.nextNameLabel.setText(data["beats"][next_entry_val]["name"])
            self.nextTextEdit.setPlainText(data["beats"][next_entry_val]["synopsis"])
        else:
            self.nextNameLabel.setText("...")
            self.nextTextEdit.setPlainText("")
        self.nowNameLabel.setText(data["beats"][slider_val]["name"])
        self.nowTextEdit.setPlainText(data["beats"][slider_val]["synopsis"])
        self.tabWidget.refresh_view(data, slider_val)


    def insert_beat_window(self, beat_num):
        self.insert_beat_window = AddBeatView(view = self, beat_num=beat_num)
        self.insert_beat_window.send_entry_data.connect(self.controller.insert_beat_in_model)
        self.insert_beat_window.canceled.connect(self.controller.cancel)
        self.insert_beat_window.show()
        return self.insert_beat_window

    def add_beat_to_end_window(self, beat_num):
        self.beat_window = AddBeatView(view = self, beat_num=beat_num)
        self.beat_window.send_entry_data.connect(self.controller.add_beat_to_end_model)
        self.beat_window.canceled.connect(self.controller.cancel)
        self.beat_window.show()
        return self.beat_window

    def edit_entry_window(self, entry_int):
        pass

    def new_scale_window(self):
        pass

    def character_details_window(self, character):
        '''
        show character details/ allow editing.

        '''

    def add_character_window(self):
        '''
        load a pop up window that lets you edit a character or add a new one,
         depending on if you passed in data or not
        returns the window object.
        '''
        self.char_window = AddCharacterView(view = self)
        self.char_window.send_character_data.connect(self.controller.add_character_to_model)
        self.char_window.canceled.connect(self.controller.cancel)
        self.char_window.show()
        return self.char_window

    def edit_character_window(self, data):
        self.edit_char_window = EditCharacterView(view = self, data = data)
        self.edit_char_window.send_character_data.connect(self.controller.edit_character_in_model)
        self.edit_char_window.canceled_signal.connect(self.controller.cancel)
        self.edit_char_window.show()
        return self.edit_char_window

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
            logging.debug("File type for save data to load must be .json")
            return None
        pass

class AddCharacterView(QtWidgets.QWidget, Ui_AddCharacterWindow):
        
        send_character_data = pyqtSignal(dict)
        canceled = pyqtSignal(QtWidgets.QWidget)

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

        def cancel(self):
            self.canceled.emit(self)

        def refresh_view(self):
            self.nameLineEdit.setText("")
            self.ageLineEdit.setText("")
            self.descTextEdit.clear()


class EditCharacterView(QtWidgets.QWidget, Ui_EditCharacterWindow):
    send_character_data = pyqtSignal(dict)
    canceled_signal = pyqtSignal(QtWidgets.QWidget)

    def __init__(self, view = None, data = dict):
        QtWidgets.QWidget.__init__(self)
        Ui_AddCharacterWindow.__init__(self)
        self.view = view
        self.setupUi(self)
        self.connect_signals()
        self.fill_data(data)
        self.data = data

    def connect_signals(self):
        self.addBtn.clicked.connect(self.edit_character)
        self.cancelBtn.clicked.connect(self.cancel)

    def fill_data(self, data):
        self.nameLineEdit.setText(data['name'])
        self.ageLineEdit.setText(data['age'])
        self.descTextEdit.setPlainText(data['desc'])

    def edit_character(self):
        self.data['name'] = self.nameLineEdit.text()
        self.data['age'] = self.ageLineEdit.text()
        self.data['desc'] = self.descTextEdit.toPlainText()
        self.send_character_data.emit(self.data)
        print("set point")

    def cancel(self):
        self.canceled_signal.emit(self)

    def refresh_view(self):
        self.nameLineEdit.setText("")
        self.ageLineEdit.setText("")
        self.descTextEdit.clear()


class AddBeatView(QtWidgets.QWidget, Ui_AddEntryWindow):
    send_entry_data = pyqtSignal(dict)
    canceled = pyqtSignal(QtWidgets.QWidget)

    def __init__(self, view=None, beat_num=int):
        QtWidgets.QWidget.__init__(self)
        Ui_AddEntryWindow.__init__(self)
        self.setupUi(self)
        self.view = view
        self.beat_num = beat_num
        self.create_character_widgets()
        self.connect_signals()

    def connect_signals(self):
        self.addEntryBtn.clicked.connect(self.create_entry)
        self.cancelBtn.clicked.connect(self.cancel)

    def create_character_widgets(self):
        self.tabWidget = EntryPerCharWidget(view=self.view, data=self.view.controller.model.data, beat_num=self.beat_num)
        self.tabHolder.addWidget(self.tabWidget)

    def create_entry(self):
        """
        pull data from the widgets and then format it for the model.
        emit signal and send data.
        """
        text_per_character = []
        for index in range(0, self.tabWidget.tabWidget.count()):
            tab = self.tabWidget.tabWidget.widget(index)
            temp_text = tab.entryTextEdit.toPlainText()
            text_per_character.append((tab.uuid, temp_text))
        self.data = {}
        self.data["name"] = self.nameLineEdit.text()
        self.data["synopsis"] = self.synopsisTextEdit.toPlainText()
        self.data["uuid"] = UUID()
        self.data["characters"]= {}
        for uuid, text in text_per_character:
            self.data["characters"][str(uuid)] = {"uuid":uuid, "scale_list":[0], "notes_list":[text]}
        self.send_entry_data.emit(self.data)

    def cancel(self):
        self.canceled.emit(self)
    def refresh_synopsis_view(self, data):
        '''
        show what is happening before, now , and next in the story
        based on the position of the plotSlider
        data = the data variable of a model.StoryObject
        '''
        # prep vars
        if len(data["beats"]) == 0:
            return
        prev_entry = True
        next_entry = True
        slider_val = self.view.plotSlider.value()
        # check if the plot slider is at max or min position
        # so we know whether prev or next text exists in data
        if slider_val == 0:
            prev_entry = False
        else:
            prev_entry_val = slider_val -1

        # slider value starts at 1, beats len starts at 1
        if slider_val == len(data["beats"])-1:
            next_entry = False
        else:
            next_entry_val = slider_val + 1

        # edit the text widgets based on availability of data
        if prev_entry:
            self.prevNameLabel.setText(data["beats"][prev_entry_val]["name"])
            self.prevTextEdit.setPlainText(data["beats"][prev_entry_val]["synopsis"])
        else:
            self.prevNameLabel.setText("...")
            self.prevTextEdit.setPlainText("")
        if next_entry:
            self.nextNameLabel.setText(data["beats"][next_entry_val]["name"])
            self.nextTextEdit.setPlainText(data["beats"][next_entry_val]["synopsis"])
        else:
            self.nextNameLabel.setText("...")
            self.nextTextEdit.setPlainText("")

    def refresh_view(self, data):
        #self.beat_num = beat_num
        self.nameLineEdit.setText("")
        self.synopsisTextEdit.clear()
        self.tabWidget.
        self.tabWidget.clear_view()
        self.refresh_synopsis_view(data)
        self.create_character_widgets()





class CharListWidgetItem(QtWidgets.QListWidgetItem):
    """
    a custom version of QListWidgetItem so that it stores the uuid for the character with the item
    """
    def __init__(self, *args, uuid='', **kwargs ):
        super().__init__(*args, **kwargs)
        self.uuid = uuid


class EntryPerCharWidget(QtWidgets.QWidget):
    """
    This creates a tabbed view of the specific entry for each character.
    A separate implementation of this will make one tab per entry for a single character.

    """
    def __init__(self, *args, view=None, data=None, beat_num=0, **kwargs):
        """
        data = the entire JSON data contained in the model
        beat_num = the integer for the entry to display

        """
        super().__init__(*args, **kwargs)
        self.view = view
        self.beat_num = beat_num
        self.layout = QtWidgets.QVBoxLayout(self)
        self.tabWidget = QtWidgets.QTabWidget()
        self.layout.addWidget(self.tabWidget)
        self.setLayout(self.layout)
        self.tabs = []
        if data:
            self.create_tabWidget(data)


    def create_tabWidget(self, data=None):
        """
        create the entire tabwidget
        iterates through the entries in a beat and adds a tab for each one it finds

        sets everything to self, so it can be easily referenced
        """
        self.tabs = []

        if len(data["beats"]):
            for char_uuid, char_data in data['beats'][self.beat_num]['characters'].items():
                name = data["characters"][str(char_uuid)]["name"]
                self.tabs.append((self.create_character_tab(entry_character_data = char_data), name, char_uuid))
        else:
            for char_uuid, char_data in data["characters"].items():
                name = char_data["name"]
                self.tabs.append((self.create_character_tab(char_uuid = char_data["uuid"]), name, char_data["uuid"]))
        for tab in self.tabs:
            self.tabWidget.addTab(tab[0], tab[1])


    def create_character_tab(self, entry_character_data=None, char_uuid=str):
        """
        create a character tab, and return the reference to the tab
        Each character tab contains the character's name
        and the entry text for the specified entry_num
        """
        tab = QtWidgets.QWidget()
        tab.layout = QtWidgets.QVBoxLayout(tab)
        tab.entryTextEdit = QtWidgets.QPlainTextEdit()
        tab.layout.addWidget(tab.entryTextEdit)
        if entry_character_data:
            tab.uuid = entry_character_data["uuid"]
            tab.entryTextEdit.setPlainText(entry_character_data["notes_list"][0])
        else:
            tab.uuid = char_uuid
            tab.entryTextEdit.setPlainText("")
        tab.setLayout(tab.layout)
        return tab

    def refresh_view(self, data, beat_num):
        #self.layout = QtWidgets.QVBoxLayout(self)
        #self.tabWidget = QtWidgets.QTabWidget()
        #self.tabs = []
        self.beat_num = beat_num
        self.tabWidget.clear()
        char_uuid_on_file = [tab[2] for tab in self.tabs]
        for char_uuid, char_data in data["characters"].items():
            name = char_data["name"]
            char_entry_data = data["beats"][self.beat_num]["characters"][char_uuid]
            if char_uuid in char_uuid_on_file:
                char_tab_index = char_uuid_on_file.index(char_uuid)
                self.tabs[char_tab_index][0].entryTextEdit.setPlainText(char_entry_data["notes_list"][0])
            #a new character was added since last time.
            else:
                new_tab = self.create_character_tab(entry_character_data=char_entry_data, char_uuid = char_uuid)
                self.tabs.append((new_tab, name, char_uuid))
                self.tabWidget.addTab(self.tabs[-1][0], self.tabs[-1][1])

    def clear_view(self):
        for tab in self.tabs:
                tab[0].entryTextEdit.clear()

