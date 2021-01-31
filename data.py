import numpy as np
from core import *
from views import *



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TalentData:

    def __init__(self, tree, row, col):
        self.tree = tree
        self.row = row
        self.col = col
        self.name = None
        self.icon = PATHS.ICON_QUESTION
        self.ranks = 0
        self.points_spent = 0
        self.prerequisite = None
        self.dependant = None
        self.description_text = None
        self.description_values = None
        self.description_per_rank = None
        self.view = TalentView(self)
    
    def parse_description_per_rank(self):
        description_per_rank = ["?"] * self.ranks
        try:
            values = [[per_rank for per_rank in per_index.strip().split()] for per_index in self.description_values.strip().split(";")]
            for rank in range(self.ranks):
                text_with_values = ""
                value_index = 0
                for c in self.description_text:
                    if c == '$':
                        try:
                            text_with_values += str(values[value_index][rank])
                            value_index += 1
                        except Exception as e:
                            text_with_values += "?"
                            value_index += 1
                    else:
                        text_with_values += c
                description_per_rank[rank] = text_with_values
        except:
            pass
        return description_per_rank
    
    def check_can_add_point(self):
        return self.check_prerequisite_is_satisfied() and self.check_sufficient_earlier_points() and self.tree.check_points_available() and self.points_spent < self.ranks
    
    def check_prerequisite_is_satisfied(self):
        return (self.prerequisite == None) or (self.prerequisite.points_spent == self.prerequisite.ranks)
    
    def check_sufficient_earlier_points(self):
        return sum(self.tree.points_in_row[:self.row]) >= 5*self.row
    
    def check_dependant_is_satisfied(self):
        return (self.dependant == None) or (self.dependant.points_spent == 0)
    
    def check_point_is_dispensable(self):
        for row in range(self.row+1, 7):
            if (self.tree.points_in_row[row] > 0) and (sum(self.tree.points_in_row[:row]) - 1 < 5*row):
                return False
        return True
    
    def refresh_status(self):
        if (self.points_spent > 0) and (not self.check_prerequisite_is_satisfied() or not self.check_sufficient_earlier_points()):
            self.tree.points_in_row[row] -= self.points_spent
            self.tree.points_spent -= self.points_spent
            self.points_spent = 0
        if self.view != None:
           self.view.update() 

    def clear(self):
        if self.prerequisite != None:
            self.prerequisite.dependant = None
        if self.dependant != None:
            self.dependant.prerequisite = None
        for point in range(self.points_spent):
            self.tree.subtract_point(self)
        self.name = None
        self.icon = None
        self.ranks = 0
        self.points_spent = 0
        self.description_text = None
        self.description_values = None
        self.view.update()
        self.tree.reevaluate_subtree(self.row)

    def add_point(self):
        if self.check_prerequisite_is_satisfied() and self.check_sufficient_earlier_points() and (self.points_spent < self.ranks) and (self.tree.check_points_available()):
            self.points_spent += 1
            self.tree.add_point(self)
    
    def subtract_point(self):
        if self.check_dependant_is_satisfied() and self.check_point_is_dispensable() and (self.points_spent > 0):
            self.points_spent -= 1
            self.tree.subtract_point(self)
    
    def load_from_dict(self, talent_data_dict):
        self.name = talent_data_dict["name"]
        self.icon = talent_data_dict["icon"]
        self.ranks = talent_data_dict["ranks"]
        self.description_text = talent_data_dict["description_text"]
        self.description_values = talent_data_dict["description_values"]
        self.description_per_rank = self.parse_description_per_rank()
        if "points_spent" in talent_data_dict:
            self.points_spent = talent_data_dict["points_spent"]
    


#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TreeData:

    def __init__(self, multi_tree, index):
        self.multi_tree = multi_tree
        self.index = index
        self.name = None
        self.icon = PATHS.ICON_QUESTION
        self.background = PATHS.BACKGROUND_BLANK
        self.talent_holder = np.empty(shape=(7,4), dtype=TalentData)
        self.points_in_row = np.zeros(7)
        self.points_spent = 0
        self.view = TreeView(self)
        for row in range(7):
            for col in range(4):
                talent = TalentData(self, row, col)
                self.talent_holder[row,col] = talent
                self.view.set_talent_view(talent.view)
    
    def add_point(self, talent):
        self.points_spent += 1
        self.points_in_row[talent.row] += 1
        self.multi_tree.add_point()
    
    def subtract_point(self, talent):
        self.points_spent -= 1
        self.points_in_row[talent.row] -= 1
        self.multi_tree.subtract_point()
    
    def check_points_available(self):
        return self.multi_tree.check_points_available()
    
    def clear(self):
        for row in range(7):
            for col in range(4):
                self.talent_holder[row,col].clear()
        self.cumulative_points_below_rank = np.zeros(7)
        self.multi_tree.points_remaining += self.points_spent
        self.points_spent = 0
    
    def reset_talent_points(self):
        for row in self.talent_holder:
            for col in self.talent_holder[row]:
                talent = self.talent_holder[row,col]
                if talent != None:
                    talent.clear_talent_points()
    
    def reevaluate_subtree(self, starting_row):
        for row in range(starting_row, 7):
            for repeat_for_siderequisite_edge_case in range(4):
                for col in range(4):
                    talent = self.talent_holder[row,col]
                    if talent != None:
                        talent.refresh_status()

    def load_from_dict(self, tree_data_dict):
        self.name = tree_data_dict["name"]
        self.icon = tree_data_dict["icon"]
        self.background = tree_data_dict["background"]
        self.view.data_updated()
        if "talents" in tree_data_dict:
            self.clear()
            for row_col_str,talent_data_dict in tree_data_dict["talents"].items():
                row, col = map(int, row_col_str.split(","))
                self.talent_holder[row, col].load_from_dict(talent_data_dict)
        


#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class MultiTreeData:

    def __init__(self):
        self.name = None
        self.points_remaining = 51
        self.tree_holder = np.empty(shape=(3,), dtype=TreeData)
        self.view = MultiTreeView(self)
        for index in range(3):
            tree = TreeData(self, index)
            self.tree_holder[index] = tree
            self.view.set_tree_view(tree.view)

    def add_point(self):
        self.points_remaining -= 1
        if self.points_remaining == 0:
            for tree in self.tree_holder:
                tree.reevaluate_subtree(0)
            RUNTIME.get_top_view().update_icons()

    def subtract_point(self):
        self.points_remaining += 1
        if self.points_remaining == 1:
            for tree in self.tree_holder:
                tree.reevaluate_subtree(0)
            RUNTIME.get_top_view().update_icons()
    
    def check_points_available(self):
        return self.points_remaining > 0

    def clear(self):
        for index in range(3):
            self.tree_holder[index].clear()
            self.points_remaining = 51

    def load_from_dict(self, multi_tree_data_dict):
        self.name = multi_tree_data_dict["name"]
        self.points_remaining = multi_tree_data_dict.get("points_remaining", 51)
        if "trees" in multi_tree_data_dict:
            self.clear()
            for index_str,tree_data_dict in multi_tree_data_dict["trees"].items():
                index = int(index_str)
                self.tree_holder[index].load_from_dict(tree_data_dict)
                self.view.set_tree_view(self.tree_holder[index].view)