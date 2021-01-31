from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class RUNTIME:
    app = None
    multi_tree = None
    curr_hovered = None
    curr_pressed = None
    in_edit_mode = False
    edit_window_open = False
    last_mouse_move_event = None

    staticmethod
    def set_edit_mode(in_edit_mode):
        RUNTIME.in_edit_mode = in_edit_mode

    staticmethod
    def set_curr_hovered(new_hovered):
        if RUNTIME.curr_hovered != new_hovered:
            RUNTIME.clear_hovered()
        RUNTIME.curr_hovered = new_hovered
        try:
            RUNTIME.curr_hovered.set_hovered(True)
        except:
            pass

    staticmethod
    def clear_hovered():
        if RUNTIME.curr_hovered != None:
            try:
                RUNTIME.curr_hovered.set_hovered(False)
            except:
                pass
            RUNTIME.curr_hovered = None
        RUNTIME.multi_tree.view.tooltip_view.hide_tooltip()

    staticmethod
    def set_curr_pressed(new_pressed):
        if RUNTIME.curr_pressed != new_pressed:
            RUNTIME.clear_pressed()
        RUNTIME.curr_pressed = new_pressed
        try:
            RUNTIME.curr_pressed.set_pressed(True)
        except:
            pass

    staticmethod
    def clear_pressed():
        if RUNTIME.curr_pressed != None:
            try:
                RUNTIME.curr_pressed.set_pressed(False)
            except:
                pass
            RUNTIME.curr_pressed = None

    staticmethod
    def init(scale=1):
        RUNTIME.app = QApplication([])
        VALUES.init(scale=scale)
        PIXMAPS.init()

    staticmethod
    def get_app():
        if RUNTIME.app != None:
            return RUNTIME.app
        else:
            raise Exception("The 'app' reference has not been passed into the RUNTIME")

    staticmethod
    def get_top_view():
        if RUNTIME.multi_tree != None:
            return RUNTIME.multi_tree.view
        else:
            raise Exception("The top 'multi_tree' reference has not been passed into the RUNTIME")

    staticmethod
    def show(multi_tree):
        RUNTIME.multi_tree = multi_tree
        RUNTIME.multi_tree.view.show()
        RUNTIME.app.exec_()



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class UTILS:

    staticmethod
    def get_pixmap_with_saturation(path_to_file, saturation=1):
        image = QImage(QPixmap.toImage(QPixmap(path_to_file)))
        for i in range(image.width()):
            for j in range(image.height()):
                color = image.pixelColor(i, j)
                color.setHsv(color.hue(), saturation * color.saturation(), color.value())
                image.setPixelColor(i, j, color)
        return QPixmap.fromImage(image)



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class PATHS:

    TALENT_FRAME = "./assets/talent-frame.png"
    TALENT_FRAME_MASK = "./assets/talent-frame-mask.png"
    TALENT_BORDER = "./assets/talent-border.png"
    TALENT_HOVER_BLUE = "./assets/talent-hover-blue.png"
    TALENT_HOVER_GOLD = "./assets/talent-hover-gold.png"
    TALENT_BUBBLE_GREY = "./assets/talent-bubble-grey.png"
    TALENT_BUBBLE_GOLD = "./assets/talent-bubble-gold.png"
    TALENT_ACCENT_GREY = "./assets/talent-accent-grey"
    TALENT_ACCENT_GREEN = "./assets/talent-accent-green"
    TALENT_ACCENT_GOLD = "./assets/talent-accent-gold"
    TALENT_ADD_BUTTON_NOHOVER = "./assets/add-talent-nohover.png"
    TALENT_ADD_BUTTON_HOVER = "./assets/add-talent-hover.png"
    CLOSE_HOVER = "./assets/close-hover.png"
    CLOSE_NOHOVER = "./assets/close-nohover.png"
    CLOSE_PRESSED_HOVER = "./assets/close-pressed-hover.png"
    CLOSE_PRESSED_NOHOVER = "./assets/close-pressed-nohover.png"
    WINDOW_BACKGROUND = "./assets/text-box.png"
    ACCEPT_HOVER = "./assets/accept-hover.png"
    ACCEPT_NOHOVER = "./assets/accept-nohover.png"
    ACCEPT_PRESSED_HOVER = "./assets/accept-pressed-hover.png"
    ACCEPT_PRESSED_NOHOVER = "./assets/accept-pressed-nohover.png"
    DELETE_HOVER = "./assets/delete-hover.png"
    DELETE_NOHOVER = "./assets/delete-nohover.png"
    DELETE_PRESSED_HOVER = "./assets/delete-pressed-hover.png"
    DELETE_PRESSED_NOHOVER = "./assets/delete-pressed-nohover.png"
    SAVE_HOVER = "./assets/save-hover.png"
    SAVE_NOHOVER = "./assets/save-nohover.png"
    SAVE_PRESSED_HOVER = "./assets/save-pressed-hover.png"
    SAVE_PRESSED_NOHOVER = "./assets/save-pressed-nohover.png"
    LOAD_HOVER = "./assets/load-hover.png"
    LOAD_NOHOVER = "./assets/load-nohover.png"
    LOAD_PRESSED_HOVER = "./assets/load-pressed-hover.png"
    LOAD_PRESSED_NOHOVER = "./assets/load-pressed-nohover.png"
    EDIT_HOVER = "./assets/edit-hover.png"
    EDIT_NOHOVER = "./assets/edit-nohover.png"
    EDIT_PRESSED_HOVER = "./assets/edit-pressed-hover.png"
    EDIT_PRESSED_NOHOVER = "./assets/edit-pressed-nohover.png"
    EDIT_TALENT_FRAME = "./assets/edit-talent-frame.png"
    ICON_QUESTION = "./icons/items/INV_Misc_QuestionMark.png"
    BACKGROUND_BLANK = "./backgrounds/blank.png"
    ARROW_DOWN_GREY = "./assets/arrows/down-grey.png"
    ARROW_DOWN_GOLD = "./assets/arrows/down-gold.png"
    ARROW_RIGHT_GREY = "./assets/arrows/right-grey.png"
    ARROW_RIGHT_GOLD = "./assets/arrows/right-gold.png"
    ARROW_RIGHT_DOWN_GREY = "./assets/arrows/right-down-grey.png"
    ARROW_RIGHT_DOWN_GOLD = "./assets/arrows/right-down-gold.png"
    ARROW_LEFT_GREY = "./assets/arrows/left-grey.png"
    ARROW_LEFT_GOLD = "./assets/arrows/left-gold.png"
    ARROW_LEFT_DOWN_GREY = "./assets/arrows/left-down-grey.png"
    ARROW_LEFT_DOWN_GOLD = "./assets/arrows/left-down-gold.png"



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class PIXMAPS:

    __init_called__ = False
    __pixmap_cache__ = {}
    __pixmap_cache_greyscale__ = {}

    @staticmethod
    def init(scale=1.0):
        attr_list = [attr for attr in PATHS.__dict__ if not "__" in attr]
        for attr in attr_list:
            exec("PIXMAPS.{} = QPixmap(PATHS.{})".format(attr, attr))
        PIXMAPS.__init_called__ = True
    
    @staticmethod
    def get_pixmap(icon_name, greyscale=False):
        if not icon_name in PIXMAPS.__pixmap_cache__:
            PIXMAPS.__pixmap_cache__[icon_name] = QPixmap(icon_name)
            PIXMAPS.__pixmap_cache_greyscale__[icon_name] = QPixmap.fromImage(QPixmap.toImage(QPixmap(icon_name)).convertToFormat(QImage.Format_Grayscale8))
        if greyscale:
            return PIXMAPS.__pixmap_cache_greyscale__[icon_name]
        else:
            return PIXMAPS.__pixmap_cache__[icon_name]



#############################################################################################################################################
     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###     ###
#############################################################################################################################################



class VALUES:

    __init_called__ = False
    REF_FRAME_WIDTH = 1335
    REF_FRAME_HEIGHT = 805
    REF_FRAME_INTERTREE_WIDTH = 12
    REF_TOOLTIP_WIDTH = 400
    REF_TOOLTIP_FLIPOVER_PADDING = 100
    REF_TOOLTIP_VERTICAL_OFFSET = 130
    REF_TOOLTIP_Y_FLOOR = 120
    REF_MAIN_BUTTON_SAVE_X = 863
    REF_MAIN_BUTTON_SAVE_Y = 773
    REF_MAIN_BUTTON_LOAD_X = 893
    REF_MAIN_BUTTON_LOAD_Y = 773
    REF_MAIN_BUTTON_EDIT_X = 931
    REF_MAIN_BUTTON_EDIT_Y = 773
    REF_MAIN_BUTTON_ACCEPT_X = 931
    REF_MAIN_BUTTON_ACCEPT_Y = 773
    REF_TREE_X = 27
    REF_TREE_Y = 90
    REF_TREE_WIDTH = 421
    REF_TREE_HEIGHT = 670
    REF_TREE_ICON_X = 18
    REF_TREE_ICON_Y = 11
    REF_TREE_ICON_SIZE = 70
    REF_TREE_LABEL_X = 80
    REF_TREE_LABEL_Y = 19
    REF_TREE_LABEL_WIDTH = 296
    REF_TREE_LABEL_HEIGHT = 23
    REF_TREE_POINTS_X = 80
    REF_TREE_POINTS_Y = 66
    REF_TREE_POINTS_WIDTH = 296
    REF_TREE_POINTS_HEIGHT = 17
    REF_TREE_CONTENTS_MARGIN_LEFT = 25
    REF_TREE_CONTENTS_MARGIN_TOP = 0
    REF_TREE_CONTENTS_MARGIN_RIGHT = 35
    REF_TREE_CONTENTS_MARGIN_BOTTOM = 10
    REF_TREE_NAME_FONT_SIZE = 15
    REF_TREE_POINTS_FONT_SIZE = 12
    REF_TALENT_CELL_SIZE = 100
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
    REF_EDIT_TALENT_FRAME_WIDTH = 701
    REF_EDIT_TALENT_FRAME_HEIGHT = 465.5
    REF_EDIT_TALENT_SCROLL_X = 5
    REF_EDIT_TALENT_SCROLL_Y = 72
    REF_EDIT_TALENT_ICON_SIZE = 53.3
    REF_EDIT_TALENT_NUM_ROWS = 6
    REF_EDIT_TALENT_NUM_COLS = 6
    REF_EDIT_TALENT_SCROLL_AMOUNT = 3
    REF_EDIT_TALENT_SIDE_PADDING = 10
    REF_EDIT_TALENT_SELECTED_ICON_X = 25
    REF_EDIT_TALENT_SELECTED_ICON_Y = 70
    REF_EDIT_TALENT_SELECTED_ICON_SIZE = 64
    REF_EDIT_TALENT_TEXTEDIT_NAME_X = 100
    REF_EDIT_TALENT_TEXTEDIT_NAME_Y = 83
    REF_EDIT_TALENT_TEXTEDIT_NAME_W = 253
    REF_EDIT_TALENT_TEXTEDIT_NAME_H = 48
    REF_EDIT_TALENT_TEXTEDIT_RANKS_X = 75
    REF_EDIT_TALENT_TEXTEDIT_RANKS_Y = 116
    REF_EDIT_TALENT_TEXTEDIT_RANKS_W = 20
    REF_EDIT_TALENT_TEXTEDIT_RANKS_H = 20
    REF_EDIT_TALENT_TEXTEDIT_TEXT_X = 28
    REF_EDIT_TALENT_TEXTEDIT_TEXT_Y = 154
    REF_EDIT_TALENT_TEXTEDIT_TEXT_W = 325
    REF_EDIT_TALENT_TEXTEDIT_TEXT_H = 150
    REF_EDIT_TALENT_TEXTEDIT_VALS_X = 28
    REF_EDIT_TALENT_TEXTEDIT_VALS_Y = 329
    REF_EDIT_TALENT_TEXTEDIT_VALS_W = 325
    REF_EDIT_TALENT_TEXTEDIT_VALS_H = 70
    REF_EDIT_TALENT_LABEL_FRAME_X = 280
    REF_EDIT_TALENT_LABEL_FRAME_Y = 12
    REF_EDIT_TALENT_LABEL_FRAME_W = 162
    REF_EDIT_TALENT_LABEL_FRAME_H = 25
    REF_EDIT_TALENT_LABEL_NAME_X = 104
    REF_EDIT_TALENT_LABEL_NAME_Y = 67
    REF_EDIT_TALENT_LABEL_NAME_W = 100
    REF_EDIT_TALENT_LABEL_NAME_H = 20
    REF_EDIT_TALENT_LABEL_TEXT_X = 32
    REF_EDIT_TALENT_LABEL_TEXT_Y = 138
    REF_EDIT_TALENT_LABEL_TEXT_W = 200
    REF_EDIT_TALENT_LABEL_TEXT_H = 20
    REF_EDIT_TALENT_LABEL_VALS_X = 32
    REF_EDIT_TALENT_LABEL_VALS_Y = 313
    REF_EDIT_TALENT_LABEL_VALS_W = 200
    REF_EDIT_TALENT_LABEL_VALS_H = 20
    REF_EDIT_TALENT_LABEL_ICON_X = 370
    REF_EDIT_TALENT_LABEL_ICON_Y = 67
    REF_EDIT_TALENT_LABEL_ICON_W = 100
    REF_EDIT_TALENT_LABEL_ICON_H = 20
    REF_EDIT_TALENT_BUTTON_SAVE_X = 20
    REF_EDIT_TALENT_BUTTON_SAVE_Y = 422
    REF_EDIT_TALENT_BUTTON_LOAD_X = 50
    REF_EDIT_TALENT_BUTTON_LOAD_Y = 422
    REF_EDIT_TALENT_BUTTON_ACCEPT_X = 400
    REF_EDIT_TALENT_BUTTON_ACCEPT_Y = 421
    REF_EDIT_TALENT_BUTTON_DELETE_X = 546
    REF_EDIT_TALENT_BUTTON_DELETE_Y = 421
    REF_EDIT_TALENT_BUTTON_CLOSE_X = 666
    REF_EDIT_TALENT_BUTTON_CLOSE_Y = 26
    REF_CLOSE_MAIN_X = 1295
    REF_CLOSE_MAIN_Y = 17
    REF_CLOSE_WIDTH = 25.5
    REF_CLOSE_HEIGHT = 24
    REF_ACCEPT_WIDTH = 136.8
    REF_ACCEPT_HEIGHT = 25.2
    REF_DELETE_WIDTH = 136.8
    REF_DELETE_HEIGHT = 25.2
    REF_SAVE_WIDTH = 25.5
    REF_SAVE_HEIGHT = 24
    REF_LOAD_WIDTH = 25.5
    REF_LOAD_HEIGHT = 24
    REF_EDIT_WIDTH = 136.8
    REF_EDIT_HEIGHT = 25.2

    @staticmethod
    def init(scale=1.0):
        ref_attr_list = [ref_attr for ref_attr in VALUES.__dict__ if "REF" in ref_attr]
        for ref_attr in ref_attr_list:
            exec("VALUES.{} = VALUES.{}".format(ref_attr[4:], ref_attr))
        VALUES.__init_called__ = True
        if scale != 1.0:
            VALUES.set_scale(scale)
        
    @staticmethod
    def set_scale(scale, q_main_window=None):
        if not VALUES.__init_called__:
            raise Exception("VALUES.init() not called")
        attr_list = [attr for attr in VALUES.__dict__ if (not "__" in attr and not "REF" in attr and not attr in ["set_scale", "init"])]
        for attr in attr_list:
            exec("VALUES.{} = int(round(scale * VALUES.REF_{}))".format(attr, attr))
        if q_main_window != None:
            q_main_window.update()