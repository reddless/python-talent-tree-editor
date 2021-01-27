import numpy as np
from core import *
from views import *



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TalentData:

    def __init__(self, name, icon, ranks, description_text, description_values, row=None, col=None):
        self.row = row
        self.col = col
        self.name = name
        self.icon = icon
        self.ranks = int(ranks)
        self.points_spent = 0
        self.prerequisite = None
        self.dependant = None
        self.description_per_rank = self.parse_description_per_rank(description_text, description_values)
        self.talent_view = TalentView(self)
    
    def parse_description_per_rank(self, description_text, description_values):
        description_per_rank = ["?"] * self.ranks
        try:
            values = [[per_rank for per_rank in per_index.strip().split()] for per_index in description_values.strip().split(";")]
            for rank in range(self.ranks):
                text_with_values = ""
                value_index = 0
                for c in description_text:
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
        if self.talent_view != None:
           self.talent_view.update() 

    def delete(self):
        if self.prerequisite != None:
            self.prerequisite.dependant = None
        if self.dependant != None:
            self.dependant.prerequisite = None
        self.tree.reevaluate_subtree(self.row)

    def add_point(self):
        if self.check_prerequisite_is_satisfied() and self.check_sufficient_earlier_points() and (self.points_spent < self.ranks) and (self.tree.check_points_available()):
            self.points_spent += 1
            self.tree.add_point(self)
    
    def subtract_point(self):
        if self.check_dependant_is_satisfied() and self.check_point_is_dispensable() and (self.points_spent > 0):
            self.points_spent -= 1
            self.tree.subtract_point(self)
    
    @staticmethod
    def load_from_dict(talent_data_dict):
        talent_data = TalentData(
            talent_data_dict["name"],
            talent_data_dict["icon"],
            talent_data_dict["ranks"],
            talent_data_dict["description_text"],
            talent_data_dict["description_values"]
        )
        if "points_spent" in talent_data_dict:
            talent_data.points_spent = talent_data_dict["points_spent"]
        if "row" in talent_data_dict:
            talent_data.row = talent_data_dict["row"]
        if "col" in talent_data_dict:
            talent_data.col = talent_data_dict["col"]
        return talent_data




#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TalentPlaceholderData(TalentData):

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.talent_view = TalentPlaceholderView(self)
        self.tree = None
    
    def refresh_status(self):
        pass
    



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TreeData:

    def __init__(self, name, icon, background, index=None):
        self.index = index
        self.name = name
        self.icon = icon
        self.background = background
        self.talent_holder = np.empty(shape=(7,4), dtype=TalentData)
        self.points_in_row = np.zeros(7)
        self.points_spent = 0
        self.tree_view = TreeView(self)
    
    def add_point(self, talent):
        self.points_spent += 1
        self.points_in_row[talent.row] += 1
        self.multi_tree.add_point()
        # if True or self.points_spent % 5 == 1:
        #     RUNTIME.get_top_view().update_icon(self.index)
    
    def subtract_point(self, talent):
        self.points_spent -= 1
        self.points_in_row[talent.row] -= 1
        self.multi_tree.subtract_point()
        # if True or self.points_spent % 5 == 0:
        #     RUNTIME.get_top_view().update_icon(self.index)
    
    def check_points_available(self):
        return self.multi_tree.check_points_available()

    def add_talent(self, talent, row=None, col=None):
        if row != None and col != None:
            talent.tree = self
            talent.row = row
            talent.col = col
        if talent.row != None and talent.col != None:
            self.talent_holder[talent.row,talent.col] = talent
            talent.tree = self
            self.tree_view.add_talent_view(talent.talent_view)
        else:
            raise Exception("Talent row/column not specified")
    
    def delete_talent(self, talent):
        self.talent_holder[talent.row,talent.col] = None
    
    def delete_all_talents(self):
        self.talent_holder = np.empty(shape=(7,4), dtype=TalentData)
        self.cumulative_points_below_rank = np.zeros(7)
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

    @staticmethod
    def load_from_dict(tree_data_dict):
        tree_data = TreeData(
            tree_data_dict["name"],
            tree_data_dict["icon"],
            tree_data_dict["background"]
        )
        if "index" in tree_data_dict:
            tree_data.index = tree_data_dict["index"]
        if "talents" in tree_data_dict:
            for talent_data_dict in tree_data_dict["talents"]:
                tree_data.add_talent(TalentData.load_from_dict(talent_data_dict))
        return tree_data
        


#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class MultiTreeData:

    def __init__(self, name):
        self.name = name
        self.points_remaining = 51
        self.tree_data_holder = np.empty(shape=(3,), dtype=TreeData)
        self.multi_tree_view = MultiTreeView(self)
    
    def add_tree(self, tree, index=None):
        if index != None:
            self.tree_data_holder[index] = tree
            tree.multi_tree = self
            self.multi_tree_view.add_tree_view(tree.tree_view)
        else:
            if tree.index != None:
                self.tree_data_holder[index] = tree
                tree.multi_tree = self
                self.multi_tree_view.add_tree_view(tree.tree_view)
            else:
                raise Exception("Tree index not specified")

    def add_point(self):
        self.points_remaining -= 1
        if self.points_remaining == 0:
            for tree in self.tree_data_holder:
                tree.reevaluate_subtree(0)
            RUNTIME.get_top_view().update_icons()

    def subtract_point(self):
        self.points_remaining += 1
        if self.points_remaining == 1:
            for tree in self.tree_data_holder:
                tree.reevaluate_subtree(0)
            RUNTIME.get_top_view().update_icons()
    
    def check_points_available(self):
        return self.points_remaining > 0
    
    @staticmethod
    def load_from_json(json_file_path):
        try:
            f = open(json_file_path, "r")
            multi_tree_data_dict = json.load(f)
            f.close()
            return MultiTreeData.load_from_dict(multi_tree_data_dict)
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def load_from_dict(multi_tree_data_dict):
        multi_tree_data = MultiTreeData(
            multi_tree_data_dict["name"]
        )
        multi_tree_data.points_remaining = multi_tree_data_dict.get("points_remaining", 51)
        if "trees" in multi_tree_data_dict:
            for tree_data_dict in multi_tree_data_dict["trees"]:
                multi_tree_data.add_tree(TreeData.load_from_dict(tree_data_dict))
        return multi_tree_data