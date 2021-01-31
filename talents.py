import random
import os
from core import *
from data import *


if __name__ == "__main__":

    RUNTIME.init()

    multi_tree = MultiTreeData()

    multi_tree_data_dict = {
        "name": "Awesome Talent Tree",
        "points_remaining": 51,
        "trees": {}
    }
    for index in range(3):
        icon_names = os.listdir("./icons/spells")
        icon_paths = ["./icons/spells/"+s for s in random.choices(icon_names, k=28)]
        tree_data_dict = {
            "name": "spec",
            "icon": icon_paths[0],
            "background": "./backgrounds/blank.png",
            "talents": {}
        }
        for row in range(7):
            for col in range(4):
                talent_data_dict = {
                    "name": "Nature's Blessing",
                    "icon": icon_paths[4*row+col],
                    "ranks": 5, 
                    "description_text": "Description $%"+" aasdwe"*int(random.random()*20),
                    "description_values": "10 20 30 40 50"
                }
                tree_data_dict["talents"]["{},{}".format(row,col)] = talent_data_dict
        multi_tree_data_dict["trees"]["{}".format(index)] = tree_data_dict
    
    multi_tree.load_from_dict(multi_tree_data_dict)

    RUNTIME.show(multi_tree)









