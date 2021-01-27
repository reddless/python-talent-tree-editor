import random
import os
from core import *
from data import *


if __name__ == "__main__":

    RUNTIME.init()

    multi_tree = MultiTreeData("Awesome Talent Tree")
    trees = []
    talents = [[],[],[]]
    for i in range(3):
        icon_names = os.listdir("./icons/spells")
        icon_paths = ["./icons/spells/"+s for s in random.choices(icon_names, k=28)]
        tree = TreeData("spec", icon_paths[0], "./backgrounds/blank.png", index=i)
        for y in range(7):
            for x in range(4):
                talent = TalentData("Nature's Blessing", icon_paths[4*y+x], 5, "Description $%"+" aasdwe"*int(random.random()*20), "10 20 30 40 50", row=y, col=x)
                talents[i] += [talent]
                tree.add_talent(talent if random.random() > 0.6 else TalentPlaceholderData(y,x))
        trees += [tree]
        multi_tree.add_tree(tree)
    
    # multi_tree = MultiTreeData.load_from_json("./_test_data/multi_tree_example.json")

    RUNTIME.show(multi_tree)









