# story arc grapher. Allows you to plot out a character's mental state on each story beat,
# use graphing abilities to observe their changes overtime, and how their changes interact
'''
Turn this into a Video Game Narrative Design Tool:
This could eventually be useful in videogame design by adding parameters for production time projections,
creating possible asset sheets, and other game-relevant info.
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
                                    "characters":[],
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
            self.is_dirty = True
            return
        
    def load_data(self, save_dir):
        '''
        load json data for an entire story object.
        '''
        self.data = json.loads(save_dir)
        self.save_dir = save_dir
        self.is_dirty = False
            
    def save_data(self, save_dir=None):
        '''
        save the current self.data as a json file to the specified save_dir
        calling this without arguments overwrites existing save file
        '''
        # if a save path was provided, save there
        if save_dir:
            logging.info("new save path provided. Writing to new location")
            self.data['save_dir'] = save_dir
            json_data = json.dumps(self.data, indent=4)

            with open(save_dir, 'w') as dest_file:
                dest_file.write(json_data)
            self.is_dirty = False
            self.save_dir = self.data['save_dir']
        # if no save path was provided and this Story doesnt have a save path yet
        elif self.save_dir is None:
            logger.warning("no save path provided and story object has no existing save path")
        # Overwrite current project
        else:
            logging.warning("overwriting existing save file.")
            json_data = json.dumps(self.data, indent=4)
            with open(self.save_dir, 'w') as dest_file:
                dest_file.write(json_data)


            self.is_dirty = False

    def add_or_edit_character(self, data=None):
        '''
        JSON data is stored as a dict in python, so I should store each character's data as a dict as well.
        This means that my characters most likely dont need to be a Class object.
        '''
        for char in self.data['characters']:
            if data.uid == char['uuid']:
                for key, value in data:
                    char.set_data(key=key, value=value)
                return

        new_character = Character_Object(data)
        # JSON is a dict in python, so add this character to the python dict in the characters section
        self.data['characters'].append(new_character.get_data())
        self.is_dirty = True
        return

    def edit_entry(self, beat_ID, action, emotion, energy_level, rational_level, caution_level):
        beats[beat_ID][self.name] = {}
        self.is_dirty = True
        return

    def add_entry(self, character_uuid, scale_list):
        self.is_dirty = True

        return


class Entry_Object(object):
    '''
    This is the contents of an entry that is stored in each Character Object
    '''
    def __init__(self, x, scale_list=[], notes_list=[], *args, **kwargs):
        '''
        args:
        x (INT) = the location of this entry on the x axis of the story arc graph
        scale_dict (DICT) =  key (STR): a UUID for the user's defined scale; value (FLT): the location on that scale
        description (STR) = a string that lets the user record some text about this entry.
        '''
        if len(scale_list) != len(notes_list):
            smaller = min(scale_list, notes_list)
            larger = max(scale_list, notes_list)
            difference = larger - smaller
            for x in range(0, difference):
                smaller.append([])
        self.empty_entry_object = {
                                    "x":0, 
                                    "scales":[],
                                    "notes":[],
        }
        self.data = {}
        self.data["x"] = x
        self.data["scale_list"] = scale_list
        self.data["notes_list"] = notes_list 


class Character_Object(object):
    #the character has different story entries, and we can establish a trend line
    #these story entries track a personal emotional history line
    #different personalities are like pokemon types: They have weaknesses and resistances to different emotions
    #each character is tracked on their own.
    # in the model-controller-view system, this is a model object.

    #action: does the character complete something? who does this action impact?
    #event: does something happen to this character? who causes it?
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
    return temp_uuid.int
