# story arc grapher. Allows you to plot out a character's mental state on each story beat,
# use graphing abilities to observe their changes overtime, and how their changes interact
'''
Turn this into a Video Game Narrative Design Tool:
This could eventually be useful in videogame design by adding parameters for production time projections,
creating possible asset sheets, and other game-relevant info.
'''
#ToDo:
# + implement the "Add entry to end" button
# + implement the entry per character  tabWidget
# + I created "Character" and "Beat" classes.
#   These are causing disparity between the model.data that gets loaded (which is just JSON)
#   and  the classes that exist in-memory for newly created objects. I think I need to turn
#   the classes into functions instead, that way they only return json data instead of returning
#   class objects.

import math
import json
import logging
import uuid
import os
actions = ['heal', 'wound', 'kill', 'betray', 'defend', 'immobilize', 'condemn', 'beg']
emotions = ['happy', 'sad', 'furious', 'motivated', 'disgusted']
energy_level_list = ['manic', 'excited', 'neutral', 'sluggish', 'lethargic']
rational_level_list = ['logical', 'thoughtful', 'neutral', 'irrational', 'idiotic']
caution_level_list = ['reckless', 'confident', 'neutral', 'reserved', 'risk averse']
entries = []

logging.basicConfig(filename='log.log', filemode='w', level=logging.INFO)
_logger = logging.log

class Story_Object(object):
    '''
    You refresh a view object by using model.layoutchanged.emit() or some similar .emit() call
    This Model will contain a story object, which is the "Project" file. 
    The Characters will exist within, 
    and there will be some other data specific to the Project File stored here.
    '''
    def __init__(self):
        '''
        args:
        scale_dict (DICT) =  key (STR): a UUID for the user's defined scale; value (STR): the name of the scale, given by the user
        uuid (STR) = a unique ID for the story itself
        save_dir (STR) =  an absolute path to the location where the save data exists
        '''
        self.empty_story_object = {
                                    "name":"",
                                    "uuid":"",
                                    "color_theme":[],
                                    "save_dir":"",
                                    "scale_dict":{},
                                    "characters":{},
                                    "beats":[]
        }
        self.start_up()



    def start_up(self, save_dir=None):
        '''
        This function runs when a user wants to work on a story project
        There are two options: Load a saved file, or start a new untitled.
        '''
        if save_dir:
            self.load_data(save_dir)
        else:
            self.data = self.empty_story_object
            self.data["name"] = "untitled"
            self.data["uuid"] = UUID()
            self.data["scale_dict"] = {}
            self.data["save_dir"] = None
            self.is_dirty = False
            return
        
    def load_data(self, save_dir):
        '''
        load json data for an entire story object.
        '''
        save_file = open(save_dir, 'r')
        self.data = json.load(save_file)
        self.save_dir = save_dir
        self.is_dirty = False
            
    def save_data(self, save_dir=None):
        '''
        save the current self.data as a json file to the specified save_dir
        calling this without arguments overwrites existing save file
        '''
        # if a save path was provided, save there
        if save_dir:
            # ensure the save path is valid
            try:
                folder = os.path.split(save_dir[0])
                assert os.path.exists(folder)
            except AssertionError:
                return "not_exist"
            try:
                assert save_dir.endswith(".json")
            except AssertionError:
                return "wrong_type"

            logging.info("new save path provided. Writing to new location")
            self.data['save_dir'] = save_dir
            json_data = json.dumps(self.data, indent=4)

            with open(save_dir, 'w') as dest_file:
                dest_file.write(json_data)
            self.is_dirty = False
            self.save_dir = self.data['save_dir']
            return "success"
        # if no save path was provided and this Story doesnt have a save path yet
        elif self.save_dir is None:
            logging.warning("no save path provided and story object has no existing save path")
        # Overwrite current project
        else:
            logging.warning("overwriting existing save file.")
            json_data = json.dumps(self.data, indent=4)
            with open(self.save_dir, 'w') as dest_file:
                dest_file.write(json_data)
            self.is_dirty = False
            return "success"

    def add_character(self, data):
        '''
        JSON data is stored as a dict in python, so I should store each character's data as a dict as well.
        This means that my characters most likely dont need to be a Class object.
        '''
        uuid = UUID()
        data["uuid"] = uuid
        self.data["characters"][str(uuid)] = data
        logging.info("no existing character found, adding new one")

        self.is_dirty = True
        return

    def edit_character(self, data):
        logging.info("edit_character() called on :" + data["name"])
        self.data["characters"][str(data["uuid"])]=data
        self.is_dirty = True
        return

    def add_or_edit_entry(self, beat_ID, char_ID, scale_list, notes_list):
        '''
        add or edit one character's entry.
        beat_ID (int) = the location on the x axis for this entry
        char_ID (int) = a long integer created by the UUID() class
        scale_list  (list) = list of floats that indicate the quality of each entry
        notes_list (list) = list of strings that provide details about each scale value
        '''
        for char in self.data.beats[beat_ID]:
            if char['uuid'] == char_ID:
                char['scale_list'] = scale_list
                char['notes_list'] = notes_list
                self.is_dirty = True
                return
        logging.warning("no character found, edit_entry did not edit anything")
        return

    def get_character_data(self, char_ID, data_key):
        for char in self.data['characters']:
            if char["uuid"] == char_ID:
                return char[data_key]

    def add_beat(self, data, append=False, index=0):
        if append:
            self.data["beats"].append(data)
        else:
            self.data["beats"].insert(index, data)
        self.is_dirty = True


    def create_empty_entry(self, char_ID, beat_index=0):
        '''
        insert a placeholder entry for the specified character.
        If append is false, insert into the space indicated with "x"
        '''
        self.data["beats"][beat_index]["characters"][char_ID] = self.entry_object(char_ID)

    def entry_object(self, uuid, scale_list = [0], notes_list = [""]):
        """
        convenience function for creating an empty entry dict
        """
        data = {}
        data["uuid"] = uuid
        data["scale_list"] = scale_list
        data["notes_list"] = notes_list
        return data

    def beat_object(self):
        data = {}
        data["name"] = ""
        data["synopsis"] = ""
        data["uuid"] = UUID()
        data["characters"] = {}
        return data

class Character_Object(object):
    #the character has different story entries, and we can establish a trend line
    #these story entries track a personal emotional history line
    #different personalities are like pokemon types: They have weaknesses and resistances to different emotions
    #each character is tracked on their own.
    # in the model-controller-view system, this is a model object.
    def __init__(self, data):
        self.__data = {}
        if "uuid" not in data:
            self.__data["uuid"] = UUID()
        for key, value in data.items():
            self.__data[key] = value

    def get_data(self):
        return self.__data

    def set_data(self, key = str, value=None):
        if key in self.__data:
            if type(self.__data[key]) == type(value):
                if self.__data[key] == value:
                    #no need to reset if it is already the same
                    return
                else:
                    self.__data[key] = value
            else:
                raise TypeError("expected a {0}, value was instead a {1}".format(str(type(self.__data)), str(type(value))))
        else:
            raise KeyError("key does not exist in dict. Use add_data instead.")

    def add_data(self, key=str, value=None):
        if key in self.__data:
            raise KeyError("key already exists. cannot add.")
        elif value is not None:
            self.__data[key] = value


def UUID():
    temp_uuid = uuid.uuid1()
    return str(temp_uuid.int)
