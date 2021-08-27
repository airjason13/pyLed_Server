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
    scale_factor = 8
    pixmap_led_layout = QPixmap(led_w*scale_factor + margin * 2, led_h*scale_factor + margin * 2)
    #pixmap_led_layout.fill(Qt.GlobalColor.white)
    pixmap_led_layout.fill(bg_color)
    pixmap_paint = QPainter(pixmap_led_layout)
    #pixmap_paint.setPen(Qt.GlobalColor.red)
    pixmap_paint.setPen(point_color)
    for h in range(led_h*scale_factor):
        for w in range(led_w*scale_factor):
            if w%scale_factor != 0:
                continue
            if h%scale_factor != 0:
                continue
            pixmap_paint.drawPoint(margin + w, margin + 4 + h)  #why add 4???
    log.debug("pixmap_led_layout width : %d", pixmap_led_layout.width())
    log.debug("pixmap_led_layout height : %d", pixmap_led_layout.height())
    return pixmap_led_layout

''' scale factor is 8'''
def gen_led_cabinet_pixmap(led_w, led_h, client_id, port_num, margin=0, layout_type=0,
                           bg_color=Qt.GlobalColor.transparent, line_color=Qt.GlobalColor.red, str_color=Qt.GlobalColor.yellow):
    '''margin is 0 pixel, left/right/up/bottom is 0 pixel'''
    scale_factor = 8
    line_interval = scale_factor/2
    arrow_width = scale_factor/2
    pixmap_led_layout_type = QPixmap(led_w*scale_factor, led_h*scale_factor)
    pixmap_led_layout_type.fill(bg_color)
    pixmap_paint = QPainter(pixmap_led_layout_type)
    pixmap_paint.setPen(line_color)
    str_port_id = str(client_id) + "-" + str(port_num)
    if margin == 0:
        max_line = led_h*scale_factor
    else:
        max_line = int(led_h*scale_factor / margin) + 1

    h_drawed = 0
    if layout_type == 0:
        for i in range( max_line):
            '''draw line'''
            if i % (scale_factor) == line_interval:
                pixmap_paint.drawLine(margin, margin + i, ((led_w - 1) * scale_factor )+ margin , margin + i)
                ''' check line number'''
                h_drawed += 1
            elif i % (scale_factor*2) == line_interval + scale_factor + 1:
                #log.debug("left line")
                pixmap_paint.drawLine(margin, margin + (i), margin, margin + (i + (scale_factor)))
            elif i % (scale_factor * 2) == line_interval + 1:
                #log.debug("left line")
                pixmap_paint.drawLine(((led_w - 1) * scale_factor )+ margin, margin + (i), ((led_w - 1) * scale_factor )+ margin, margin + (i + (scale_factor)))
            if h_drawed >= led_h:
                break
        '''draw arrow'''
        #pixmap_paint.drawLine(margin, margin, 2, 2)
        #pixmap_paint.drawLine(margin, 4, 2, 2)

    '''draw str_port_id'''
    pixmap_paint.setPen(str_color)
    pixmap_paint.drawText(led_w, led_h, str_port_id)
    return pixmap_led_layout_type


''' scale factor is 4'''
def gen_led_cabinet_pixmap_tmp(led_w, led_h, client_id, port_num, margin=0, layout_type=0,
                           bg_color=Qt.GlobalColor.transparent, line_color=Qt.GlobalColor.red, str_color=Qt.GlobalColor.yellow):
    '''margin is 0 pixel, left/right/up/bottom is 0 pixel'''
    scale_factor = 4
    arrow_width = 1
    pixmap_led_layout_type = QPixmap(led_w*scale_factor , led_h*scale_factor )
    pixmap_led_layout_type.fill(bg_color)
    pixmap_paint = QPainter(pixmap_led_layout_type)
    pixmap_paint.setPen(line_color)
    str_port_id = str(client_id) + "-" + str(port_num)
    if margin == 0:
        max_line = led_h*scale_factor
    else:
        max_line = int(led_h*4 / margin) + 1


    h_drawed = 0
    if layout_type == 0:
        for i in range( max_line):
            if i < 2:
                continue
            '''draw line'''
            if i % 8 == 2 or i % 8 == 6:
                pixmap_paint.drawLine(margin, margin + i, led_w * 4 + margin, margin + i)
                ''' check line number'''
                h_drawed += 1
                if h_drawed >= led_h:
                    break
            elif i % 8 == 7 : #or i % 8 == 7:
                pixmap_paint.drawLine(margin, margin + (i), margin, margin + (i + 3))
            elif i % 8 == 3: #or i % 8 == 3 or i % 8 == 6:  # or i % 8 == 4:
                pixmap_paint.drawLine(margin + led_w * 4 - 1, margin + (i), margin + led_w * 4 - 1, margin + (i + 3))
        '''draw arrow'''
        pixmap_paint.drawLine(margin, margin, 2, 2)
        pixmap_paint.drawLine(margin, 4, 2, 2)

    '''elif layout_type == 1:
        for i in range(max_line):
            if i % 4 == 0 or i % 4 == 2:
                pixmap_paint.drawLine(margin, margin + i, led_w * 2 + margin, margin + i)
            elif i % 4 == 1:
                pixmap_paint.drawLine(margin + led_w * 2 - 1, margin + (i), margin + led_w * 2 - 1, margin + (i + 1))
            elif i % 4 == 3:
                pixmap_paint.drawLine(margin, margin + (i), margin, margin + (i + 1))'''

    '''draw str_port_id'''
    pixmap_paint.setPen(str_color)
    pixmap_paint.drawText(led_w, led_h, str_port_id)
    return pixmap_led_layout_type