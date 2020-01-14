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
        model = a variable that loads in from a save file that contains each character's data
        
        ? Do I need to make a new instance of the Model when I load a different file?

        '''
        self.model = model
        self.view = view

    def add_character(self, name, age, *args, **kwargs):
        self.model.add_character(name, age, gender, **kwargs)

    def load_data(self, save_path):
        self.view.clear()
        self.model.load_data(save_path)
        self.view.default_view()

    def save_data(self, save_path=None):
        if save_path:
            self.model.save_data(save_path)
        else:
            self.model.save_data()

    def add_entry(self, character_uuid):
        '''
        Open the 'New Entry' window in the View to get user's input.
        create a new entry in the Model using the user's input

        ? How do I get the character_uuid? Each new entry button should request it from the model it represents.
        '''
        scale_list = self.view.new_entry_window()
        self.model.add_entry(character_uuid, scale_list)


class UUID(object):
    '''
    simple uuid that just creates an integer uuid.
    '''
    def __init__(self):
        temp_uuid = uuid.uuid1()
        return temp_uuid.int


'''
Program Flow:

Run Script
Load Empty View
->User Choice: Start new or open existing.

'''
