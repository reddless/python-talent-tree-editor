from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from core import *
from buttons import *
import os
import json



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



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
            painter.drawPixmap(rect_border, PIXMAPS.TALENT_BORDER)
            if self.is_hovered: 
                painter.drawPixmap(rect_hover, PIXMAPS.TALENT_HOVER)
            if self.talent.points_spent == self.talent.ranks:
                painter.drawPixmap(rect_accent, PIXMAPS.TALENT_ACCENT_GOLD)
            else:
                painter.drawPixmap(rect_accent, PIXMAPS.TALENT_ACCENT_GREEN)
            painter.drawPixmap(rect_bubble, PIXMAPS.TALENT_BUBBLE)
            self.points_text.setText(self.get_html_points())
            self.points_text.setVisible(True)
        else:
            painter = QPainter(self)
            painter.drawPixmap(rect_icon, QPixmap.fromImage(QImage(QPixmap.toImage(QPixmap(self.talent.icon)).convertToFormat(QImage.Format_Grayscale8))))
            painter.drawPixmap(rect_border, PIXMAPS.TALENT_BORDER)
            if self.is_hovered: 
                painter.drawPixmap(rect_hover, PIXMAPS.TALENT_HOVER)
            painter.drawPixmap(rect_accent, PIXMAPS.TALENT_ACCENT_GREY)
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
        self.talent.talent_view = None
        self.talent = None
    
    def get_html_tooltip(self):
        text = "<font color=\"white\" size=5>{}</font>".format(self.talent.name)
        text += "<br/><font color=\"white\">Rank {}/{}</font>".format(self.talent.points_spent, self.talent.ranks)
        if not self.talent.check_sufficient_earlier_points():
            text += "<br/><font color=\"red\">Requires {} points in {} Talents</font>".format(5*(self.talent.row), self.talent.name)
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
        self.new_talent_view = EditTalentView(self)
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
        
        self.close_is_hovered = False
        self.close_button = CloseButtonView(self, f=lambda: RUNTIME.get_app().quit())
        self.close_button.move(VALUES.CLOSE_MAIN_X, VALUES.CLOSE_MAIN_Y)
        self.close_button.update_pixmap()
        self.last_updated_time = None

    def add_tree_view(self, tree_view):
        index = tree_view.tree.index
        if self.tree_views[index] != None:
            self.tree_views[index].delete()
        self.tree_views[index] = tree_view
        tree_view.setParent(self)
        tree_view.move(VALUES.TREE_X + index*(VALUES.TREE_WIDTH + VALUES.FRAME_INTERTREE_WIDTH), VALUES.TREE_Y)
        self.update_icon(index)
    
    def get_html_points_remaining(self):
        return "<font color=\"gold\">Talent Points: </font><font color=\"white\">{}</font>".format(self.multi_tree.points_remaining)

    def check_event_in_close_area(self, event):
        return (event.x() >= VALUES.CLOSE_MAIN_X) and (event.x() <= VALUES.CLOSE_MAIN_X + VALUES.CLOSE_WIDTH) and (event.y() >= VALUES.CLOSE_MAIN_Y) and (event.y() <= VALUES.CLOSE_MAIN_Y + VALUES.CLOSE_HEIGHT)

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
    
    def update_icon(self, tree_index):
        if self.tree_views[tree_index] != None:
            if self.multi_tree.points_remaining == 0:
                saturation = 1-((51-self.tree_views[tree_index].tree.points_spent)/51)**3
                pixmap = UTILS.get_pixmap_with_saturation(self.tree_views[tree_index].tree.icon, saturation)
                self.tree_icons[tree_index].setPixmap(pixmap.scaledToWidth(self.tree_icons[tree_index].width()))
                self.tree_icons[tree_index].raise_()
                self.update_frame()
            else:
                pixmap = QPixmap(self.tree_views[tree_index].tree.icon)
                self.tree_icons[tree_index].setPixmap(pixmap.scaledToWidth(self.tree_icons[tree_index].width()))
                self.tree_icons[tree_index].raise_()
                self.update_frame()
    
    def update_icons(self):
        for index in range(3):
            self.update_icon(index)
    
    def update_frame(self):
        self.frame.raise_()
        self.close_button.raise_()
        self.update_points()
        self.tooltip_view.background.raise_()
        self.tooltip_view.raise_()
    
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
    
    def show_edit_talent_view(self, talent):
        self.new_talent_view.open_window(talent)



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
                self.background.update_background(self)
            if not self.isVisible():
                self.setVisible(True)
            if not self.background.isVisible():
                self.background.setVisible(True)
        else:
            self.setVisible(False)
            self.background.setVisible(False)
        self.background.raise_()
        self.raise_()
        self.update()
    
    def hide_tooltip(self):
        if self.previous_talent_view != None:
            self.previous_talent_view.is_hovered = False
            self.previous_talent_view.update()
            self.setVisible(False)
            self.background.setVisible(False)
    
    def mouseMoveEvent(self, event):
        self.hide_tooltip()



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



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
        RUNTIME.get_top_view().show_edit_talent_view(self.talent)
    
    def delete(self):
        pass



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
        self.buttons["save"].setGeometry(
            VALUES.EDIT_TALENT_BUTTON_SAVE_X,
            VALUES.EDIT_TALENT_BUTTON_SAVE_Y,
            VALUES.EDIT_TALENT_BUTTON_SAVE_W,
            VALUES.EDIT_TALENT_BUTTON_SAVE_H)
        self.buttons["save"].update_pixmap()

        self.buttons["load"] = LoadButtonView(self, f=lambda: self.load_talent_prompt())
        self.buttons["load"].setGeometry(
            VALUES.EDIT_TALENT_BUTTON_LOAD_X,
            VALUES.EDIT_TALENT_BUTTON_LOAD_Y,
            VALUES.EDIT_TALENT_BUTTON_LOAD_W,
            VALUES.EDIT_TALENT_BUTTON_LOAD_H)
        self.buttons["load"].update_pixmap()

        self.buttons["accept"] = AcceptButtonView(self, f=lambda: self.accept_talent_edit())
        self.buttons["accept"].setGeometry(
            VALUES.EDIT_TALENT_BUTTON_ACCEPT_X,
            VALUES.EDIT_TALENT_BUTTON_ACCEPT_Y,
            VALUES.EDIT_TALENT_BUTTON_ACCEPT_W,
            VALUES.EDIT_TALENT_BUTTON_ACCEPT_H)
        self.buttons["accept"].update_pixmap()

        self.buttons["delete"] = DeleteButtonView(self)
        self.buttons["delete"].setGeometry(
            VALUES.EDIT_TALENT_BUTTON_DELETE_X,
            VALUES.EDIT_TALENT_BUTTON_DELETE_Y,
            VALUES.EDIT_TALENT_BUTTON_DELETE_W,
            VALUES.EDIT_TALENT_BUTTON_DELETE_H)
        self.buttons["delete"].update_pixmap()

        self.buttons["close"] = CloseButtonView(self, f=lambda: self.close_window())
        self.buttons["close"].move(VALUES.EDIT_TALENT_BUTTON_CLOSE_X, VALUES.EDIT_TALENT_BUTTON_CLOSE_Y)
        self.buttons["close"].update_pixmap()

        self.curr_hover = None
        self.curr_pressed = None
    
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
                self.curr_pressed = button_view
                button_view.set_pressed(True)
                break
    
    def mouseMoveEvent(self, event):
        for button_view in self.buttons.values():
            if event.pos() in button_view.geometry():
                if self.curr_hover != button_view:
                    if self.curr_hover != None:
                        self.curr_hover.set_hovered(False)
                    self.curr_hover = button_view
                    self.curr_hover.set_hovered(True)
                return
        if self.curr_hover != None:
            self.curr_hover.set_hovered(False)
            self.curr_hover = None
    
    def mouseReleaseEvent(self, event):
        for button_view in self.buttons.values():
            if event.pos() in button_view.geometry():
                self.curr_pressed = button_view
                button_view.set_pressed(False)
                break
    
    def mouseLeaveEvent(self, event):
        if self.curr_hover != None:
            self.curr_hover.set_hovered(False)
            self.curr_hover = None

    def open_window(self, talent):
        self.modifying_talent = talent
        self.edit_talent_icon.set_icon(PATHS.ICON_QUESTION)
        self.edit_talent_name.clear()
        self.edit_talent_ranks.clear()
        self.edit_talent_desc_text.clear()
        self.edit_talent_desc_vals.clear()
        self.setVisible(True)
        self.edit_talent_name.setFocus()
        self.raise_()
        self.update()

    def close_window(self):
        self.setVisible(False)
    
    def create_talent_data_dict(self):
        name = self.edit_talent_name.toPlainText()
        icon = self.edit_talent_icon.icon
        ranks = self.edit_talent_ranks.text()
        text = self.edit_talent_desc_text.toPlainText()
        vals = self.edit_talent_desc_vals.toPlainText()
        if name == '' or icon == '' or ranks == '' or text == '' or vals == '':
            return ""
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
    
    def accept_talent_edit(self):
        try:
            self.modifying_talent.tree.add_talent(self.modifying_talent.load_from_dict(self.create_talent_data_dict()))
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
                    self.curr_pressed = talent_icon_view
                    return
    
    def mouseMoveEvent(self, event):
        for icon_row in self.grid_views:
            for talent_icon_view in icon_row:
                if event.pos() in talent_icon_view.geometry():
                    if self.parent().curr_hover != talent_icon_view:
                        if self.parent().curr_hover != None:
                            self.parent().curr_hover.set_hovered(False)
                        self.parent().curr_hover = talent_icon_view
                        self.parent().curr_hover.set_hovered(True)
                    return
        if self.parent().curr_hover != None:
            self.parent().curr_hover.set_hovered(False)
            self.parent().curr_hover = None
    
    def mouseReleaseEvent(self, event):
        for icon_row in self.grid_views:
            for talent_icon_view in icon_row:
                if event.pos() in talent_icon_view.geometry():
                    if self.curr_pressed == talent_icon_view:
                        self.selected_icon = self.curr_pressed.icon
                        self.parent().edit_talent_icon.set_icon(self.selected_icon)
                        self.curr_pressed.update()
                        self.curr_pressed = None
                    return



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class TalentIconView(QWidget):

    def __init__(self, parent, icon_size=None, pick_icon_scroll_view=None):
        super().__init__()
        self.setParent(parent)
        self.pick_icon_scroll_view = pick_icon_scroll_view
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.icon = None
        self.size = icon_size if icon_size != None else VALUES.EDIT_TALENT_ICON_SIZE
        self.scale = self.size/VALUES.TALENT_BORDER_SIZE
        self.setGeometry(0, 0, self.size, self.size)
        self.hovered = False
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
                    painter.drawPixmap(self.rect_hover, PIXMAPS.TALENT_HOVER)
                painter.drawPixmap(self.rect_accent, PIXMAPS.TALENT_ACCENT_GREY)

    def set_icon(self, icon):
        self.icon = icon
        if icon != None:
            self.pixmap_icon = QPixmap(self.icon)
            self.setVisible(True)
        else:
            self.setVisible(False)
        self.raise_()

    def set_hovered(self, hovered):
        if self.hovered != hovered:
            self.hovered = hovered
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
