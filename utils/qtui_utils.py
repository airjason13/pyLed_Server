from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QPoint
import utils.log_utils

from global_def import *

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
    if layout_type == 0 or layout_type == 3:
        for i in range(max_line):
            '''橫線'''
            pixmap_paint.drawLine(margin, margin*(i+1), led_w + margin , margin*(i+1))
            '''直線'''
            if i % 2 == 0:
                if i == (max_line - 1):
                    pass
                else:
                    pixmap_paint.drawLine(margin + led_w, margin*(i+1), margin + led_w, margin*(i+2))
            else:
                 pixmap_paint.drawLine(margin, margin*(i+1), margin, margin*(i+2))
        '''draw arrow'''
        if layout_type == 0:
            pixmap_paint.drawLine(margin, int(margin * (0.5)), int(led_w/8) + margin, margin * (0 + 1))
            pixmap_paint.drawLine(margin, int(margin * (1.5)), int(led_w/8) + margin, margin * (0 + 1))

        elif layout_type == 3:
            pixmap_paint.drawLine(margin + led_w, int(margin*(i+1) - margin*0.5 ), margin + led_w - int(led_w/8), margin*(i+1))
            pixmap_paint.drawLine(margin + led_w, int(margin*(i+1) + margin*0.5 ), margin + led_w - int(led_w/8), margin*(i+1))

    elif layout_type == 2 or layout_type == 1:
        for i in range(max_line):
            '''橫線'''
            pixmap_paint.drawLine(margin, margin*(i+1), led_w + margin , margin*(i+1))
            '''直線'''
            if i % 2 == 1:
                pixmap_paint.drawLine(margin + led_w, margin*(i+1), margin + led_w, margin*(i+2))
            else:
                if i == (max_line - 1):
                    pass
                else:
                    pixmap_paint.drawLine(margin, margin*(i+1), margin, margin*(i+2))
        '''arrow'''
        if layout_type == 2:
            pixmap_paint.drawLine(margin + led_w, int(margin * (0.5)),
                                  margin + led_w - int(led_w / 8), margin * (0 + 1))
            pixmap_paint.drawLine(margin + led_w, int(margin * (1.5)),
                                  margin + led_w - int(led_w / 8), margin * (0 + 1))

        elif layout_type == 1:
            pixmap_paint.drawLine(margin, int(margin*(i+1) - margin*0.5 ),
                                  margin + int(led_w / 8), margin*(i+1))
            pixmap_paint.drawLine(margin , int(margin*(i+1) + margin*0.5),
                                  margin + int(led_w / 8),  margin*(i+1))
    elif layout_type == 4 or layout_type == 5:
        for i in range(max_line):
            '''直線'''
            pixmap_paint.drawLine(margin*(i+1), margin, margin*(i+1), margin + led_h)
            '''橫線'''
            if i % 2 == 1:
                pixmap_paint.drawLine(margin*(i+1) , margin + led_h, margin*(i+2) , margin+ led_h)
            else:
                if i == (max_line - 1):
                    pass
                else:
                    pixmap_paint.drawLine(margin * (i + 1), margin, margin * (i + 2), margin)
        '''arrow'''
        if layout_type == 4:
            pixmap_paint.drawLine(margin*(i+1) - int(margin * (0.5)), margin, margin*(i+1), int(led_h / 8) + margin )
            pixmap_paint.drawLine(margin*(i+1) + int(margin * (0.5)), margin, margin*(i+1), int(led_h / 8) + margin )
        elif layout_type == 5:
            pixmap_paint.drawLine(int(margin * (0.5)), margin + led_h, margin * (0 + 1),  margin + led_h - int(led_h / 8))
            pixmap_paint.drawLine(int(margin * (1.5)), margin + led_h, margin * (0 + 1), margin + led_h - int(led_h / 8))
            pass
    elif layout_type == 6 or layout_type == 7:
        for i in range(max_line):
            '''直線'''
            pixmap_paint.drawLine(margin * (i + 1), margin, margin * (i + 1), margin + led_h)
            '''橫線'''
            if i % 2 == 1:
                pixmap_paint.drawLine(margin * (i + 1), margin, margin * (i + 2), margin)
            else:
                if i == (max_line - 1):
                    pass
                else:
                    pixmap_paint.drawLine(margin * (i + 1), margin + led_h, margin * (i + 2), margin + led_h)
        if layout_type == 6:
            pixmap_paint.drawLine(margin * (i + 1) - int(margin * (0.5)), margin + led_h,
                                  margin * (i + 1), margin + led_h - int(led_h / 8))
            pixmap_paint.drawLine(margin * (i + 1) + int(margin * (0.5)), margin + led_h,
                                  margin * (i + 1), margin + led_h - int(led_h / 8))
            pass
        elif layout_type == 7:
            pixmap_paint.drawLine(int(margin * (0.5)), margin, margin * (0 + 1), int(led_h / 8) + margin)
            pixmap_paint.drawLine(int(margin * (1.5)), margin, margin * (0 + 1), int(led_h / 8) + margin)
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
            pixmap_paint.drawPoint(margin + w, margin + h)  #why add 4???
    log.debug("pixmap_led_layout width : %d", pixmap_led_layout.width())
    log.debug("pixmap_led_layout height : %d", pixmap_led_layout.height())
    return pixmap_led_layout


''' scale factor is 8'''


def gen_led_cabinet_pixmap_with_cabinet_params_test(c_params, margin=0,
                                               bg_color=Qt.GlobalColor.transparent, line_color=Qt.GlobalColor.red,
                                               str_color=Qt.GlobalColor.yellow):
    '''margin is 0 pixel, left/right/up/bottom is 0 pixel'''
    log.debug('')
    scale_factor = 8
    line_interval = scale_factor / 2
    arrow_width = scale_factor / 2
    pixmap_led_layout_type = QPixmap(c_params.cabinet_width * scale_factor, c_params.cabinet_height * scale_factor)
    pixmap_led_layout_type.fill(bg_color)
    pixmap_paint = QPainter(pixmap_led_layout_type)

    pixmap_paint.setPen(line_color)

    str_port_id = str(c_params.client_id) + "-" + str(c_params.port_id)
    if c_params.layout_type < 4:
        if margin == 0:
            max_line = c_params.cabinet_height * scale_factor
        else:
            max_line = int(c_params.cabinet_height * scale_factor / margin) + 1
    else:
        if margin == 0:
            max_line = c_params.cabinet_width * scale_factor
        else:
            max_line = int(c_params.cabinet_width * scale_factor / margin) + 1
    w_drawed = 0
    h_drawed = 0
    #if c_params.layout_type == 0 or c_params.layout_type == 1:
    if c_params.layout_type == 0:
        for i in range(max_line):
            start_point = QPoint(c_params.start_x - 1 , int(c_params.start_y - 1 + line_interval))
            start_point_bak = QPoint(c_params.start_x - 1 , int(c_params.start_y - 1 + line_interval))
            # print(start_point)
            pixel_num = c_params.cabinet_width * c_params.cabinet_height
            reverse = 0
            for p in range(pixel_num -1 ):
                if reverse == 0:
                    if start_point_bak.x() < (c_params.cabinet_width - 1) * scale_factor:
                        next_point = start_point_bak + (scale_factor * QPoint(1, 0))
                    else:
                        next_point = start_point_bak + (scale_factor * QPoint(0, 1))
                        if reverse == 0:
                            reverse = 1
                        else:
                            reverse = 0
                else:
                    if start_point_bak.x() > start_point.x():
                        next_point = start_point_bak - (scale_factor * QPoint(1, 0))
                    else:
                        next_point = start_point_bak + (scale_factor * QPoint(0, 1))
                        if reverse == 1:
                            reverse = 0
                        else:
                            reverse = 1

                pixmap_paint.drawLine(start_point_bak, next_point)
                start_point_bak = next_point
        '''draw arrow'''
        if c_params.layout_type == 0:
            pixmap_paint.drawLine(margin, margin,
                                  margin + int(c_params.cabinet_width / scale_factor), int(margin + line_interval))
            pixmap_paint.drawLine(margin, margin + (2 * line_interval),
                                  margin + int(c_params.cabinet_width / scale_factor), int(margin + line_interval))
        elif c_params.layout_type == 1:
            if c_params.cabinet_height % 2 == 0:
                pixmap_paint.drawLine(margin, int(margin + i - line_interval),
                                      margin + int(c_params.cabinet_width / scale_factor), margin + i)
                pixmap_paint.drawLine(margin, int(margin + i + (line_interval)),
                                      margin + int(c_params.cabinet_width / scale_factor), margin + i)
            elif c_params.cabinet_height % 2 == 1:
                pixmap_paint.drawLine(margin + ((c_params.cabinet_width - 1) * scale_factor),
                                      int(margin + i - line_interval),
                                      margin + ((c_params.cabinet_width - 1) * scale_factor) - int(
                                          c_params.cabinet_width / scale_factor), margin + i)
                pixmap_paint.drawLine(margin + ((c_params.cabinet_width - 1) * scale_factor),
                                      int(margin + i + (line_interval)),
                                      margin + ((c_params.cabinet_width - 1) * scale_factor) - int(
                                          c_params.cabinet_width / scale_factor), margin + i)

    elif c_params.layout_type == 1:

        start_point = scale_factor*QPoint(c_params.start_x - 1 , c_params.start_y - 1 ) + QPoint(0, int(line_interval))
        start_point_bak = scale_factor*QPoint(c_params.start_x - 1 , c_params.start_y - 1 ) + QPoint(0, int(line_interval))

        pixel_num = c_params.cabinet_width * c_params.cabinet_height
        reverse = 1
        for p in range(pixel_num - 1):
            next_point = start_point_bak - (scale_factor*QPoint(1, 0))
            # print(next_point)

            pixmap_paint.drawLine(start_point_bak, next_point)
            start_point_bak = next_point

    '''draw str_port_id'''
    pixmap_paint.setPen(str_color)
    pixmap_paint.drawText(c_params.cabinet_width, c_params.cabinet_height, str_port_id)




    return pixmap_led_layout_type

''' scale factor is 8'''
def gen_led_cabinet_pixmap_with_cabinet_params(c_params, margin=0,
                           bg_color=Qt.GlobalColor.transparent, line_color=Qt.GlobalColor.red, str_color=Qt.GlobalColor.yellow):
    '''margin is 0 pixel, left/right/up/bottom is 0 pixel'''
    # log.debug('')
    scale_factor = 8
    line_interval = scale_factor/2
    arrow_width = scale_factor/2
    pixmap_led_layout_type = QPixmap(c_params.cabinet_width*scale_factor, c_params.cabinet_height*scale_factor)
    pixmap_led_layout_type.fill(bg_color)
    pixmap_paint = QPainter(pixmap_led_layout_type)

    pixmap_paint.setPen(line_color)
    # log.debug("c_params.client_id = %d", c_params.client_id)
    # log.debug("c_params.client_id = %d", c_params.port_id)
    str_port_id = str(c_params.client_id) + "-" + str(c_params.port_id)
    if c_params.layout_type < 4:
        if margin == 0:
            max_line = c_params.cabinet_height*scale_factor
        else:
            max_line = int(c_params.cabinet_height*scale_factor / margin) + 1
    else:
        if margin == 0:
            max_line = c_params.cabinet_width*scale_factor
        else:
            max_line = int(c_params.cabinet_width*scale_factor / margin) + 1
    w_drawed = 0
    h_drawed = 0
    if c_params.layout_type == 0 or c_params.layout_type == 1:
        for i in range( max_line):
            start_point = QPoint(c_params.start_x - 1, c_params.start_y -1)


            '''橫線'''
            if i % (scale_factor) == int(line_interval):
                pixmap_paint.drawLine(margin, margin + i, ((c_params.cabinet_width - 1) * scale_factor )+ margin , margin + i)
                
                h_drawed += 1
            #左邊直線
            elif i % (scale_factor*2) == int(line_interval) + scale_factor + 1:
                #log.debug("left line")
                pixmap_paint.drawLine(margin, margin + (i), margin, margin + (i + (scale_factor)))
            #右邊直線
            elif i % (scale_factor * 2) == int(line_interval) + 1:
                #log.debug("left line")
                pixmap_paint.drawLine(((c_params.cabinet_width - 1) * scale_factor )+ margin, margin + (i), ((c_params.cabinet_width - 1) * scale_factor )+ margin, margin + (i + (scale_factor)))
            if h_drawed >= c_params.cabinet_height:
                break
        '''draw arrow'''
        if c_params.layout_type == 0:
            pixmap_paint.drawLine(margin, margin ,
                                  margin + int(c_params.cabinet_width/scale_factor), int(margin + line_interval))
            pixmap_paint.drawLine(margin, int(margin + (2*line_interval)),
                                  margin + int(c_params.cabinet_width/scale_factor), int(margin + line_interval))
        elif c_params.layout_type == 1:
            if c_params.cabinet_height % 2 == 0:
                pixmap_paint.drawLine(int(margin), int(margin + i - line_interval),
                                      margin + int(c_params.cabinet_width / scale_factor), margin + i )
                pixmap_paint.drawLine(int(margin), int(margin + i + (line_interval)),
                                      margin + int(c_params.cabinet_width / scale_factor), margin + i )
            elif c_params.cabinet_height % 2 == 1:
                pixmap_paint.drawLine(margin + ((c_params.cabinet_width - 1) * scale_factor ) , int(margin + i - line_interval),
                                      margin + ((c_params.cabinet_width - 1) * scale_factor ) - int(c_params.cabinet_width / scale_factor), margin + i)
                pixmap_paint.drawLine(margin + ((c_params.cabinet_width - 1) * scale_factor ) , int(margin + i + (line_interval)),
                                      margin + ((c_params.cabinet_width - 1) * scale_factor ) - int(c_params.cabinet_width / scale_factor), margin + i)
    elif c_params.layout_type == 2 or c_params.layout_type == 3:
        for i in range( max_line):
            '''橫線'''
            if i % (scale_factor) == int(line_interval):
                pixmap_paint.drawLine(margin, margin + i, ((c_params.cabinet_width - 1) * scale_factor )+ margin , margin + i)
                ''' check line number'''
                h_drawed += 1
            #左邊直線
            elif i % (scale_factor*2) == int(line_interval + scale_factor + 1):
                pixmap_paint.drawLine(((c_params.cabinet_width - 1) * scale_factor) + margin, margin + (i),
                                      ((c_params.cabinet_width - 1) * scale_factor) + margin,
                                      margin + (i + (scale_factor)))
            #右邊直線
            elif i % (scale_factor * 2) == int(line_interval + 1):
                pixmap_paint.drawLine(margin, margin + (i), margin, margin + (i + (scale_factor)))

            if h_drawed >= c_params.cabinet_height:
                break
        '''draw arrow'''
        if c_params.layout_type == 2:
            pixmap_paint.drawLine(int(((c_params.cabinet_width - 1) * scale_factor) + margin), int(margin) ,
                                  int((c_params.cabinet_width - 1) * scale_factor) + int(margin) - int(c_params.cabinet_width/scale_factor),
                                  int(margin + line_interval))
            pixmap_paint.drawLine(int(((c_params.cabinet_width - 1) * scale_factor) + margin), int(margin + (2*line_interval)),
                                  int(((c_params.cabinet_width - 1) * scale_factor) + margin - int(c_params.cabinet_width/scale_factor)),
                                  int(margin + line_interval))
        elif c_params.layout_type == 3:
            if c_params.cabinet_height % 2 == 0:
                pixmap_paint.drawLine(int(((c_params.cabinet_width - 1) * scale_factor) + margin), int(margin + i - line_interval),
                                      int(((c_params.cabinet_width - 1) * scale_factor) + margin - int(c_params.cabinet_width / scale_factor)),
                                      int(margin + i))
                pixmap_paint.drawLine(int(((c_params.cabinet_width - 1) * scale_factor) + margin), int(margin + i + (line_interval)),
                                      int(((c_params.cabinet_width - 1) * scale_factor) + margin - int(c_params.cabinet_width / scale_factor)), int(margin + i))
            elif c_params.cabinet_height % 2 == 1:
                pixmap_paint.drawLine( int(margin), int(margin + i - line_interval),
                                      int(margin + int(c_params.cabinet_width / scale_factor)), int(margin + i))
                pixmap_paint.drawLine( int(margin), int(margin + i + (line_interval)),
                                       int(margin + int(c_params.cabinet_width / scale_factor)), int(margin + i))
    elif c_params.layout_type == 4 or c_params.layout_type == 7:
        for i in range(max_line):
            '''直線'''
            if i % (scale_factor) == int(line_interval):
                pixmap_paint.drawLine(margin + i, margin, margin + i,
                                      int(margin + ((c_params.cabinet_height - 1) * scale_factor)))
                ''' check line number'''
                w_drawed += 1
            # 上方直線
            elif i % (scale_factor * 2) == int(line_interval + scale_factor + 1):
                pixmap_paint.drawLine(margin + (i), margin,
                                      int(margin + (i + (scale_factor))), margin)

            # 下方直線
            elif i % (scale_factor * 2) == int(line_interval + 1):
                pixmap_paint.drawLine(margin + (i), int(margin + ((c_params.cabinet_height - 1) * scale_factor)),
                                      int(margin + (i + (scale_factor))),  int(margin + ((c_params.cabinet_height - 1) * scale_factor)))


            if w_drawed >= c_params.cabinet_width:
                break
        '''draw arrow'''
        if c_params.layout_type == 4:
            '''pixmap_paint.drawLine(margin + i - line_interval, margin,
                                  margin + i, margin + int(c_params.cabinet_width / scale_factor))
            pixmap_paint.drawLine(margin + i + line_interval, margin,
                                  margin + i, margin + int(c_params.cabinet_width / scale_factor))'''
            if c_params.cabinet_width % 2 == 0:
                pixmap_paint.drawLine(int(margin + i -line_interval) , margin ,
                                      margin + i , int(margin  + int(c_params.cabinet_width/scale_factor)))
                pixmap_paint.drawLine(int(margin + i + line_interval), margin ,
                                      margin +i , int(margin + int(c_params.cabinet_width / scale_factor)))
            elif c_params.cabinet_width % 2 == 1:
                pixmap_paint.drawLine(int(margin + i - line_interval), margin + int((c_params.cabinet_height - 1) * scale_factor) ,
                                      margin + i , margin + int(((c_params.cabinet_height - 1) * scale_factor) - line_interval ))
                pixmap_paint.drawLine(int(margin + i + line_interval), margin + int((c_params.cabinet_height - 1) * scale_factor),
                                      margin + i , margin + int(((c_params.cabinet_height - 1) * scale_factor) - line_interval))

        elif c_params.layout_type == 7:
            pixmap_paint.drawLine(margin , margin ,
                                  int(margin + line_interval), margin + int(c_params.cabinet_width / scale_factor))
            pixmap_paint.drawLine(int(margin + (2*line_interval)) , margin ,
                                  int(margin + line_interval), margin + int(c_params.cabinet_width / scale_factor))
            pass
    elif c_params.layout_type == 5 or c_params.layout_type == 6:
        for i in range( max_line):
            '''直線'''
            if i % (scale_factor) == int(line_interval):
                pixmap_paint.drawLine(margin + i, margin ,  margin + i, margin + int(((c_params.cabinet_height - 1) * scale_factor )))
                ''' check line number'''
                w_drawed += 1
            #下方直線
            elif i % (scale_factor*2) == int(line_interval + scale_factor + 1):
                pixmap_paint.drawLine( margin + (i), margin + int(((c_params.cabinet_height - 1) * scale_factor)) ,
                                       margin + (i + (scale_factor)), margin + int(((c_params.cabinet_height - 1) * scale_factor)))

            #上方直線
            elif i % (scale_factor * 2) == int(line_interval + 1):
                pixmap_paint.drawLine(margin + (i), margin ,
                                      int(margin + (i + (scale_factor))), margin )


            if w_drawed >= c_params.cabinet_width:
                break
        '''draw arrow'''
        if c_params.layout_type == 5:
            pixmap_paint.drawLine(margin , margin + ((c_params.cabinet_height - 1) * scale_factor),
                                  int(margin + line_interval), margin + ((c_params.cabinet_height - 1) * scale_factor) - int(c_params.cabinet_width/scale_factor))
            pixmap_paint.drawLine(int(margin + (2*line_interval)), margin + ((c_params.cabinet_height - 1) * scale_factor) ,
                                  int(margin + line_interval), margin + ((c_params.cabinet_height - 1) * scale_factor) - int(c_params.cabinet_width / scale_factor))
        elif c_params.layout_type == 6:
            if c_params.cabinet_width % 2 == 1:
                pixmap_paint.drawLine(int(margin + i -line_interval), margin ,
                                      margin + i , margin  + int(c_params.cabinet_width/scale_factor))
                pixmap_paint.drawLine(int(margin + i + line_interval), margin ,
                                      margin +i , margin + int(c_params.cabinet_width / scale_factor))
            elif c_params.cabinet_width % 2 == 0:
                pixmap_paint.drawLine(int(margin + i - line_interval), margin + int(((c_params.cabinet_height - 1) * scale_factor)) ,
                                      margin + i , margin + int(((c_params.cabinet_height - 1) * scale_factor) - line_interval ))
                pixmap_paint.drawLine(int(margin + i + line_interval), margin + int((c_params.cabinet_height - 1) * scale_factor),
                                      margin + i , margin + int(((c_params.cabinet_height - 1) * scale_factor) - line_interval))
    '''draw str_port_id'''
    pixmap_paint.setPen(str_color)
    pixmap_paint.drawText(c_params.cabinet_width, c_params.cabinet_height, str_port_id)




    return pixmap_led_layout_type

''' scale factor is 8'''
def gen_led_cabinet_pixmap_deprecated(c_ip, c_id, c_portid, led_w, led_h, client_id, port_num, margin=0, layout_type=0,
                           bg_color=Qt.GlobalColor.transparent, line_color=Qt.GlobalColor.red, str_color=Qt.GlobalColor.yellow):
    '''margin is 0 pixel, left/right/up/bottom is 0 pixel'''
    log.debug('')
    scale_factor = 8
    line_interval = scale_factor/2
    arrow_width = scale_factor/2
    pixmap_led_layout_type = QPixmap(led_w*scale_factor, led_h*scale_factor)
    pixmap_led_layout_type.fill(bg_color)
    pixmap_paint = QPainter(pixmap_led_layout_type)

    pixmap_paint.setPen(line_color)

    str_port_id = str(c_id) + "-" + str(c_portid)
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