from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt
import utils.log_utils

log = utils.log_utils.logging_init(__file__)

def gen_led_layout_type_pixmap( led_w, led_h, margin, layout_type):
    '''margin is 20 pixel, left/right/up/bottom is 10 pixel'''
    pixmap_led_layout_type = QPixmap(led_w + margin*2, led_h + margin*2)
    pixmap_led_layout_type.fill(Qt.GlobalColor.white)
    pixmap_paint = QPainter(pixmap_led_layout_type)
    pixmap_paint.setPen(Qt.GlobalColor.red)
    if margin == 0:
        max_line = led_h
    else:
        max_line = int(led_h / margin) + 1
    '''draw line'''
    if layout_type == 0:
        for i in range(max_line):
            pixmap_paint.drawLine(margin, margin*(i+1), led_w + margin , margin*(i+1))
            if i % 2 == 0:
                if i == (max_line - 1):
                    pass
                else:
                    pixmap_paint.drawLine(margin + led_w, margin*(i+1), margin + led_w, margin*(i+2))
            else:
                 pixmap_paint.drawLine(margin, margin*(i+1), margin, margin*(i+2))
    elif layout_type == 1:
        for i in range(max_line):
            pixmap_paint.drawLine(margin, margin*(i+1), led_w + margin , margin*(i+1))
            if i % 2 == 1:
                pixmap_paint.drawLine(margin + led_w, margin*(i+1), margin + led_w, margin*(i+2))
            else:
                if i == (max_line - 1):
                    pass
                else:
                    pixmap_paint.drawLine(margin, margin*(i+1), margin, margin*(i+2))
    return pixmap_led_layout_type

def gen_led_layout_pixmap(led_w, led_h, margin, bg_color, point_color):
    pixmap_led_layout = QPixmap(led_w*2 + margin * 2, led_h*2 + margin * 2)
    #pixmap_led_layout.fill(Qt.GlobalColor.white)
    pixmap_led_layout.fill(bg_color)
    pixmap_paint = QPainter(pixmap_led_layout)
    #pixmap_paint.setPen(Qt.GlobalColor.red)
    pixmap_paint.setPen(point_color)
    for h in range(led_h*2):
        for w in range(led_w*2):
            if w%2 == 1:
                continue
            if h%2 == 1:
                continue
            pixmap_paint.drawPoint(margin + w, margin + h)

    return pixmap_led_layout

def gen_led_cabinet_pixmap(led_w, led_h, margin, bg_color, point_color, alpha, layout_type):
    '''margin is 0 pixel, left/right/up/bottom is 0 pixel'''
    pixmap_led_layout_type = QPixmap(led_w*2 , led_h*2 )
    pixmap_led_layout_type.fill(bg_color)
    pixmap_paint = QPainter(pixmap_led_layout_type)
    pixmap_paint.setPen(point_color)
    if margin == 0:
        max_line = led_h*2
    else:
        max_line = int(led_h*2 / margin) + 1
    '''draw line'''
    if layout_type == 0:
        for i in range(max_line):
            if i % 4 == 0 or i % 4 == 2:
                pixmap_paint.drawLine(margin, margin + i , led_w*2 + margin, margin + i)
            elif i % 4 == 1:
                pixmap_paint.drawLine(margin, margin + (i ), margin, margin + (i + 1))
            elif i % 4 == 3:
                pixmap_paint.drawLine(margin+ led_w*2-1, margin + (i), margin + led_w*2-1, margin + (i + 1))
            
    elif layout_type == 1:
        for i in range(max_line):
            pixmap_paint.drawLine(margin, margin * (i + 1), led_w + margin, margin * (i + 1))
            if i % 2 == 1:
                pixmap_paint.drawLine(margin + led_w, margin * (i + 1), margin + led_w, margin * (i + 2))
            else:
                if i == (max_line - 1):
                    pass
                else:
                    pixmap_paint.drawLine(margin, margin * (i + 1), margin, margin * (i + 2))
    return pixmap_led_layout_type