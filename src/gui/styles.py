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
            QSlider::groove:horizontal {{ 
                border: 0px solid #bbb;
            }}
            QSlider::sub-page:horizontal {{ 
                background: {color}; 
                border-radius: 2px; 
                margin-top:6px; 
                margin-bottom:6px;
            }}
            QSlider::add-page:horizontal {{ 
                background: rgb(255,255, 255); 
                border: 0px solid #777; 
                border-radius: 2px; 
                margin-top:6px; 
                margin-bottom:6px;
            }}
            QSlider::handle:horizontal {{ 
                background: #616161; 
                width: 5px; 
                border: 1px solid #616161; 
                border-radius: 2px; 
                margin-top:2px; 
                margin-bottom:2px;
            }}
            QSlider::handle:horizontal:hover {{ 
                background: black; 
                width: 10px; 
                border: 1px solid black; 
                border-radius: 2px; 
                margin-top:2px; 
                margin-bottom:2px;
            }}
            """


qss_button_normal = """
        QPushButton {
            background-color: white; 
            color: #333333; 
            border: 2px solid #333333;
            border-radius: 5px;
            font-weight: bold;
            margin: 0px
        }

        QPushButton:pressed {
            background: #333333;
            color: white;
            border: 2px solid #333333;
            border-radius: 5px;
            margin: 0px
        }
"""

qss_save_location_button = """
        /* 基础样式 */
        QPushButton {
            background: transparent; 
            color: gray; 
            font-weight: bold; 
            border: none; 
            border-radius: 0px; 
            padding: 8px 6px; 
            margin: 0px 2px; 
            font-size: 13px; 
            text-decoration: none;
        } 
        
        /* 禁用状态 */
        QPushButton:disabled {
            color: #CCCCCC;
        } 
        
        /* 未选中但文件存在 */
        QPushButton[file_exists="true"] {
            text-decoration: underline;
        } 
        
        /* 未选中但参数匹配 */
        QPushButton[param_matched="true"] {
            color: black;
        }
        
        /* 选中状态 */
        QPushButton:checked {
            border: 2px solid black;
            border-radius: 4px;
            padding: 6px 4px; /* 调整padding，避免文字被边框遮挡 */
        }
        
        /* 选中且文件存在 */
        QPushButton:checked[file_exists="true"] {
            text-decoration: underline;
        }
        
        /* 选中且参数匹配 */
        QPushButton:checked[param_matched="true"] {
            color: black;
        }
        
        /* 按下状态 */
        QPushButton:pressed {
            background: #F0F0F0; 
            color: gray; 
        } 
"""

qss_button_small_black = """
        QPushButton {
            background: white; 
            color: #000000;
            font-weight: bold;
            border: 2px solid #000000;
            border-radius: 5px;
            margin: 0px;
            padding: 4px 8px; /* 减小内边距以适应较小宽度 */
            font-size: 13px;
        }

        /* 禁用状态 */
        QPushButton:disabled {
            background: #F0F0F0;
            color: #CCCCCC;
            border-color: #CCCCCC;
        }

        QPushButton:hover {
            background: #F0F0F0; 
            color: #000000;
            font-weight: bold;
            border: 2px solid #000000;
            border-radius: 5px;
            margin: 0px;
            padding: 4px 8px;
        }

        QPushButton:pressed {
            background: #666666;
            color: white;
            font-weight: bold;
            border: 2px solid #000000;
            border-radius: 5px;
            margin: 0px;
            padding: 4px 8px;
        }
        
        QPushButton:checked {
            background-color: #000000; 
            color: white; 
            border: 2px solid #000000;
            font-weight: bold;
            border-radius: 5px;
            margin: 0px;
            padding: 4px 8px;
        }
        
        QPushButton:checked:disabled {
            background: #F0F0F0;
            color: #CCCCCC;
            border-color: #CCCCCC;
        }
"""


