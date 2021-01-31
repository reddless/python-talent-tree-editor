from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from core import *
from buttons import *
import os
import json
import numpy as np
import random



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class Hoverable():
    def __init__(self):
        super().__init__()
        self.hovered = False
    def set_hovered(self, hovered):
        if self.hovered != hovered:
            self.hovered = hovered
            self.update()

class Pressable():
    def __init__(self):
        super().__init__()
        self.pressed = False
    def set_pressed(self, pressed):
        if self.pressed != pressed:
            self.pressed = pressed
            self.update()

class Selectable():
    def __init__(self):
        super().__init__()
        self.selected = False
    def set_selected(self, selected):
        if self.selected != selected:
            self.selected = selected
            self.update()



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TalentView(QWidget, Hoverable, Pressable, Selectable):

    def __init__(self, talent):
        super().__init__()
        self.setGeometry(0, 0, VALUES.TALENT_CELL_SIZE, VALUES.TALENT_CELL_SIZE)
        self.talent = talent
        self.blocking_arrows = set()
        font = QFont()
        font.setPointSize(int(round(VALUES.TALENT_FONT_SIZE)))
        self.points_text = QLabel(self)
        self.points_text.setFont(font)
        self.points_text.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.points_text.setGeometry(VALUES.TALENT_POINTS_OFFSET_X,VALUES.TALENT_POINTS_OFFSET_Y,VALUES.TALENT_POINTS_SIZE,VALUES.TALENT_POINTS_SIZE)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover)
        self.rect_icon = QRect(*(lambda x: ((VALUES.TALENT_CELL_SIZE-x)/2,(VALUES.TALENT_CELL_SIZE-x)/2,x,x))(VALUES.TALENT_ICON_SIZE))
        self.rect_border = QRect(*(lambda x: ((VALUES.TALENT_CELL_SIZE-x)/2,(VALUES.TALENT_CELL_SIZE-x)/2,x,x))(VALUES.TALENT_BORDER_SIZE))
        self.rect_hover = QRect(*(lambda x: ((VALUES.TALENT_CELL_SIZE-x)/2,(VALUES.TALENT_CELL_SIZE-x)/2,x,x))(VALUES.TALENT_HOVER_SIZE))
        self.rect_accent = QRect(*(lambda x: ((VALUES.TALENT_CELL_SIZE-x)/2,(VALUES.TALENT_CELL_SIZE-x)/2,x,x))(VALUES.TALENT_ACCENT_SIZE))
        self.rect_bubble = QRect(VALUES.TALENT_BUBBLE_OFFSET,VALUES.TALENT_BUBBLE_OFFSET,VALUES.TALENT_BUBBLE_SIZE,VALUES.TALENT_BUBBLE_SIZE)
        self.rect_add_talent_h = QRect(38,28,24,44)
        self.rect_add_talent_v = QRect(28,38,44,24)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        if len(self.blocking_arrows) > 0:
            self.points_text.setVisible(False)
        elif RUNTIME.in_edit_mode:
            if self.talent.name == None:
                if self.hovered:
                    painter.drawPixmap(self.rect_icon, PIXMAPS.TALENT_ADD_BUTTON_HOVER)
                else:
                    painter.drawPixmap(self.rect_icon, PIXMAPS.TALENT_ADD_BUTTON_NOHOVER)
                self.points_text.setVisible(False)
            else:
                if self.hovered or self.selected:
                    painter.drawPixmap(self.rect_icon, PIXMAPS.get_pixmap(self.talent.icon, greyscale=False))
                    painter.drawPixmap(self.rect_border, PIXMAPS.TALENT_BORDER)
                    painter.drawPixmap(self.rect_hover, PIXMAPS.TALENT_HOVER_GOLD)
                    painter.drawPixmap(self.rect_accent, PIXMAPS.TALENT_ACCENT_GOLD)
                    painter.drawPixmap(self.rect_bubble, PIXMAPS.TALENT_BUBBLE_GOLD)
                    self.points_text.setText(self.get_html_ranks())
                    self.points_text.setVisible(True)
                else:
                    painter.drawPixmap(self.rect_icon, PIXMAPS.get_pixmap(self.talent.icon, greyscale=True))
                    painter.drawPixmap(self.rect_border, PIXMAPS.TALENT_BORDER)
                    painter.drawPixmap(self.rect_accent, PIXMAPS.TALENT_ACCENT_GREY)
                    painter.drawPixmap(self.rect_bubble, PIXMAPS.TALENT_BUBBLE_GREY)
                    self.points_text.setText(self.get_html_ranks(color="gray"))
                    self.points_text.setVisible(True)
        else:
            if self.talent.name == None:
                return
            else:
                if self.talent.check_can_add_point() or self.talent.points_spent > 0:
                    painter.drawPixmap(self.rect_icon, PIXMAPS.get_pixmap(self.talent.icon, greyscale=False))
                    painter.drawPixmap(self.rect_border, PIXMAPS.TALENT_BORDER)
                    if self.hovered: 
                        painter.drawPixmap(self.rect_hover, PIXMAPS.TALENT_HOVER_BLUE)
                    if self.talent.points_spent == self.talent.ranks:
                        painter.drawPixmap(self.rect_accent, PIXMAPS.TALENT_ACCENT_GOLD)
                    else:
                        painter.drawPixmap(self.rect_accent, PIXMAPS.TALENT_ACCENT_GREEN)
                    painter.drawPixmap(self.rect_bubble, PIXMAPS.TALENT_BUBBLE_GOLD)
                    self.points_text.setText(self.get_html_points())
                    self.points_text.setVisible(True)
                else:
                    painter.drawPixmap(self.rect_icon, PIXMAPS.get_pixmap(self.talent.icon, greyscale=True))
                    painter.drawPixmap(self.rect_border, PIXMAPS.TALENT_BORDER)
                    if self.hovered: 
                        painter.drawPixmap(self.rect_hover, PIXMAPS.TALENT_HOVER_BLUE)
                    painter.drawPixmap(self.rect_accent, PIXMAPS.TALENT_ACCENT_GREY)
                    self.points_text.setVisible(False)

    def mousePressEvent(self, event):
        if self.check_event(event):
            RUNTIME.set_curr_pressed(self)
            if RUNTIME.in_edit_mode:
                self.set_selected(True)
            return

    def mouseMoveEvent(self, event):
        if self.check_event(event):
            RUNTIME.set_curr_hovered(self)
        else:
            if RUNTIME.in_edit_mode and self.pressed:
                for row in range(self.talent.row,7):
                    for col in range(4):
                        dst_talent_view = self.talent.tree.view.grid_views[row,col]
                        if dst_talent_view.check_event(event, offset=QPoint(self.x() - dst_talent_view.x(), self.y() - dst_talent_view.y())):
                            RUNTIME.set_curr_hovered(dst_talent_view)
            else:
                RUNTIME.clear_hovered()

    def mouseReleaseEvent(self, event):
        if self.check_event(event):
            if RUNTIME.in_edit_mode and event.button() == Qt.LeftButton:
                RUNTIME.get_top_view().show_edit_talent_view(self.talent)
                RUNTIME.clear_pressed()
                return
            elif event.button() == Qt.LeftButton:
                self.talent.add_point()
            elif event.button() == Qt.RightButton:
                self.talent.subtract_point()
            self.talent.tree.reevaluate_subtree(0)
            RUNTIME.get_top_view().update_points()
            RUNTIME.get_top_view().update_tooltip(self)
            RUNTIME.clear_pressed()
            return
        else:
            if RUNTIME.in_edit_mode:
                self.set_selected(False)
                self.talent.tree.add_arrow(self.talent, RUNTIME.curr_hovered.talent)
    
    def wheelEvent(self, event):
        if self.check_event(event) and not RUNTIME.in_edit_mode:
            if event.angleDelta().y() > 0:
                self.talent.add_point()
            elif event.angleDelta().y() < 0:
                self.talent.subtract_point()
            self.talent.tree.reevaluate_subtree(0)
            RUNTIME.get_top_view().update_points()
            RUNTIME.get_top_view().update_tooltip(self)
    
    def check_event(self, event, offset=QPoint(0,0)):
        if RUNTIME.edit_window_open or len(self.blocking_arrows):
            return False
        elif RUNTIME.in_edit_mode and self.talent.name == None:
            return event.pos() + offset in self.rect_add_talent_h or event.pos() in self.rect_add_talent_v
        else:
            return event.pos() + offset in self.rect_border

    def get_html_tooltip(self):
        text = "<font color=\"white\" size=5>{}</font>".format(self.talent.name)
        text += "<br/><font color=\"white\">Rank {}/{}</font>".format(self.talent.points_spent, self.talent.ranks)
        if not self.talent.check_sufficient_earlier_points():
            text += "<br/><font color=\"red\">Requires {} points in {} Talents</font>".format(5*(self.talent.row), self.talent.name)
        if not self.talent.check_prerequisite_is_satisfied():
            text += "<br/><font color=\"red\">Requires {} points in {}</font>".format(self.talent.prerequisite.ranks, self.talent.prerequisite.name)
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
    
    def get_html_ranks(self, color="gold"):
        return "<font color=\"{}\">{}</font>".format(color, self.talent.ranks)
    
    def set_hovered(self, hovered):
        if self.hovered != hovered:
            self.hovered = hovered
            if self.hovered and self.talent.name != None:
                RUNTIME.get_top_view().update_tooltip(self)
            else:
                RUNTIME.get_top_view().hide_tooltip()
            self.update()
    
    def add_blocking_arrow(self, arrow):
        self.blocking_arrows |= {arrow}
        if len(self.blocking_arrows) == 1:
            self.update()
    
    def remove_blocking_arrow(self, arrow):
        self.blocking_arrows -= {arrow}
        if len(self.blocking_arrows) == 0:
            self.update()



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TreeView(QWidget):

    def __init__(self, tree):
        super().__init__()
        self.setGeometry(0,0,VALUES.TREE_WIDTH,VALUES.TREE_HEIGHT)
        self.setFixedSize(self.width(), self.height())
        self.tree = tree
        self.background = QLabel(self)
        self.background.resize(self.width(), self.height())
        self.background.setPixmap(QPixmap(self.tree.background).scaledToHeight(self.height()))
        self.background.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.grid_views = np.ndarray(shape=(7,4), dtype=TalentView)
    
    def add_arrow_view(self, arrow_view):
        arrow_view.update()
        arrow_view.setVisible(True)
        src = arrow_view.arrow.src
        dst = arrow_view.arrow.dst
        for col in range(min(src.col, dst.col), max(src.col, dst.col)):
            self.grid_views[src.row, col].add_blocking_arrow(arrow_view)
        for row in range(src.row, dst.row):
            self.grid_views[row, dst.col].add_blocking_arrow(arrow_view)
        self.grid_views[src.row, src.col].remove_blocking_arrow(arrow_view)
        self.update()
    
    def remove_arrow_view(self, arrow_view):
        arrow_view.setParent(None)
        arrow_view.setVisible(False)
        arrow_view.update()
        src = arrow_view.arrow.src
        dst = arrow_view.arrow.dst
        for col in range(min(src.col, dst.col), max(src.col, dst.col)):
            self.grid_views[src.row, col].remove_blocking_arrow(arrow_view)
        for row in range(src.row, dst.row):
            self.grid_views[row, dst.col].remove_blocking_arrow(arrow_view)

    def data_updated(self):
        self.background.setPixmap(QPixmap(self.tree.background).scaledToHeight(self.height()))

    def set_talent_view(self, talent_view):
        row = talent_view.talent.row
        col = talent_view.talent.col
        self.grid_views[row,col] = talent_view
        talent_view.setParent(self)
        W = (VALUES.TREE_WIDTH-40)/4
        H = (VALUES.TREE_HEIGHT-10)/7
        w = talent_view.width()
        h = talent_view.height()
        ww = (W-w)/2
        hh = (H-h)/2
        x = 20 + col*W + ww
        y = 5 + row*H + hh
        talent_view.move(x, y)
        talent_view.update()
    
    def get_html_tree_name(self):
        return "<font color=\"gold\">{}</font>".format(self.tree.name)
    
    def get_html_points_spent(self):
        return "<font color=\"gold\">Points spent in {} Talents: </font><font color=\"white\">{}</font>".format(self.tree.name, self.tree.points_spent)



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class MultiTreeView(QMainWindow):

    def __init__(self, multi_tree):
        super().__init__()
        self.multi_tree = multi_tree
        self.setGeometry(50,50,VALUES.FRAME_WIDTH,VALUES.FRAME_HEIGHT)
        self.setFixedSize(self.width(), self.height())
        self.setMouseTracking(True)

        mask_pixmap = QPixmap(self.width(),self.height())
        mask_pixmap.fill(Qt.white)
        painter = QPainter(mask_pixmap)
        painter.drawPixmap(QRect(0,0,VALUES.FRAME_WIDTH,VALUES.FRAME_HEIGHT), QPixmap(PATHS.TALENT_FRAME_MASK).scaledToWidth(VALUES.FRAME_WIDTH))
        painter.end()
        self.setMask(QBitmap(mask_pixmap))
        self.setAttribute(Qt.WA_TranslucentBackground, True)
     
        self.frame = QLabel()
        self.frame.setGeometry(0,0,VALUES.FRAME_WIDTH,VALUES.FRAME_HEIGHT)
        self.frame.setParent(self)
        self.frame.setPixmap(QPixmap(PATHS.TALENT_FRAME).scaledToWidth(VALUES.FRAME_WIDTH))
        self.frame.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.tree_views = [None, None, None]
        self.tooltip_view = TooltipView(self)
        self.edit_talent_view = EditTalentView(self)
        self.mouse_held = False
        self.mouse_old_pos = None

        self.points_remaining_label = QLabel()
        self.points_remaining_label.setParent(self)
        self.points_remaining_label.setGeometry(960, 773, 315, 17)
        self.points_remaining_label.setStyleSheet("font: {}px Arial Narrow".format(VALUES.TREE_POINTS_FONT_SIZE))
        self.points_remaining_label.setAlignment(Qt.AlignRight)
        self.points_remaining_label.setText(self.get_html_points_remaining())
        self.points_remaining_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.tree_icons = [QLabel(), QLabel(), QLabel()]
        for i in range(3):
            self.tree_icons[i].setParent(self)
            self.tree_icons[i].setGeometry(
                VALUES.TREE_ICON_X + i*(VALUES.TREE_WIDTH + VALUES.FRAME_INTERTREE_WIDTH),
                VALUES.TREE_ICON_Y,
                VALUES.TREE_ICON_SIZE,
                VALUES.TREE_ICON_SIZE)
            self.tree_icons[i].setAttribute(Qt.WA_TransparentForMouseEvents)

        self.tree_labels = [QLabel(), QLabel(), QLabel()]
        for i in range(3):
            self.tree_labels[i].setParent(self)
            self.tree_labels[i].setGeometry(
                VALUES.TREE_LABEL_X + VALUES.TREE_X + i*(VALUES.TREE_WIDTH + VALUES.FRAME_INTERTREE_WIDTH), 
                VALUES.TREE_LABEL_Y,
                VALUES.TREE_LABEL_WIDTH,
                VALUES.TREE_LABEL_HEIGHT)
            self.tree_labels[i].setStyleSheet("font: {}px Arial Narrow".format(VALUES.REF_TREE_NAME_FONT_SIZE))
            self.tree_labels[i].setAlignment(Qt.AlignCenter)
            self.tree_labels[i].setText("")
            self.tree_labels[i].setAttribute(Qt.WA_TransparentForMouseEvents)

        self.points_spent_labels = [QLabel(), QLabel(), QLabel()]
        for i in range(3):
            self.points_spent_labels[i].setParent(self)
            self.points_spent_labels[i].setGeometry(
                VALUES.TREE_POINTS_X + VALUES.TREE_X + i*(VALUES.TREE_WIDTH + VALUES.FRAME_INTERTREE_WIDTH),
                VALUES.TREE_POINTS_Y,
                VALUES.TREE_POINTS_WIDTH,
                VALUES.TREE_POINTS_HEIGHT)
            self.points_spent_labels[i].setStyleSheet("font: {}px Arial Narrow".format(VALUES.TREE_POINTS_FONT_SIZE))
            self.points_spent_labels[i].setAlignment(Qt.AlignCenter)
            self.points_spent_labels[i].setText("")
            self.points_spent_labels[i].setAttribute(Qt.WA_TransparentForMouseEvents)
        
        self.buttons = {}

        self.close_is_hovered = False
        self.buttons["close"] = CloseButtonView(self, f=lambda: RUNTIME.get_app().quit())
        self.buttons["close"].move(VALUES.CLOSE_MAIN_X, VALUES.CLOSE_MAIN_Y)
        self.buttons["close"].update_pixmap()

        self.buttons["save"] = SaveButtonView(self)
        self.buttons["save"].move(VALUES.MAIN_BUTTON_SAVE_X, VALUES.MAIN_BUTTON_SAVE_Y)
        self.buttons["save"].update_pixmap()

        self.buttons["load"] = LoadButtonView(self)
        self.buttons["load"].move(VALUES.MAIN_BUTTON_LOAD_X, VALUES.MAIN_BUTTON_LOAD_Y)
        self.buttons["load"].update_pixmap()

        self.buttons["edit"] = EditButtonView(self, f=lambda:  [
            self.buttons["edit"].set_enabled(False),
            self.buttons["accept"].set_enabled(True),
            RUNTIME.set_edit_mode(True),
            self.update_talents(),
            self.update_icons()])
        self.buttons["edit"].move(VALUES.MAIN_BUTTON_EDIT_X, VALUES.MAIN_BUTTON_EDIT_Y)
        self.buttons["edit"].update_pixmap()

        self.buttons["accept"] = AcceptButtonView(self, f=lambda: [
            self.buttons["edit"].set_enabled(True),
            self.buttons["accept"].set_enabled(False),
            RUNTIME.set_edit_mode(False),
            self.update_talents(),
            self.update_icons()])
        self.buttons["accept"].move(VALUES.MAIN_BUTTON_EDIT_X, VALUES.MAIN_BUTTON_EDIT_Y)
        self.buttons["accept"].update_pixmap()
        self.buttons["accept"].set_enabled(False)

    def set_tree_view(self, tree_view):
        index = tree_view.tree.index
        self.tree_views[index] = tree_view
        tree_view.setParent(self)
        tree_view.move(VALUES.TREE_X + index*(VALUES.TREE_WIDTH + VALUES.FRAME_INTERTREE_WIDTH), VALUES.TREE_Y)
        self.update_icon(index)
    
    def get_html_points_remaining(self):
        return "<font color=\"gold\">Talent Points: </font><font color=\"white\">{}</font>".format(self.multi_tree.points_remaining)

    def mousePressEvent(self, event):
        for button_view in self.buttons.values():
            if event.pos() in button_view.geometry() and button_view.enabled:
                RUNTIME.set_curr_pressed(button_view)
                return
        self.mouse_held = True
        self.mouse_old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        RUNTIME.last_mouse_move_event = event
        self.tooltip_view.hide_tooltip()
        for button_view in self.buttons.values():
            if event.pos() in button_view.geometry() and button_view.enabled:
                RUNTIME.set_curr_hovered(button_view) 
                return
        RUNTIME.clear_hovered()
        if self.mouse_held:
            mouse_new_pos = event.globalPos()
            curr_pos = self.mapToGlobal(self.pos())
            diff_pos = mouse_new_pos - self.mouse_old_pos
            new_pos = self.mapFromGlobal(curr_pos + diff_pos)
            self.move(new_pos)
            self.mouse_old_pos = mouse_new_pos

    def mouseReleaseEvent(self, event):
        for button_view in self.buttons.values():
            if event.pos() in button_view.geometry() and button_view.enabled:
                RUNTIME.clear_pressed()
                self.mouse_held = False
                self.mouse_old_pos = None
                if RUNTIME.last_mouse_move_event != None:
                    self.mouseMoveEvent(RUNTIME.last_mouse_move_event)
                return
        RUNTIME.clear_pressed()
        self.mouse_held = False
        self.mouse_old_pos = None
    
    def update_icon(self, tree_index):
        if self.tree_views[tree_index] != None:
            tree = self.tree_views[tree_index].tree
            tree_icon = self.tree_icons[tree_index]
            if RUNTIME.in_edit_mode:
                if RUNTIME.curr_hovered == tree_icon:
                    tree_icon.setPixmap(PIXMAPS.get_pixmap(tree.icon).scaledToWidth(tree_icon.width()))
                    tree_icon.raise_()
                    self.update_frame()
                else:
                    tree_icon.setPixmap(PIXMAPS.get_pixmap(tree.icon, greyscale=True).scaledToWidth(tree_icon.width()))
                    tree_icon.raise_()
                    self.update_frame()
            else:
                if self.multi_tree.points_remaining == 0:
                    saturation = 1-((51-self.tree_views[tree_index].tree.points_spent)/51)**3
                    tree_icon.setPixmap(UTILS.get_pixmap_with_saturation(tree.icon, saturation).scaledToWidth(tree_icon.width()))
                    tree_icon.raise_()
                    self.update_frame()
                else:
                    tree_icon.setPixmap(PIXMAPS.get_pixmap(tree.icon).scaledToWidth(tree_icon.width()))
                    tree_icon.raise_()
                    self.update_frame()
    
    def update_icons(self):
        for index in range(3):
            self.update_icon(index)
    
    def update_frame(self):
        self.frame.raise_()
        for button in self.buttons.values():
            button.raise_()
        self.update_points()
        self.tooltip_view.background.raise_()
        self.tooltip_view.raise_()
    
    def update_points(self):
        self.points_remaining_label.raise_()
        self.points_remaining_label.setText(self.get_html_points_remaining())
        for index in range(3):
            self.tree_labels[index].raise_()
            self.points_spent_labels[index].raise_()
            if self.tree_views[index] != None:
                self.tree_labels[index].setText(self.tree_views[index].get_html_tree_name())
                self.points_spent_labels[index].setText(self.tree_views[index].get_html_points_spent())
    
    def update_talents(self):
        for index in range(3):
            self.tree_views[index].update()

    def update_tooltip(self, talent_view):
        self.tooltip_view.update_tooltip(talent_view)
    
    def show_edit_talent_view(self, talent):
        self.edit_talent_view.open_window(talent)



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TooltipView(QLabel):

    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setStyleSheet("font: 14pt Verdana; padding: 7px")
        self.setFixedWidth(VALUES.TOOLTIP_WIDTH)
        self.setVisible(False)
        self.setWordWrap(True)
        self.background = BackgroundView(parent)
        self.background_pixmap = None
        self.previous_talent_view = None
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.background.setAttribute(Qt.WA_TransparentForMouseEvents)
    
    def update_tooltip(self, talent_view):
        old_x = self.x()
        old_y = self.y()
        old_geometry = self.geometry()
        self.setText(talent_view.get_html_tooltip())
        self.adjustSize()
        tree_position = talent_view.talent.tree.view.geometry().topLeft()
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
            self.background.update_background(self)
        if not self.isVisible():
            self.setVisible(True)
        if not self.background.isVisible():
            self.background.setVisible(True)
        self.background.raise_()
        self.raise_()
        self.update()
    
    def hide_tooltip(self):
        self.setVisible(False)
        self.background.setVisible(False)



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class EditTalentView(QLabel):

    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setVisible(False)
        self.setGeometry(
            parent.width()/2 - VALUES.EDIT_TALENT_FRAME_WIDTH/2,
            parent.height()/2 - VALUES.EDIT_TALENT_FRAME_HEIGHT/2,
            VALUES.EDIT_TALENT_FRAME_WIDTH,
            VALUES.EDIT_TALENT_FRAME_HEIGHT)
        self.setMouseTracking(True)
        self.modifying_talent = None

        self.pick_icon_scroll_view_label = QLabel(self)
        self.pick_icon_scroll_view_label.setText("Pick an icon:")
        self.pick_icon_scroll_view_label.setStyleSheet("background: transparent; font: 9px Arial Narrow; color: white; font-weight: normal")
        self.pick_icon_scroll_view_label.setGeometry(
            VALUES.EDIT_TALENT_LABEL_ICON_X,
            VALUES.EDIT_TALENT_LABEL_ICON_Y,
            VALUES.EDIT_TALENT_LABEL_ICON_W,
            VALUES.EDIT_TALENT_LABEL_ICON_H)

        self.pick_icon_scroll_view = PickIconScrollView(self)

        self.edit_talent_icon = TalentIconView(self, icon_size=VALUES.EDIT_TALENT_SELECTED_ICON_SIZE)
        self.edit_talent_icon.move(VALUES.EDIT_TALENT_SELECTED_ICON_X, VALUES.EDIT_TALENT_SELECTED_ICON_Y)
        self.edit_talent_icon.set_icon(PATHS.ICON_QUESTION)

        self.edit_talent_name_label = QLabel(self)
        self.edit_talent_name_label.setText("Enter a talent name:")
        self.edit_talent_name_label.setStyleSheet("background: transparent; font: 9px Arial Narrow; color: white; font-weight: normal")
        self.edit_talent_name_label.setGeometry(
            VALUES.EDIT_TALENT_LABEL_NAME_X,
            VALUES.EDIT_TALENT_LABEL_NAME_Y,
            VALUES.EDIT_TALENT_LABEL_NAME_W,
            VALUES.EDIT_TALENT_LABEL_NAME_H)

        self.edit_talent_name = QTextEdit(self)
        self.edit_talent_name.setStyleSheet("background: transparent; font: 16px Arial Narrow; color: white")
        self.edit_talent_name.setGeometry(
            VALUES.EDIT_TALENT_TEXTEDIT_NAME_X,
            VALUES.EDIT_TALENT_TEXTEDIT_NAME_Y,
            VALUES.EDIT_TALENT_TEXTEDIT_NAME_W,
            VALUES.EDIT_TALENT_TEXTEDIT_NAME_H)
        self.edit_talent_name.setTabChangesFocus(True)
        self.edit_talent_name_background = BackgroundView(self)
        self.edit_talent_name_background.update_background(self.edit_talent_name)

        self.edit_talent_ranks = QLineEdit(self)
        self.edit_talent_ranks.setStyleSheet("background: transparent; font: 14px Arial Narrow; color: gold; padding: 1px, 0px, 0px, 7px")
        self.edit_talent_ranks.setGeometry(
            VALUES.EDIT_TALENT_TEXTEDIT_RANKS_X,
            VALUES.EDIT_TALENT_TEXTEDIT_RANKS_Y,
            VALUES.EDIT_TALENT_TEXTEDIT_RANKS_W,
            VALUES.EDIT_TALENT_TEXTEDIT_RANKS_H)
        self.edit_talent_ranks.setAlignment(Qt.AlignCenter)
        self.edit_talent_ranks.setMaxLength(1)
        self.edit_talent_ranks.setValidator(QIntValidator())
        self.edit_talent_ranks_background = BackgroundView(self)
        self.edit_talent_ranks_background.update_background(self.edit_talent_ranks)

        self.edit_talent_desc_text_label = QLabel(self)
        self.edit_talent_desc_text_label.setText("Enter a talent description:")
        self.edit_talent_desc_text_label.setStyleSheet("background: transparent; font: 9px Arial Narrow; color: white; font-weight: normal")
        self.edit_talent_desc_text_label.setGeometry(
            VALUES.EDIT_TALENT_LABEL_TEXT_X,
            VALUES.EDIT_TALENT_LABEL_TEXT_Y,
            VALUES.EDIT_TALENT_LABEL_TEXT_W,
            VALUES.EDIT_TALENT_LABEL_TEXT_H)
        
        self.edit_talent_desc_text = QTextEdit(self)
        self.edit_talent_desc_text.setStyleSheet("background: transparent; font: 15px Arial Narrow; color: gold")
        self.edit_talent_desc_text.setGeometry(
            VALUES.EDIT_TALENT_TEXTEDIT_TEXT_X,
            VALUES.EDIT_TALENT_TEXTEDIT_TEXT_Y,
            VALUES.EDIT_TALENT_TEXTEDIT_TEXT_W,
            VALUES.EDIT_TALENT_TEXTEDIT_TEXT_H)
        self.edit_talent_desc_text.setTabChangesFocus(True)
        self.edit_talent_desc_text_background = BackgroundView(self)
        self.edit_talent_desc_text_background.update_background(self.edit_talent_desc_text)

        self.edit_talent_desc_vals_label = QLabel(self)
        self.edit_talent_desc_vals_label.setText("Enter numeric values to be used per rank:")
        self.edit_talent_desc_vals_label.setStyleSheet("background: transparent; font: 9px Arial Narrow; color: white; font-weight: normal")
        self.edit_talent_desc_vals_label.setGeometry(
            VALUES.EDIT_TALENT_LABEL_VALS_X,
            VALUES.EDIT_TALENT_LABEL_VALS_Y,
            VALUES.EDIT_TALENT_LABEL_VALS_W,
            VALUES.EDIT_TALENT_LABEL_VALS_H)
        
        self.edit_talent_desc_vals = QTextEdit(self)
        self.edit_talent_desc_vals.setStyleSheet("background: transparent; font: 15px Arial Narrow; color: gold")
        self.edit_talent_desc_vals.setGeometry(
            VALUES.EDIT_TALENT_TEXTEDIT_VALS_X,
            VALUES.EDIT_TALENT_TEXTEDIT_VALS_Y,
            VALUES.EDIT_TALENT_TEXTEDIT_VALS_W,
            VALUES.EDIT_TALENT_TEXTEDIT_VALS_H)
        self.edit_talent_desc_vals.setTabChangesFocus(True)
        self.edit_talent_desc_vals_background = BackgroundView(self)
        self.edit_talent_desc_vals_background.update_background(self.edit_talent_desc_vals)

        self.frame = QLabel()
        self.frame.setParent(self)
        self.frame.setGeometry(0,0,self.width(),self.height())
        self.frame.setPixmap(QPixmap(PATHS.EDIT_TALENT_FRAME).scaledToWidth(self.width()))
        self.frame.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.label = QLabel()
        self.label.setParent(self)
        self.label.setGeometry(
            VALUES.EDIT_TALENT_LABEL_FRAME_X,
            VALUES.EDIT_TALENT_LABEL_FRAME_Y,
            VALUES.EDIT_TALENT_LABEL_FRAME_W,
            VALUES.EDIT_TALENT_LABEL_FRAME_H)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font: 16px Arial Narrow; color: gold")
        self.label.setText("Edit Talent")

        self.buttons = {}

        self.buttons["save"] = SaveButtonView(self, f=lambda: self.save_talent_prompt())
        self.buttons["save"].move(VALUES.EDIT_TALENT_BUTTON_SAVE_X, VALUES.EDIT_TALENT_BUTTON_SAVE_Y)
        self.buttons["save"].update_pixmap()

        self.buttons["load"] = LoadButtonView(self, f=lambda: self.load_talent_prompt())
        self.buttons["load"].move(VALUES.EDIT_TALENT_BUTTON_LOAD_X, VALUES.EDIT_TALENT_BUTTON_LOAD_Y)
        self.buttons["load"].update_pixmap()

        self.buttons["accept"] = AcceptButtonView(self, f=lambda: self.accept_talent_edit())
        self.buttons["accept"].move(VALUES.EDIT_TALENT_BUTTON_ACCEPT_X, VALUES.EDIT_TALENT_BUTTON_ACCEPT_Y)
        self.buttons["accept"].update_pixmap()

        self.buttons["delete"] = DeleteButtonView(self, f=lambda: self.delete_talent())
        self.buttons["delete"].move(VALUES.EDIT_TALENT_BUTTON_DELETE_X, VALUES.EDIT_TALENT_BUTTON_DELETE_Y)
        self.buttons["delete"].update_pixmap()

        self.buttons["close"] = CloseButtonView(self, f=lambda: self.close_window())
        self.buttons["close"].move(VALUES.EDIT_TALENT_BUTTON_CLOSE_X, VALUES.EDIT_TALENT_BUTTON_CLOSE_Y)
        self.buttons["close"].update_pixmap()
    
    def paintEvent(self, event):
        self.edit_talent_icon.raise_()
        self.edit_talent_ranks_background.raise_()
        self.edit_talent_name_background.raise_()
        self.edit_talent_desc_text_background.raise_()
        self.edit_talent_desc_vals_background.raise_()
        self.edit_talent_ranks.raise_()
        self.edit_talent_name.raise_()
        self.edit_talent_desc_text.raise_()
        self.edit_talent_desc_vals.raise_()
        self.edit_talent_name_label.raise_()
        self.edit_talent_desc_text_label.raise_()
        self.edit_talent_desc_vals_label.raise_()
        self.pick_icon_scroll_view_label.raise_()
        self.raise_()
    
    def mousePressEvent(self, event):
        for button_view in self.buttons.values():
            if event.pos() in button_view.geometry():
                RUNTIME.set_curr_pressed(button_view)
                return
    
    def mouseMoveEvent(self, event):
        for button_view in self.buttons.values():
            if event.pos() in button_view.geometry():
                if RUNTIME.curr_hovered != button_view:
                    RUNTIME.set_curr_hovered(button_view)
                return
        RUNTIME.clear_hovered()
    
    def mouseReleaseEvent(self, event):
        for button_view in self.buttons.values():
            if event.pos() in button_view.geometry():
                RUNTIME.clear_pressed()
                return
        RUNTIME.clear_pressed()

    def open_window(self, talent):
        RUNTIME.edit_window_open = True
        self.modifying_talent = talent
        if talent.name == None:
            self.edit_talent_icon.set_icon(PATHS.ICON_QUESTION)
            self.edit_talent_name.clear()
            self.edit_talent_ranks.clear()
            self.edit_talent_desc_text.clear()
            self.edit_talent_desc_vals.clear()
        else:
            self.edit_talent_icon.set_icon(talent.icon)
            self.edit_talent_name.setText(talent.name)
            self.edit_talent_ranks.setText(str(talent.ranks))
            self.edit_talent_desc_text.setText(talent.description_text)
            self.edit_talent_desc_vals.setText(talent.description_values)
        self.setVisible(True)
        self.edit_talent_name.setFocus()
        self.raise_()
        self.update()

    def close_window(self):
        self.modifying_talent.view.set_selected(False)
        self.setVisible(False)
        RUNTIME.edit_window_open = False
    
    def create_talent_data_dict(self):
        name = self.edit_talent_name.toPlainText()
        icon = self.edit_talent_icon.icon
        ranks = self.edit_talent_ranks.text()
        text = self.edit_talent_desc_text.toPlainText()
        vals = self.edit_talent_desc_vals.toPlainText()
        talent_data_dict = {
            "name": name,
            "icon": icon,
            "ranks": int(ranks),
            "description_text": text,
            "description_values": vals,
            "row": self.modifying_talent.row,
            "col": self.modifying_talent.col
        }
        return talent_data_dict
    
    def delete_talent(self):
        self.modifying_talent.clear()
        self.close_window()
    
    def accept_talent_edit(self):
        try:
            self.modifying_talent.load_from_dict(self.create_talent_data_dict())
            self.modifying_talent.view.update()
            self.close_window()
        except Exception as e:
            print(e)
    
    def load_talent_prompt(self):
        try:
            filename = QFileDialog.getOpenFileName(self, "Load Talent JSON", "./", "*.json")[0]
            f = open(filename, "r")
            talent_data_dict = json.load(f)
            f.close()
            self.edit_talent_name.setText(talent_data_dict["name"])
            self.edit_talent_icon.set_icon(talent_data_dict["icon"])
            self.edit_talent_ranks.setText(str(talent_data_dict["ranks"]))
            self.edit_talent_desc_text.setText(talent_data_dict["description_text"])
            self.edit_talent_desc_vals.setText(talent_data_dict["description_values"])
        except Exception as e:
            print(e)
    
    def save_talent_prompt(self):
        try:
            filename = QFileDialog.getSaveFileName(self, "Save Talent JSON", "./talent.json", "*.json")[0]
            f = open(filename,"w+")
            f.write(json.dumps(self.create_talent_data_dict(),indent=4))
            f.close()
        except Exception as e:
            print(e)



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class PickIconScrollView(QScrollArea):

    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setStyleSheet("background: transparent")
        self.grid_data = []
        self.grid_views = []
        width = VALUES.EDIT_TALENT_SIDE_PADDING + VALUES.EDIT_TALENT_NUM_COLS*VALUES.EDIT_TALENT_ICON_SIZE
        height = VALUES.EDIT_TALENT_SIDE_PADDING + VALUES.EDIT_TALENT_NUM_ROWS*VALUES.EDIT_TALENT_ICON_SIZE
        self.setGeometry(parent.width()/2 + VALUES.EDIT_TALENT_SCROLL_X, VALUES.EDIT_TALENT_SCROLL_Y, width, height)
        self.selected_icon = None
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.NoFocus)

        index = 0
        for folder in ["Abilities","Spells"]:
            if folder in os.listdir("./icons"):
                for icon in os.listdir("./icons/{}".format(folder)):
                    path = "./icons/{}/{}".format(folder, icon)
                    row = index // VALUES.EDIT_TALENT_NUM_COLS
                    col = index % VALUES.EDIT_TALENT_NUM_COLS
                    if row == len(self.grid_data):
                        self.grid_data += [[]]
                    self.grid_data[row] += [path]
                    index += 1

        self.num_rows = row
        self.curr_row = 0
        self.last_row_painted = -1
        
        for row in range(VALUES.EDIT_TALENT_NUM_ROWS):
            self.grid_views += [[]]
            for col in range(VALUES.EDIT_TALENT_NUM_COLS):
                talent_icon_view = TalentIconView(self, pick_icon_scroll_view=self)
                talent_icon_view.move(
                    VALUES.EDIT_TALENT_SIDE_PADDING + col*VALUES.EDIT_TALENT_ICON_SIZE, 
                    VALUES.EDIT_TALENT_SIDE_PADDING + row*VALUES.EDIT_TALENT_ICON_SIZE)
                self.grid_views[row] += [talent_icon_view]

    def paintEvent(self, event):
        if self.last_row_painted != self.curr_row:
            self.last_row_painted = self.curr_row
            for row in range(VALUES.EDIT_TALENT_NUM_ROWS):
                if self.curr_row + row < self.num_rows:
                    for col in range(VALUES.EDIT_TALENT_NUM_COLS):
                        if col < len(self.grid_data[self.curr_row + row]):
                            self.grid_views[row][col].set_icon(self.grid_data[self.curr_row + row][col])
                        else:
                            self.grid_views[row][col].set_icon(None)
                else:
                    for col in range(VALUES.EDIT_TALENT_NUM_COLS):
                        self.grid_views[row][col].set_icon(None)
        else:
            for row in range(VALUES.EDIT_TALENT_NUM_ROWS):
                for col in range(VALUES.EDIT_TALENT_NUM_COLS):
                    self.grid_views[row][col].raise_()
        self.raise_()
    
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            if self.curr_row > 0:
                self.curr_row = max(0, self.curr_row - VALUES.EDIT_TALENT_SCROLL_AMOUNT)
        elif event.angleDelta().y() < 0:
            if self.curr_row < self.num_rows - VALUES.EDIT_TALENT_NUM_ROWS:
                self.curr_row = min(self.num_rows - VALUES.EDIT_TALENT_NUM_ROWS, self.curr_row + VALUES.EDIT_TALENT_SCROLL_AMOUNT)
    
    def mousePressEvent(self, event):
        for icon_row in self.grid_views:
            for talent_icon_view in icon_row:
                if event.pos() in talent_icon_view.geometry():
                    RUNTIME.set_curr_pressed(talent_icon_view)
                    return
    
    def mouseMoveEvent(self, event):
        for icon_row in self.grid_views:
            for talent_icon_view in icon_row:
                if event.pos() in talent_icon_view.geometry():
                    RUNTIME.set_curr_hovered(talent_icon_view)
                    return
        RUNTIME.clear_hovered()
    
    def mouseReleaseEvent(self, event):
        for icon_row in self.grid_views:
            for talent_icon_view in icon_row:
                if event.pos() in talent_icon_view.geometry():
                    RUNTIME.clear_pressed()
                    return
        RUNTIME.clear_pressed()



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TalentIconView(QWidget, Hoverable, Pressable):

    def __init__(self, parent, icon_size=None, pick_icon_scroll_view=None):
        super().__init__()
        self.setParent(parent)
        self.pick_icon_scroll_view = pick_icon_scroll_view
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.icon = None
        self.size = icon_size if icon_size != None else VALUES.EDIT_TALENT_ICON_SIZE
        self.scale = self.size/VALUES.TALENT_BORDER_SIZE
        self.setGeometry(0, 0, self.size, self.size)
        self.setMouseTracking(True)
        self.rect_icon = QRect(*(lambda x: ((self.size-x)/2,(self.size-x)/2,x,x))(self.scale*VALUES.TALENT_ICON_SIZE))
        self.rect_border = QRect(*(lambda x: ((self.size-x)/2,(self.size-x)/2,x,x))(self.scale*VALUES.TALENT_BORDER_SIZE))
        self.rect_hover = QRect(*(lambda x: ((self.size-x)/2,(self.size-x)/2,x,x))(self.scale*VALUES.TALENT_HOVER_SIZE))
        self.rect_accent = QRect(*(lambda x: ((self.size-x)/2,(self.size-x)/2,x,x))(self.scale*VALUES.TALENT_ACCENT_SIZE))
        self.pixmap_icon = None

    def paintEvent(self, event):
        if self.icon != None:
            painter = QPainter(self)
            painter.drawPixmap(self.rect_icon, self.pixmap_icon)
            painter.drawPixmap(self.rect_border, PIXMAPS.TALENT_BORDER)
            if self.pick_icon_scroll_view != None and self.pick_icon_scroll_view.selected_icon == self.icon:
                painter.drawPixmap(self.rect_hover, PIXMAPS.TALENT_HOVER_GOLD)
                painter.drawPixmap(self.rect_accent, PIXMAPS.TALENT_ACCENT_GOLD)
            else:
                if self.hovered: 
                    painter.drawPixmap(self.rect_hover, PIXMAPS.TALENT_HOVER_BLUE)
                painter.drawPixmap(self.rect_accent, PIXMAPS.TALENT_ACCENT_GREY)

    def set_icon(self, icon):
        self.icon = icon
        if icon != None:
            self.pixmap_icon = QPixmap(self.icon)
            self.setVisible(True)
        else:
            self.setVisible(False)
        self.raise_()
    
    def set_pressed(self, pressed):
        if self.hovered and self.pressed and not pressed:
            self.pick_icon_scroll_view.selected_icon = self.icon
            self.pick_icon_scroll_view.parent().edit_talent_icon.set_icon(self.icon)
        self.pressed = pressed
        self.update()



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class BackgroundView(QLabel):

    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.pixmap_ref = QPixmap(PATHS.WINDOW_BACKGROUND)

    def update_background(self, ref_view):
        self.setGeometry(ref_view.geometry())
        w = self.width()/2
        h = self.height()/2
        ww = self.pixmap_ref.width()
        hh = self.pixmap_ref.height()
        s = (lambda x: 100/(100+x))(10)
        background_pixmap = QPixmap(self.width(), self.height())
        image = QImage(self.width(), self.height(), 6)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setBackgroundMode(Qt.TransparentMode)
        painter.drawPixmap(QRectF(0,0,w,h), self.pixmap_ref, QRectF(0,0,s*w,s*h))
        painter.drawPixmap(QRectF(w,0,w,h), self.pixmap_ref, QRectF(ww-s*w,0,s*w,s*h))
        painter.drawPixmap(QRectF(0,h,w,h), self.pixmap_ref, QRectF(0,hh-s*h,s*w,s*h))
        painter.drawPixmap(QRectF(w,h,w,h), self.pixmap_ref, QRectF(ww-s*w,hh-s*h,s*w,s*h))
        painter.end()
        background_pixmap.convertFromImage(image)
        self.setPixmap(background_pixmap)
        self.update()



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class ArrowView(QWidget, Hoverable, Pressable):

    def __init__(self, arrow):
        super().__init__()
        self.arrow = arrow
        self.setParent(arrow.tree.view)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover)
        self.src = self.arrow.src.view
        self.dst = self.arrow.dst.view
        self.down = self.dst.talent.row - self.src.talent.row
        self.side = self.dst.talent.col - self.src.talent.col
        W = 20
        H = 20
        
        self.h = None
        self.v = None
        if self.side == 0: #down
            self.v = QRect(
                self.src.x() + (self.src.width() - W)/2,
                self.src.y() + self.src.height() - H,
                W,
                self.dst.y() - self.src.y() - self.src.height() + 2*H)
        elif self.down == 0 and self.side > 0: #right
            self.h = QRect(
                self.src.x() + self.src.width() - W,
                self.src.y() + (self.src.height() - H)/2,
                self.dst.x() - self.src.x() - self.src.width() + 2*W,
                H)
        elif self.side > 0: #right-down
            self.h = QRect(
                self.src.x() + self.src.width() - W,
                self.src.y() + (self.src.height() - H)/2,
                self.dst.x() - self.src.x() - self.src.width()/2 + 1.5*W,
                H)
            self.v = QRect(
                self.dst.x() + self.src.width()/2 - 0.5*W,
                self.src.y() + (self.src.height() - H)/2 + H,
                W,
                self.dst.y() - self.src.y() - self.src.height()/2 + 0.5*H)
        elif self.down == 0 and self.side < 0: #left
            self.h = QRect(
                self.dst.x() + self.dst.width() - W,
                self.src.y() + (self.src.height() - H)/2,
                self.src.x() - self.dst.x() - self.dst.width() + 2*W,
                H)
        elif self.side < 0: #left-down
            self.h = QRect(
                self.dst.x() + self.dst.width()/2 - 0.5*W,
                self.src.y() + (self.src.height() - H)/2,
                self.src.x() - self.dst.x() - self.dst.width()/2 + 1.5*W,
                H)
            self.v = QRect(
                self.dst.x() + self.dst.width()/2 - 0.5*W,
                self.src.y() + (self.src.height() - H)/2 + H,
                W,
                self.dst.y() - self.src.y() - self.src.height()/2 + 0.5*H)
        
        if self.h != None:
            x = self.h.x()
            y = self.h.y()
            w = self.h.width()
            h = self.h.height() + self.v.height() if self.v != None else self.h.height()
        else:
            x = self.v.x()
            y = self.v.y()
            w = self.v.width()
            h = self.v.height()

        self.setGeometry(x,y,w,h)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        if self.side == 0: #down
            pixmap = PIXMAPS.ARROW_DOWN_GOLD if self.satisfied() else PIXMAPS.ARROW_DOWN_GREY
            scale = self.v.width()/pixmap.width()
            pixmap = pixmap.scaled(pixmap.width()*scale, pixmap.height()*scale, transformMode=Qt.SmoothTransformation)
            painter.drawPixmap(QRect(0,0,self.v.width(),self.v.height()), pixmap, QRect(0,pixmap.height()-self.v.height(),self.v.width(),self.v.height()))
            painter.end()
        elif self.down == 0 and self.side > 0: #right
            pixmap = PIXMAPS.ARROW_RIGHT_GOLD if self.satisfied() else PIXMAPS.ARROW_RIGHT_GREY
            scale = self.h.height()/pixmap.height()
            pixmap = pixmap.scaled(pixmap.width()*scale, pixmap.height()*scale, transformMode=Qt.SmoothTransformation)
            painter.drawPixmap(QRect(0,0,self.h.width(),self.h.height()), pixmap, QRect(pixmap.width()-self.h.width(),0,self.h.width(),self.h.height()))
            painter.end()
        elif self.side > 0: #right-down
            pixmap_h = PIXMAPS.ARROW_RIGHT_DOWN_GOLD if self.satisfied() else PIXMAPS.ARROW_RIGHT_DOWN_GREY
            pixmap_v = PIXMAPS.ARROW_DOWN_GOLD if self.satisfied() else PIXMAPS.ARROW_DOWN_GREY
            scale = self.h.height()/pixmap_h.height()
            pixmap_h = pixmap_h.scaled(pixmap_h.width()*scale, pixmap_h.height()*scale, transformMode=Qt.SmoothTransformation)
            pixmap_v = pixmap_v.scaled(pixmap_v.width()*scale, pixmap_v.height()*scale, transformMode=Qt.SmoothTransformation)
            painter.drawPixmap(QRect(0,0,self.h.width(),self.h.height()), pixmap_h, QRect(pixmap_h.width()-self.h.width(),0,self.h.width(),self.h.height()))
            painter.drawPixmap(QRect(self.v.x() - self.h.x(), self.v.y() - self.h.y(),self.v.width(),self.v.height()), pixmap_v, QRect(0,pixmap_v.height()-self.v.height(),self.v.width(),self.v.height()))
            painter.end()
        elif self.down == 0 and self.side < 0: #left
            pixmap = PIXMAPS.ARROW_LEFT_GOLD if self.satisfied() else PIXMAPS.ARROW_LEFT_GREY
            scale = self.h.height()/pixmap.height()
            pixmap = pixmap.scaled(pixmap.width()*scale, pixmap.height()*scale, transformMode=Qt.SmoothTransformation)
            painter.drawPixmap(QRect(0,0,self.h.width(),self.h.height()), pixmap, QRect(0,0,self.h.width(),self.h.height()))
            painter.end()
        elif self.side < 0: #left-down
            pixmap_h = PIXMAPS.ARROW_LEFT_DOWN_GOLD if self.satisfied() else PIXMAPS.ARROW_LEFT_DOWN_GREY
            pixmap_v = PIXMAPS.ARROW_DOWN_GOLD if self.satisfied() else PIXMAPS.ARROW_DOWN_GREY
            scale = self.h.height()/pixmap_h.height()
            pixmap_h = pixmap_h.scaled(pixmap_h.width()*scale, pixmap_h.height()*scale, transformMode=Qt.SmoothTransformation)
            pixmap_v = pixmap_v.scaled(pixmap_v.width()*scale, pixmap_v.height()*scale, transformMode=Qt.SmoothTransformation)
            painter.drawPixmap(QRect(0,0,self.h.width(),self.h.height()), pixmap_h, QRect(0,0,self.h.width(),self.h.height()))
            painter.drawPixmap(QRect(self.v.x() - self.h.x(), self.v.y() - self.h.y(),self.v.width(),self.v.height()), pixmap_v, QRect(0,pixmap_v.height()-self.v.height(),self.v.width(),self.v.height()))
            painter.end()
        else:
            painter.end()
        
    def satisfied(self):
        return self.src.talent.points_spent == self.src.talent.ranks
        
    def mousePressEvent(self, event):
        event_pos = event.pos() + QPoint(self.x(), self.y())
        event_in_v = self.v != None and event_pos in self.v
        event_in_h = self.h != None and event_pos in self.h
        if event_in_v or event_in_h:
            RUNTIME.set_curr_pressed(self)
        else:
            RUNTIME.clear_pressed()
        
    def mouseMoveEvent(self, event):
        RUNTIME.clear_hovered()
        
    def mouseReleaseEvent(self, event):
        self.arrow.remove()
        RUNTIME.clear_pressed()
            

