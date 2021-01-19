import numpy as np
import os
import random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import json








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
    def load_from_json(json_file_path):
        try:
            f = open(json_file_path, "r")
            talent_data_dict = json.load(f)
            f.close()
            return TalentData.load_from_dict(talent_data_dict)
        except Exception as e:
            print(e)
            return None
    
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
    
    def subtract_point(self, talent):
        self.points_spent -= 1
        self.points_in_row[talent.row] -= 1
        self.multi_tree.subtract_point()
    
    def check_points_available(self):
        return self.multi_tree.check_points_available()

    def add_talent(self, talent, row=None, col=None):
        if row != None and col != None:
            self.talent_holder[row,col] = talent
            talent.tree = self
            self.tree_view.add_talent_view(talent.talent_view)
        else:
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
    def load_from_json(json_file_path):
        try:
            f = open(json_file_path, "r")
            tree_data_dict = json.load(f)
            f.close()
            return TreeData.load_from_dict(tree_data_dict)
        except Exception as e:
            print(e)
            return None

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

    def subtract_point(self):
        self.points_remaining += 1
        if self.points_remaining == 1:
            for tree in self.tree_data_holder:
                tree.reevaluate_subtree(0)
    
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




class RUNTIME:
    app = None
    multi_tree = None

    @staticmethod
    def init(scale=1):
        VALUES.set_scale(scale)
        RUNTIME.app = QApplication([])

    @staticmethod
    def get_app():
        if RUNTIME.app != None:
            return RUNTIME.app
        else:
            raise Exception("The 'app' reference has not been passed into the RUNTIME")

    @staticmethod
    def get_top_view():
        if RUNTIME.multi_tree != None:
            return RUNTIME.multi_tree.multi_tree_view
        else:
            raise Exception("The top 'multi_tree' reference has not been passed into the RUNTIME")

    @staticmethod
    def show(multi_tree):
        RUNTIME.multi_tree = multi_tree
        RUNTIME.multi_tree.multi_tree_view.show()
        RUNTIME.app.exec_()
        
    

class UTILS:

    @staticmethod
    def get_pixmap_with_saturation(path_to_file, saturation=1):
        image = QImage(QPixmap.toImage(QPixmap(path_to_file)))
        for i in range(image.width()):
            for j in range(image.height()):
                color = image.pixelColor(i, j)
                color.setHsv(color.hue(), saturation * color.saturation(), color.value())
                image.setPixelColor(i, j, color)
        return QPixmap.fromImage(image)



class PATHS:
    TALENT_BORDER = "./assets/talent-border.png"
    TALENT_HOVER = "./assets/talent-hover.png"
    TALENT_BUBBLE = "./assets/talent-bubble.png"
    TALENT_ACCENT_GREY = "./assets/talent-accent-grey"
    TALENT_ACCENT_GREEN = "./assets/talent-accent-green"
    TALENT_ACCENT_GOLD = "./assets/talent-accent-gold"
    TALENT_ADD_BUTTON = "./assets/add-talent.png"
    CLOSE_HOVER = "./assets/close-hover.png"
    CLOSE_NOHOVER = "./assets/close-nohover.png"
    CLOSE_PRESSED_HOVER = "./assets/close-pressed-hover.png"
    CLOSE_PRESSED_NOHOVER = "./assets/close-pressed-nohover.png"



class VALUES:
    __init_called__ = False
    REF_FRAME_WIDTH = 1335
    REF_FRAME_HEIGHT = 805
    REF_FRAME_INTERTREE_WIDTH = 12
    REF_TOOLTIP_WIDTH = 400
    REF_TOOLTIP_FLIPOVER_PADDING = 80
    REF_TOOLTIP_VERTICAL_OFFSET = 130
    REF_TOOLTIP_Y_FLOOR = 120
    REF_TREE_X = 27
    REF_TREE_Y = 90
    REF_TREE_WIDTH = 421
    REF_TREE_HEIGHT = 670
    REF_TREE_CONTENTS_MARGIN_LEFT = 25
    REF_TREE_CONTENTS_MARGIN_TOP = 0
    REF_TREE_CONTENTS_MARGIN_RIGHT = 35
    REF_TREE_CONTENTS_MARGIN_BOTTOM = 10
    REF_TREE_NAME_FONT_SIZE = 15
    REF_TREE_POINTS_FONT_SIZE = 12
    REF_TALENT_CELL_SIZE = 100
    REF_TALENT_MOUSEAREA_SIZE = 60
    REF_TALENT_ICON_SIZE = 56
    REF_TALENT_BORDER_SIZE = 64
    REF_TALENT_HOVER_SIZE = 53
    REF_TALENT_ACCENT_SIZE = 60
    REF_TALENT_BUBBLE_OFFSET = 64
    REF_TALENT_BUBBLE_SIZE = 26
    REF_TALENT_POINTS_OFFSET_X = 73
    REF_TALENT_POINTS_OFFSET_Y = 53
    REF_TALENT_POINTS_SIZE = 50
    REF_TALENT_FONT_SIZE = 14

    @staticmethod
    def __init__():
        ref_attr_list = [ref_attr for ref_attr in VALUES.__dict__ if "REF" in ref_attr]
        for ref_attr in ref_attr_list:
            exec("VALUES.{} = VALUES.{}".format(ref_attr[4:], ref_attr))
        VALUES.__init_called__ = True
        
    @staticmethod
    def set_scale(scale, q_main_window=None):
        if not VALUES.__init_called__:
            VALUES.__init__()
        attr_list = [attr for attr in VALUES.__dict__ if (not "__" in attr and not "REF" in attr and not "set_scale" in attr)]
        for attr in attr_list:
            exec("VALUES.{} = int(round(scale * VALUES.REF_{}))".format(attr, attr))
        if q_main_window != None:
            q_main_window.update()




class TalentView(QWidget):

    def __init__(self, talent):
        super().__init__()
        self.setGeometry(0, 0, VALUES.TALENT_CELL_SIZE, VALUES.TALENT_CELL_SIZE)
        self.talent = talent
        self.is_hovered = False
        font = QFont()
        font.setPointSize(int(round(VALUES.TALENT_FONT_SIZE)))
        self.points_text = QLabel(self)
        self.points_text.setFont(font)
        self.points_text.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.points_text.setGeometry(VALUES.TALENT_POINTS_OFFSET_X,VALUES.TALENT_POINTS_OFFSET_Y,VALUES.TALENT_POINTS_SIZE,VALUES.TALENT_POINTS_SIZE)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover)
    
    def paintEvent(self, event):
        rect_icon = QRect(*(lambda x: ((VALUES.TALENT_CELL_SIZE-x)/2,(VALUES.TALENT_CELL_SIZE-x)/2,x,x))(VALUES.TALENT_ICON_SIZE))
        rect_border = QRect(*(lambda x: ((VALUES.TALENT_CELL_SIZE-x)/2,(VALUES.TALENT_CELL_SIZE-x)/2,x,x))(VALUES.TALENT_BORDER_SIZE))
        rect_hover = QRect(*(lambda x: ((VALUES.TALENT_CELL_SIZE-x)/2,(VALUES.TALENT_CELL_SIZE-x)/2,x,x))(VALUES.TALENT_HOVER_SIZE))
        rect_accent = QRect(*(lambda x: ((VALUES.TALENT_CELL_SIZE-x)/2,(VALUES.TALENT_CELL_SIZE-x)/2,x,x))(VALUES.TALENT_ACCENT_SIZE))
        rect_bubble = QRect(VALUES.TALENT_BUBBLE_OFFSET,VALUES.TALENT_BUBBLE_OFFSET,VALUES.TALENT_BUBBLE_SIZE,VALUES.TALENT_BUBBLE_SIZE)

        if self.talent.check_can_add_point() or self.talent.points_spent > 0:
            painter = QPainter(self)
            painter.drawPixmap(rect_icon, QPixmap(self.talent.icon))
            painter.drawPixmap(rect_border, QPixmap(PATHS.TALENT_BORDER))
            if self.is_hovered: 
                painter.drawPixmap(rect_hover, QPixmap(PATHS.TALENT_HOVER))
            if self.talent.points_spent == 5:
                painter.drawPixmap(rect_accent, QPixmap(PATHS.TALENT_ACCENT_GOLD))
            else:
                painter.drawPixmap(rect_accent, QPixmap(PATHS.TALENT_ACCENT_GREEN))
            painter.drawPixmap(rect_bubble, QPixmap(PATHS.TALENT_BUBBLE))
            self.points_text.setText(self.get_html_points())
            self.points_text.setVisible(True)
        else:
            painter = QPainter(self)
            painter.drawPixmap(rect_icon, QPixmap.fromImage(QImage(QPixmap.toImage(QPixmap(self.talent.icon)).convertToFormat(QImage.Format_Grayscale8))))
            painter.drawPixmap(rect_border, QPixmap(PATHS.TALENT_BORDER))
            if self.is_hovered: 
                painter.drawPixmap(rect_hover, QPixmap(PATHS.TALENT_HOVER))
            painter.drawPixmap(rect_accent, QPixmap(PATHS.TALENT_ACCENT_GREY))
            self.points_text.setVisible(False)

    def mouseMoveEvent(self, event):
        if self.check_event_in_mouse_area(event):
            if not self.is_hovered:
                self.is_hovered = True
                self.update()
                RUNTIME.get_top_view().update_tooltip(self)
        else:
            if self.is_hovered:
                self.is_hovered = False
                self.update()
                RUNTIME.get_top_view().update_tooltip(self)

    def mousePressEvent(self, event):
        if self.check_event_in_mouse_area(event):
            if event.button() == Qt.LeftButton:
                self.talent.add_point()
            elif event.button() == Qt.RightButton:
                self.talent.subtract_point()
            self.talent.tree.reevaluate_subtree(0)
            RUNTIME.get_top_view().update_points()
            RUNTIME.get_top_view().update_tooltip(self)
        else:
            super().mousePressEvent(event)
    
    def wheelEvent(self, event):
        if self.check_event_in_mouse_area(event):
            if event.angleDelta().y() > 0:
                self.talent.add_point()
            elif event.angleDelta().y() < 0:
                self.talent.subtract_point()
            self.talent.tree.reevaluate_subtree(0)
            RUNTIME.get_top_view().update_points()
            RUNTIME.get_top_view().update_tooltip(self)

    def check_event_in_mouse_area(self, event):
        dead_zone = (VALUES.TALENT_CELL_SIZE - VALUES.TALENT_MOUSEAREA_SIZE)/2
        return (event.x() >= dead_zone) and (event.x() <= VALUES.TALENT_CELL_SIZE - dead_zone) and (event.y() >= dead_zone) and (event.y() <= VALUES.TALENT_CELL_SIZE - dead_zone)
        
    def delete(self):
        pass
    
    def get_html_tooltip(self):
        text = "<font color=\"white\" size=5>{}</font>".format(self.talent.name)
        text += "<br/><font color=\"white\">Rank {}/{}</font>".format(self.talent.points_spent, self.talent.ranks)
        if not self.talent.check_sufficient_earlier_points():
            text += "<br/><font color=\"red\">Requires {} points in {} Talents</font>".format(5*(self.talent.row), self.tree.name)
        if not self.talent.check_prerequisite_is_satisfied():
            text += "<br/><font color=\"red\">Requires {} points in {}</font>".format(self.prerequisite.ranks, self.prerequisite.name)
        if self.talent.points_spent == 0:
            text += "<br/><font color=\"gold\">{}.</font>".format(self.talent.description_per_rank[0])
        elif self.talent.points_spent == self.talent.ranks:
            text += "<br/><font color=\"gold\">{}.</font>".format(self.talent.description_per_rank[-1])
        else:
            text += "<br/><font color=\"gold\">{}.</font><br/><br/><font color=\"white\">Next rank:</font><br/><font color=\"gold\">{}.</font>".format(
                self.talent.description_per_rank[self.talent.points_spent-1],self.talent.description_per_rank[self.talent.points_spent])
        text +=  "<br/><font color=\"#1bed00\">Click to learn</font>" if self.talent.check_can_add_point() and self.talent.points_spent == 0 else ""
        text +=  "<br/><font color=\"red\">Right click to unlearn</font>" if self.talent.points_spent != 0 else ""
        return text
    
    def get_html_points(self):
        return "<font color=\"{}\">{}</font>".format("gold" if self.talent.points_spent == self.talent.ranks else "#1bed00", self.talent.points_spent)





class TalentPlaceholderView(QWidget):

    def __init__(self, talent):
        super().__init__()
        self.setGeometry(0, 0, 100, 100)
        self.opacity = 0.2
        self.size = 50
        self.talent = talent
        self.setAttribute(Qt.WA_Hover)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.opacity)
        pixmap = QPixmap(PATHS.TALENT_ADD_BUTTON)
        painter.drawPixmap(QRect((100-self.size)/2,(100-self.size)/2,self.size,self.size), pixmap)
    
    def mousePressEvent(self, event):
        self.opacity = min(1, self.opacity + 0.2)
        self.size = min(70, self.size + 5)
        self.update()
    
    def delete(self):
        pass





class TooltipView(QLabel):
    path_tooltip_background = "./assets/tooltip.png"

    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setStyleSheet("font: 14pt Verdana; padding: 7px")
        self.setFixedWidth(VALUES.TOOLTIP_WIDTH)
        self.setVisible(False)
        self.setWordWrap(True)
        self.background_rect = QLabel()
        self.background_rect.setParent(parent)
        self.background_rect.setVisible(False)
        self.background_pixmap_ref = QPixmap(self.path_tooltip_background)
        self.background_pixmap = None
        self.previous_talent_view = None
    
    def update_tooltip(self, talent_view):
        if self.previous_talent_view != talent_view:
            self.hide_tooltip()

        self.previous_talent_view = talent_view
        if talent_view.is_hovered:
            old_x = self.x()
            old_y = self.y()
            old_geometry = self.geometry()
            self.setText(talent_view.get_html_tooltip())
            self.adjustSize()
            tree_position = talent_view.talent.tree.tree_view.geometry().topLeft()
            talent_position = talent_view.geometry().topRight()
            new_x = tree_position.x() + talent_position.x()
            new_y = talent_position.y() - self.height() + VALUES.TOOLTIP_VERTICAL_OFFSET
            if new_x > VALUES.FRAME_WIDTH - VALUES.TOOLTIP_WIDTH:
                new_x -= (VALUES.TOOLTIP_WIDTH + VALUES.TOOLTIP_FLIPOVER_PADDING)
            if new_y < VALUES.TOOLTIP_Y_FLOOR:
                new_y = VALUES.TOOLTIP_Y_FLOOR
            if new_x != old_x or new_y != old_y:
                self.move(new_x, new_y)
            if self.geometry() != old_geometry:
                self.background_rect.setGeometry(self.geometry())
                self.update_background_pixmap()
            if not self.isVisible():
                self.setVisible(True)
            if not self.background_rect.isVisible():
                self.background_rect.setVisible(True)
        else:
            self.setVisible(False)
            self.background_rect.setVisible(False)
        self.background_rect.raise_()
        self.raise_()
        self.update()
    
    def hide_tooltip(self):
        if self.previous_talent_view != None:
            self.previous_talent_view.is_hovered = False
            self.previous_talent_view.update()
            self.setVisible(False)
            self.background_rect.setVisible(False)
    
    def update_background_pixmap(self):
        w = self.background_rect.width()/2
        h = self.background_rect.height()/2
        ww = self.background_pixmap_ref.width()
        hh = self.background_pixmap_ref.height()
        s = (lambda x: 100/(100+x))(10)
        self.background_pixmap = QPixmap(self.background_rect.width(),self.background_rect.height())
        image = QImage(self.background_rect.width(),self.background_rect.height(),6)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setBackgroundMode(Qt.TransparentMode)
        painter.drawPixmap(QRectF(0,0,w,h), self.background_pixmap_ref, QRectF(0,0,s*w,s*h))
        painter.drawPixmap(QRectF(w,0,w,h), self.background_pixmap_ref, QRectF(ww-s*w,0,s*w,s*h))
        painter.drawPixmap(QRectF(0,h,w,h), self.background_pixmap_ref, QRectF(0,hh-s*h,s*w,s*h))
        painter.drawPixmap(QRectF(w,h,w,h), self.background_pixmap_ref, QRectF(ww-s*w,hh-s*h,s*w,s*h))
        painter.end()
        self.background_pixmap.convertFromImage(image)
        self.background_rect.setPixmap(self.background_pixmap)
    
    def mouseMoveEvent(self, event):
        self.hide_tooltip()





class TreeView(QWidget):

    def __init__(self, tree):
        super().__init__()
        self.setGeometry(0,0,VALUES.TREE_WIDTH,VALUES.TREE_HEIGHT)
        self.setFixedSize(self.width(), self.height())
        self.tree = tree
        self.background = QLabel(self)
        self.background.resize(self.width(), self.height())
        self.background.setPixmap(QPixmap(self.tree.background).scaledToHeight(self.height()))
        self.grid = QGridLayout()
        self.grid.setContentsMargins(
            VALUES.TREE_CONTENTS_MARGIN_LEFT,
            VALUES.TREE_CONTENTS_MARGIN_TOP,
            VALUES.TREE_CONTENTS_MARGIN_RIGHT,
            VALUES.TREE_CONTENTS_MARGIN_BOTTOM)
        self.setLayout(self.grid)
    
    def add_talent_view(self, talent_view):
        row = talent_view.talent.row
        col = talent_view.talent.col
        if self.grid.itemAtPosition(row, col) != None:
            self.grid.itemAtPosition(row, col).widget().delete()
        self.grid.addWidget(talent_view, row, col)
    
    def delete(self):
        pass
    
    def get_html_tree_name(self):
        return "<font color=\"gold\">{}</font>".format(self.tree.name)
    
    def get_html_points_spent(self):
        return "<font color=\"gold\">Points spent in {} Talents: </font><font color=\"white\">{}</font>".format(self.tree.name, self.tree.points_spent)





class MultiTreeView(QMainWindow):
    path_talent_frame = "./assets/talent-frame.png"
    path_talent_frame_mask = "./assets/talent-frame-mask.png"
    path_talent_background = "./assets/background.jpg"

    def __init__(self, multi_tree):
        super().__init__()
        self.multi_tree = multi_tree
        self.setGeometry(50,50,VALUES.FRAME_WIDTH,VALUES.FRAME_HEIGHT)
        self.setFixedSize(self.width(), self.height())
        self.setMouseTracking(True)

        mask_pixmap = QPixmap(self.width(),self.height())
        mask_pixmap.fill(Qt.white)
        painter = QPainter(mask_pixmap)
        painter.drawPixmap(QRect(0,0,VALUES.FRAME_WIDTH,VALUES.FRAME_HEIGHT), QPixmap(self.path_talent_frame_mask).scaledToWidth(VALUES.FRAME_WIDTH))
        painter.end()
        self.setMask(QBitmap(mask_pixmap))
        self.setAttribute(Qt.WA_TranslucentBackground, True)
     
        self.frame = QLabel()
        self.frame.setGeometry(0,0,VALUES.FRAME_WIDTH,VALUES.FRAME_HEIGHT)
        self.frame.setParent(self)
        self.frame.setPixmap(QPixmap(self.path_talent_frame).scaledToWidth(VALUES.FRAME_WIDTH))
        self.frame.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.tree_views = [None, None, None]
        self.tooltip_view = TooltipView(self)
        self.mouse_held = False
        self.mouse_old_pos = None

        self.points_remaining_label = QLabel()
        self.points_remaining_label.setParent(self)
        self.points_remaining_label.setGeometry(735, 773, 315, 17)
        self.points_remaining_label.setStyleSheet("font: {}px Arial Narrow".format(VALUES.TREE_POINTS_FONT_SIZE))
        self.points_remaining_label.setAlignment(Qt.AlignRight)
        self.points_remaining_label.setText(self.get_html_points_remaining())
        self.points_remaining_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.tree_icons = [QLabel(), QLabel(), QLabel()]
        for i in range(3):
            self.tree_icons[i].setParent(self)
            self.tree_icons[i].setGeometry(13 + i*(VALUES.TREE_WIDTH + VALUES.FRAME_INTERTREE_WIDTH), 6, 80, 80)
            self.tree_icons[i].setAttribute(Qt.WA_TransparentForMouseEvents)

        self.tree_labels = [QLabel(), QLabel(), QLabel()]
        for i in range(3):
            self.tree_labels[i].setParent(self)
            self.tree_labels[i].setGeometry(80 + VALUES.TREE_X + i*(VALUES.TREE_WIDTH + VALUES.FRAME_INTERTREE_WIDTH), 19, 296, 23)
            self.tree_labels[i].setStyleSheet("font: {}px Arial Narrow".format(VALUES.REF_TREE_NAME_FONT_SIZE))
            self.tree_labels[i].setAlignment(Qt.AlignCenter)
            self.tree_labels[i].setText("")
            self.tree_labels[i].setAttribute(Qt.WA_TransparentForMouseEvents)

        self.points_spent_labels = [QLabel(), QLabel(), QLabel()]
        for i in range(3):
            self.points_spent_labels[i].setParent(self)
            self.points_spent_labels[i].setGeometry(80 + VALUES.TREE_X + i*(VALUES.TREE_WIDTH + VALUES.FRAME_INTERTREE_WIDTH), 66, 296, 17)
            self.points_spent_labels[i].setStyleSheet("font: {}px Arial Narrow".format(VALUES.TREE_POINTS_FONT_SIZE))
            self.points_spent_labels[i].setAlignment(Qt.AlignCenter)
            self.points_spent_labels[i].setText("")
            self.points_spent_labels[i].setAttribute(Qt.WA_TransparentForMouseEvents)
        
        self.close_is_hovered = False
        self.close_button = CloseButton(self)
        self.close_button.setGeometry(1295,17,25.5,24)
        self.close_button.update_pixmap()

    def add_tree_view(self, tree_view):
        index = tree_view.tree.index
        if self.tree_views[index] != None:
            self.tree_views[index].delete()
        self.tree_views[index] = tree_view
        tree_view.setParent(self)
        tree_view.move(VALUES.TREE_X + index*(VALUES.TREE_WIDTH + VALUES.FRAME_INTERTREE_WIDTH), VALUES.TREE_Y)
        
        self.tree_icons[index].setPixmap(QPixmap(tree_view.tree.icon).scaledToWidth(self.tree_icons[index].width()))
        self.update_icons()
        self.update_frame()
        self.update_points()
    
    def get_html_points_remaining(self):
        return "<font color=\"gold\">Talent Points: </font><font color=\"white\">{}</font>".format(self.multi_tree.points_remaining)

    def check_event_in_close_area(self, event):
        return (event.x() >= 1293) and (event.x() <= 1293+28) and (event.y() >= 28) and (event.y() <= 28+24)

    def mousePressEvent(self, event):
        if self.check_event_in_close_area(event):
            self.close_button.set_pressed(True)
        else:
            self.mouse_held = True
            self.mouse_old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        self.tooltip_view.hide_tooltip()
        self.close_button.set_hovered(self.check_event_in_close_area(event))
        if self.mouse_held:
            mouse_new_pos = event.globalPos()
            curr_pos = self.mapToGlobal(self.pos())
            diff_pos = mouse_new_pos - self.mouse_old_pos
            new_pos = self.mapFromGlobal(curr_pos + diff_pos)
            self.move(new_pos)
            self.mouse_old_pos = mouse_new_pos

    def mouseReleaseEvent(self, event):
        self.close_button.set_pressed(False)
        self.mouse_held = False
        self.mouse_old_pos = None
    
    def update_icons(self):
        for i in range(3):
            self.tree_icons[i].raise_()

    def update_frame(self):
        self.frame.raise_()
        self.close_button.raise_()
    
    def update_points(self):
        self.points_remaining_label.raise_()
        self.points_remaining_label.setText(self.get_html_points_remaining())
        for i in range(3):
            self.tree_labels[i].raise_()
            self.points_spent_labels[i].raise_()
            if self.tree_views[i] != None:
                self.tree_labels[i].setText(self.tree_views[i].get_html_tree_name())
                self.points_spent_labels[i].setText(self.tree_views[i].get_html_points_spent())

    def update_tooltip(self, talent_view):
        self.tooltip_view.update_tooltip(talent_view)


    


class CloseButton(QLabel):

    def __init__(self, multi_tree_view):
        super().__init__()
        self.setParent(multi_tree_view)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hovered = False
        self.pressed = False
        self.multi_tree_view = multi_tree_view
    
    def set_hovered(self, hovered):
        if self.hovered != hovered:
            self.hovered = hovered
            self.update_pixmap()
    
    def set_pressed(self, pressed):
        if self.hovered and self.pressed and not pressed:
            RUNTIME.get_app().quit()
        if self.pressed != pressed:
            self.pressed = pressed
        self.update_pixmap()
    
    def update_pixmap(self):
        if self.hovered and self.pressed:
            self.setPixmap(QPixmap(PATHS.CLOSE_PRESSED_HOVER).scaledToWidth(self.width()))
        elif self.hovered:
            self.setPixmap(QPixmap(PATHS.CLOSE_HOVER).scaledToWidth(self.width()))
        elif self.pressed:
            self.setPixmap(QPixmap(PATHS.CLOSE_PRESSED_NOHOVER).scaledToWidth(self.width()))
        else:
            self.setPixmap(QPixmap(PATHS.CLOSE_NOHOVER).scaledToWidth(self.width()))
        self.raise_()
        self.update()
        





if __name__ == "__main__":

    RUNTIME.init()

    multi_tree = MultiTreeData("Awesome Talent Tree")
    trees = []
    talents = [[],[],[]]
    for i in range(3):
        icon_names = os.listdir("./icons/spells")
        icon_paths = ["./icons/spells/"+s for s in random.choices(icon_names, k=28)]
        tree = TreeData("spec", icon_paths[0], "./assets/backgrounds/druid_feral.jpeg", index=i)
        for y in range(7):
            for x in range(4):
                talent = TalentData("Nature's Blessing", icon_paths[4*y+x], 5, "Description $%"+" aasdwe"*int(random.random()*20), "10 20 30 40 50", row=y, col=x)
                talents[i] += [talent]
                tree.add_talent(talent)
        trees += [tree]
        multi_tree.add_tree(tree)
    

    # multi_tree = MultiTreeData.load_from_json("./_test_data/multi_tree_example.json")

    RUNTIME.show(multi_tree)







