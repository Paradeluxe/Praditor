def qss_button_checkable_with_color(color="#1991D3"):
    return f"""



        QLabel {{
            background-color: transparent;
            color: black;
            font-weight: bold;
        }}


        QPushButton {{
            background: {color}; 
            color: white;
            font-weight: bold;
            border: 2px solid {color};
            border-radius: 5px;
            margin: 0px
        }}

        QPushButton:pressed {{
            background: #666666;
            color: {color};
            font-weight: bold;
            border: 2px solid {color};
            border-radius: 5px;
            margin: 0px
        }}
        
        QPushButton:checked {{
            background-color: white; 
            color: {color}; 
            border: 2px solid {color};
            font-weight: bold;
            border-radius: 5px;
            margin: 0px
        }}

    """


def qss_slider_with_color(color="#1991D3"):
    return f"""

            /*horizontal ：水平QSlider*/
            QSlider::groove:horizontal {{
                border: 0px solid #bbb;
            }}

            /*1.滑动过的槽设计参数*/
            QSlider::sub-page:horizontal {{
                 /*槽颜色*/
                background: {color};
                 /*外环区域倒圆角度*/
                border-radius: 2px;
                 /*上遮住区域高度*/
                margin-top:5px;
                 /*下遮住区域高度*/
                margin-bottom:5px;
                /*width在这里无效，不写即可*/
            }}

            /*2.未滑动过的槽设计参数*/
            QSlider::add-page:horizontal {{
                /*槽颜色*/
                background: rgb(255,255, 255);
                /*外环大小0px就是不显示，默认也是0*/
                border: 0px solid #777;
                /*外环区域倒圆角度*/
                border-radius: 2px;
                 /*上遮住区域高度*/
                margin-top:7px;
                 /*下遮住区域高度*/
                margin-bottom:7px;
            }}

            /*3.平时滑动的滑块设计参数*/
            QSlider::handle:horizontal {{
                /*滑块颜色*/
                background: #616161;
                /*滑块的宽度*/
                width: 5px;
                /*滑块外环为1px，再加颜色*/
                border: 1px solid #616161;
                 /*滑块外环倒圆角度*/
                border-radius: 2px; 
                 /*上遮住区域高度*/
                margin-top:2px;
                 /*下遮住区域高度*/
                margin-bottom:2px;
            }}

            /*4.手动拉动时显示的滑块设计参数*/
            QSlider::handle:horizontal:hover {{
                /*滑块颜色*/
                background: black;
                /*滑块的宽度*/
                width: 10px;
                /*滑块外环为1px，再加颜色*/
                border: 1px solid black;
                 /*滑块外环倒圆角度*/
                border-radius: 5px; 
                 /*上遮住区域高度*/
                margin-top:0px;
                 /*下遮住区域高度*/
                margin-bottom:0px;
            }}



            """


qss_button_normal = """
        QPushButton {
            background-color: white; 
            color: #7f0020; 
            border: 2px solid #7f0020;
            border-radius: 5px;
            font-weight: bold;
            margin: 0px
        }

        QPushButton:pressed {
            background: #7f0020;
            color: white;
            border: 2px solid #7f0020;
            border-radius: 5px;
            margin: 0px
        }
"""

qss_save_location_button = """
        QPushButton {
            background: transparent; 
            color: gray; 
            font-weight: bold; 
            border: none; 
            border-radius: 0px; 
            padding: 8px 6px; 
            margin: 0px 2px; 
            font-size: 13px; 
        } 
        QPushButton:pressed {
            background: #F0F0F0; 
            color: gray; 
            font-weight: bold; 
            border: none; 
            border-radius: 0px; 
            padding: 8px 6px; 
            margin: 0px 2px; 
        } 
        QPushButton:checked {
            background-color: transparent; 
            color: black; 
            border: none; 
            font-weight: bold; 
            border-radius: 0px; 
            padding: 8px 6px; 
            margin: 0px 2px; 
        }
"""


