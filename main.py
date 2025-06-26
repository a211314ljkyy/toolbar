import os
import sys
import json
import time
import mathsjson
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QMenu, QSystemTrayIcon, QAction, QTextEdit,
                                QToolBar, QSpinBox, QStyle, QMessageBox, QLineEdit, QColorDialog)
from PyQt5.QtGui import QIcon, QCursor, QFont, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QTimer, QPoint, QDate, QTime, QDateTime

class ToolBar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.opacity = 0.9  # 初始透明度
        self.resize_edge = None
        self.resize_start_x = 0
        self.resize_start_width = 0
        self.button_configs = self.load_button_configs()  # 加载按钮配置
        self.initUI()
        self.load_config()
        self.setup_system_tray()
        self.load_auto_save_content()  # 加载自动保存的内容
        self.setup_text_edit_context_menu()
        
        # 连接文本框的事件
        self.text_input.mousePressEvent = self.text_input_mouse_press_event
        self.text_input.textChanged.connect(self.highlight_links)
        
        # 创建链接格式
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor(0, 0, 255))  # 蓝色
        self.link_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)

    def load_button_configs(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'buttons.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"buttons": []}
        except Exception as e:
            print(f"加载按钮配置失败：{str(e)}")
            return {"buttons": []}

    def handle_button_click(self, button_id):
        try:
            # 查找对应的按钮配置
            button_config = next((btn for btn in self.button_configs.get("buttons", []) if btn["id"] == button_id), None)
            if button_config:
                function_name = button_config.get("function")
                params = button_config.get("params", {})
                
                # 根据配置执行相应的功能
                if function_name == "open_file":
                    self.open_file(params.get("file_path"), params.get("program_path"))
                elif function_name == "run_command":
                    self.run_command(params.get("command"))
                elif function_name == "custom_action":
                    self.execute_custom_action(params.get("action_type"))
        except Exception as e:
            print(f"执行按钮功能失败：{str(e)}")

    def open_file(self, file_path, program_path=None):
        if file_path:
            # 如果是绝对路径，直接使用；否则，将其作为相对路径处理
            if os.path.isabs(file_path):
                abs_path = file_path
            else:
                abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
            
            if os.path.exists(abs_path):
                if program_path and os.path.exists(program_path):
                    # 使用指定程序打开文件
                    os.system(f'"{program_path}" "{abs_path}"')
                else:
                    # 使用系统默认程序打开文件
                    os.startfile(abs_path)
            else:
                print(f"文件不存在：{abs_path}")

    def run_command(self, command):
        if command:
            try:
                # 如果是启动程序的命令，先检查程序是否存在
                if 'start "" "' in command:
                    program_path = command.split('"')[2]
                    if not os.path.exists(program_path):
                        QMessageBox.warning(self, '错误', f'找不到程序：{program_path}\n请检查程序是否已安装或路径是否正确。')
                        return
                    
                    # 检查目标文件是否存在（如果命令中包含目标文件）
                    if len(command.split('"')) > 4:
                        target_file = command.split('"')[4]
                        if not os.path.exists(target_file):
                            QMessageBox.warning(self, '错误', f'找不到文件：{target_file}\n请检查文件是否存在或路径是否正确。')
                            return
                
                os.system(command)
            except Exception as e:
                QMessageBox.warning(self, '错误', f'运行命令失败：{str(e)}\n请检查命令格式是否正确。')

    def execute_custom_action(self, action_type):
        print(f"执行自定义动作：{action_type}")
        # 在这里添加自定义动作的具体实现
        
    def open_config_file(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'buttons.json')
            if os.path.exists(config_path):
                os.startfile(config_path)
        except Exception as e:
            print(f"打开配置文件失败：{str(e)}")

    def load_auto_save_content(self):
        try:
            # 使用绝对路径读取文件
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '自动保存.html')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_input.setHtml(content)
        except Exception as e:
            print(f"读取自动保存.html失败：{str(e)}")
            print(f"尝试读取的文件路径：{file_path}")
        
        # 设置自动保存定时器（每10秒）
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.save_to_auto_save_file)
        self.auto_save_timer.start(10000)  # 10000毫秒 = 10秒
        
        # 设置每日16:00保存定时器
        self.setup_daily_save_timer()

    def initUI(self):
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建主widget和布局
        self.central_widget = QWidget()
        
        # 启用鼠标追踪
        self.setMouseTracking(True)
        self.central_widget.setMouseTracking(True)
        self.setCentralWidget(self.central_widget)
        
        # 为所有主要部件启用鼠标追踪
        self.text_input = QTextEdit()
        self.text_input.setMouseTracking(True)
        self.text_input.setStyleSheet("QTextEdit { color: black; selection-color: white; selection-background-color: #0078d7; caret-color: black; }")
        
        # 连接文本变化信号
        self.text_input.textChanged.connect(self.highlight_links)
        
        self.search_input = QLineEdit()
        self.search_input.setMouseTracking(True)
        self.search_input.setStyleSheet("QLineEdit { color: black; selection-color: white; selection-background-color: #0078d7; caret-color: black; }")
        
        # 设置主窗口背景和样式
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(240, 240, 240, 0.9);
                border: 1px solid rgba(200, 200, 200, 0.8);
                border-radius: 5px;
            }
        """)
        
        # 创建主布局（水平布局）
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # 创建左侧小按钮的垂直布局
        left_buttons_layout = QVBoxLayout()
        left_buttons_layout.setSpacing(1)  # 设置按钮间距为1像素
        
        # 创建20个15*15的小按钮
        self.small_buttons = []
        for i in range(20):
            button_config = next((btn for btn in self.button_configs.get("buttons", []) if btn["id"] == i + 1), None)
            btn = QPushButton(button_config["name"] if button_config else str(i + 1))
            btn.setFixedSize(15, 15)
            btn.setMouseTracking(True)
            # 设置按钮提示文本
            if button_config:
                btn.setToolTip(f"{button_config['name']}\n{button_config['function']}")
            # 连接点击事件
            btn.clicked.connect(lambda checked, bid=i+1: self.handleButtonClick(bid))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.8);
                    border: 1px solid rgba(200, 200, 200, 0.8);
                    border-radius: 2px;
                    font-size: 8px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(230, 230, 230, 0.9);
                }
                QPushButton:pressed {
                    background-color: rgba(210, 210, 210, 0.9);
                }
            """)
            left_buttons_layout.addWidget(btn)
            self.small_buttons.append(btn)
        
        # 添加左侧按钮布局到主布局
        main_layout.addLayout(left_buttons_layout)
        
        # 创建右侧内容的垂直布局
        right_content_layout = QVBoxLayout()
        right_content_layout.setSpacing(4)
        
        # 创建关闭按钮和添加按钮的水平布局
        control_layout = QHBoxLayout()
        control_layout.setSpacing(1)
        
        # 创建关闭按钮
        self.close_button = QPushButton("x")
        self.close_button.setFixedSize(10, 10)
        self.close_button.setMouseTracking(True)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(200, 200, 200, 0.8);
                border-radius: 2px;
                font-size: 8px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(230, 230, 230, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(210, 210, 210, 0.9);
            }
        """)
        self.close_button.clicked.connect(self.hide)
        

        
        # 创建日月按钮和帮助按钮
        self.sun_button = QPushButton("日")
        self.moon_button = QPushButton("月")
        self.open_button = QPushButton("开")
        self.edit_config_button = QPushButton("m")
        self.help_button = QPushButton("H")
        self.sun_button.setFixedSize(15, 15)
        self.moon_button.setFixedSize(15, 15)
        self.open_button.setFixedSize(15, 15)
        self.edit_config_button.setFixedSize(15, 15)
        self.help_button.setFixedSize(15, 15)
        
        # 设置编辑配置按钮的提示文本和点击事件
        self.edit_config_button.setToolTip("编辑按钮配置文件")
        self.edit_config_button.clicked.connect(self.open_config_file)
        
        # 设置日月按钮和帮助按钮样式
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(200, 200, 200, 0.8);
                border-radius: 3px;
                font-size: 11px;
                padding: 1px;
                color: #333333;
                font-weight: normal;
                transition: all 0.2s;
            }
            QPushButton:hover {
                background-color: rgba(240, 240, 240, 0.95);
                border-color: rgba(180, 180, 180, 0.9);
                color: #000000;
            }
            QPushButton:pressed {
                background-color: rgba(220, 220, 220, 0.95);
                border-color: rgba(160, 160, 160, 0.9);
                padding: 2px 1px 0px 1px;
            }
            QPushButton:focus {
                border-color: rgba(100, 150, 255, 0.8);
                outline: none;
            }
        """
        self.sun_button.setStyleSheet(button_style)
        self.moon_button.setStyleSheet(button_style)
        self.open_button.setStyleSheet(button_style)
        self.help_button.setStyleSheet(button_style)
        
        # 连接开按钮的点击事件
        self.open_button.clicked.connect(self.open_save_files)

        
        # 连接按钮的点击事件
        self.sun_button.clicked.connect(self.increase_opacity)
        self.moon_button.clicked.connect(self.decrease_opacity)
        self.help_button.clicked.connect(self.open_readme)

        
        # 添加按钮到控制布局
        control_layout.addWidget(self.sun_button)
        control_layout.addWidget(self.moon_button)
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.edit_config_button)
        control_layout.addWidget(self.help_button)
        control_layout.addStretch()
        control_layout.addWidget(self.close_button)
        
        # 创建文本输入框
        self.text_input = QTextEdit()
        self.text_input.setAcceptRichText(True)  # 启用富文本支持
        self.text_input.setMinimumWidth(30)  # 设置最小宽度
        self.resize(300, 400)  # 设置窗口初始大小
        self.text_input.setMouseTracking(True)
        
        # 创建格式工具栏
        self.format_toolbar = QWidget()
        format_layout = QHBoxLayout(self.format_toolbar)
        format_layout.setSpacing(2)  # 设置按钮间距为2像素
        format_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局边距为0

        # 创建富文本编辑功能按钮
        # 加粗按钮
        bold_button = QPushButton('B')
        bold_button.setFixedSize(20, 20)
        bold_style = button_style + """
            QPushButton {
                font-weight: bold;
                font-family: Times New Roman;
            }
        """
        bold_button.setStyleSheet(bold_style)
        bold_button.clicked.connect(self.toggle_bold)
        bold_button.setToolTip('加粗文字 (Ctrl+B)')

        # 斜体按钮
        italic_button = QPushButton('I')
        italic_button.setFixedSize(20, 20)
        italic_style = button_style + """
            QPushButton {
                font-style: italic;
                font-family: Times New Roman;
            }
        """
        italic_button.setStyleSheet(italic_style)
        italic_button.clicked.connect(self.toggle_italic)
        italic_button.setToolTip('斜体文字 (Ctrl+I)')

        # 下划线按钮
        underline_button = QPushButton('U')
        underline_button.setFixedSize(20, 20)
        underline_style = button_style + """
            QPushButton {
                text-decoration: underline;
                font-family: Times New Roman;
            }
        """
        underline_button.setStyleSheet(underline_style)
        underline_button.clicked.connect(self.toggle_underline)
        underline_button.setToolTip('下划线文字 (Ctrl+U)')

        # 字体按钮
        font_button = QPushButton('字')
        font_button.setFixedSize(20, 20)
        font_style = button_style + """
            QPushButton {
                font-family: Microsoft YaHei;
                font-weight: bold;
            }
        """
        font_button.setStyleSheet(font_style)
        font_button.clicked.connect(self.show_font_dialog)
        font_button.setToolTip('选择字体样式')

        color_button = QPushButton('A')
        color_button.setFixedSize(20, 20)
        # 为颜色按钮设置特殊样式，添加红色文字颜色
        color_button_style = button_style + """
            QPushButton {
                color: #FF4444;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FF0000;
            }
        """
        color_button.setStyleSheet(color_button_style)
        color_button.clicked.connect(self.show_color_dialog)
        color_button.setToolTip('设置文字颜色 (点击打开颜色选择器)')

        # 将按钮添加到格式工具栏布局中
        format_layout.addWidget(bold_button)
        format_layout.addWidget(italic_button)
        format_layout.addWidget(underline_button)
        format_layout.addWidget(font_button)
        format_layout.addWidget(color_button)

        # 将控制布局添加到右侧内容布局
        right_content_layout.addLayout(control_layout)
        
        # 添加格式工具栏到右侧内容布局
        right_content_layout.addWidget(self.format_toolbar)
        
        # 添加文本输入框到右侧内容布局
        right_content_layout.addWidget(self.text_input)
        
        # 创建底部搜索布局
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(4)
        
        # 创建搜索框
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(20)  # 设置固定高度
        self.search_input.setPlaceholderText('搜索...')
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.8);
                border: none;
                border-radius: 5px;
                padding: 2px 5px;
            }
        """)
        bottom_layout.addWidget(self.search_input)
        
        # 创建按钮
        text_button = QPushButton('文本')
        text_button.setFixedSize(28, 20)
        text_button.clicked.connect(self.search_in_text)
        
        next_button = QPushButton('向下')
        next_button.setFixedSize(28, 20)
        next_button.clicked.connect(self.search_next)
        
        google_button = QPushButton('google')
        google_button.setFixedSize(28, 20)
        google_button.clicked.connect(self.search_in_google)
        
        filter_button = QPushButton('筛选')
        filter_button.setFixedSize(28, 20)
        filter_button.clicked.connect(self.filter_content)
        
        bottom_layout.addWidget(text_button)
        bottom_layout.addWidget(next_button)
        bottom_layout.addWidget(google_button)
        bottom_layout.addWidget(filter_button)
        
        # 添加底部布局到右侧内容布局
        right_content_layout.addLayout(bottom_layout)
        
        # 将右侧内容布局添加到主布局
        main_layout.addLayout(right_content_layout)
        
        # 初始化时不设置背景色，由update_opacity控制
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid rgba(200, 200, 200, 0.8);
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
            }
        """)
        # 设置文本框高度
        self.text_input.setFixedHeight(400)  # 设置固定高度

        # 创建拖动按钮
        self.drag_button = QPushButton(self.text_input)
        self.drag_button.setFixedSize(25, 25)
        self.drag_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 200, 200, 0.3);
                border: 1px solid rgba(200, 200, 200, 0.5);
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 0.5);
            }
        """)
        # 设置拖动按钮的位置
        self.drag_button.move(self.text_input.width() - 25, self.text_input.height() - 25)
        # 绑定拖动按钮的鼠标事件
        self.drag_button.mousePressEvent = self.drag_button_mouse_press_event
        self.drag_button.mouseMoveEvent = self.drag_button_mouse_move_event

    def setup_text_edit_context_menu(self):
        self.text_input.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_input.customContextMenuRequested.connect(self.show_text_edit_context_menu)
    
    def show_text_edit_context_menu(self, position):
        menu = QMenu()
        
        # 添加文本格式化菜单
        format_menu = QMenu('格式', self)
        
        # 字体菜单
        font_action = format_menu.addAction('字体')
        font_action.triggered.connect(self.show_font_dialog)
        
        # 字号子菜单
        size_menu = format_menu.addMenu('字号')
        for size in [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]:
            action = size_menu.addAction(str(size))
            action.triggered.connect(lambda checked, s=size: self.text_input.setFontPointSize(s))
        
        # 样式菜单
        style_menu = format_menu.addMenu('样式')
        bold_action = style_menu.addAction('粗体')
        bold_action.triggered.connect(self.toggle_bold)
        italic_action = style_menu.addAction('斜体')
        italic_action.triggered.connect(self.toggle_italic)
        underline_action = style_menu.addAction('下划线')
        underline_action.triggered.connect(self.toggle_underline)
        
        # 对齐方式菜单
        align_menu = format_menu.addMenu('对齐')
        left_align = align_menu.addAction('左对齐')
        left_align.triggered.connect(lambda: self.text_input.setAlignment(Qt.AlignLeft))
        center_align = align_menu.addAction('居中')
        center_align.triggered.connect(lambda: self.text_input.setAlignment(Qt.AlignCenter))
        right_align = align_menu.addAction('右对齐')
        right_align.triggered.connect(lambda: self.text_input.setAlignment(Qt.AlignRight))
        
        # 添加颜色菜单
        color_menu = format_menu.addMenu('颜色')
        text_color = color_menu.addAction('文字颜色')
        text_color.triggered.connect(self.show_color_dialog)
        
        # 添加格式菜单到主菜单
        menu.addMenu(format_menu)
        
        # 添加编辑菜单项
        menu.addSeparator()
        menu.addAction('剪切', self.text_input.cut)
        menu.addAction('复制', self.text_input.copy)
        menu.addAction('粘贴', self.text_input.paste)
        menu.addSeparator()
        menu.addAction('全选', self.text_input.selectAll)
        
        # 显示菜单
        menu.exec_(self.text_input.mapToGlobal(position))
    
    def show_font_dialog(self):
        from PyQt5.QtWidgets import QFontDialog
        font, ok = QFontDialog.getFont(self.text_input.currentFont(), self)
        if ok:
            self.text_input.setCurrentFont(font)
    
    def toggle_underline(self):
        cursor = self.text_input.textCursor()
        if not cursor.hasSelection():
            return
        
        # 保存当前选中的文本及其格式
        text = cursor.selectedText()
        char_format = cursor.charFormat()
        
        # 切换下划线状态
        char_format.setFontUnderline(not char_format.fontUnderline())
        
        # 删除原文本并插入带有新格式的文本
        cursor.removeSelectedText()
        cursor.insertText(text, char_format)
        
        # 重新选中文本
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(text))
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(text))
        self.text_input.setTextCursor(cursor)

    def toggle_italic(self):
        cursor = self.text_input.textCursor()
        if not cursor.hasSelection():
            return
        
        # 保存当前选中的文本及其格式
        text = cursor.selectedText()
        char_format = cursor.charFormat()
        
        # 切换斜体状态
        char_format.setFontItalic(not char_format.fontItalic())

    def show_color_dialog(self):
        from PyQt5.QtWidgets import QColorDialog
        color = QColorDialog.getColor(initial=self.text_input.textColor(), parent=self)
        if color.isValid():
            cursor = self.text_input.textCursor()
            if cursor.hasSelection():
                # 保存当前选中的文本及其格式
                text = cursor.selectedText()
                char_format = cursor.charFormat()
                
                # 设置新的文字颜色
                char_format.setForeground(color)
                
                # 删除原文本并插入带有新格式的文本
                cursor.removeSelectedText()
                cursor.insertText(text, char_format)
                
                # 重新选中文本
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(text))
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(text))
                self.text_input.setTextCursor(cursor)
            else:
                # 如果没有选中文本，设置当前光标位置的文字颜色
                char_format = cursor.charFormat()
                char_format.setForeground(color)
                cursor.mergeCharFormat(char_format)
        
        # 删除原文本并插入带有新格式的文本
        cursor.removeSelectedText()
        cursor.insertText(text, char_format)
        
        # 重新选中文本
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(text))
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(text))
        self.text_input.setTextCursor(cursor)

    def toggle_bold(self):
        cursor = self.text_input.textCursor()
        if not cursor.hasSelection():
            return
        
        # 保存当前选中的文本及其格式
        text = cursor.selectedText()
        char_format = cursor.charFormat()
        
        # 切换粗体状态
        current_weight = char_format.fontWeight()
        new_weight = QFont.Normal if current_weight == QFont.Bold else QFont.Bold
        char_format.setFontWeight(new_weight)
        
        # 删除原文本并插入带有新格式的文本
        cursor.removeSelectedText()
        cursor.insertText(text, char_format)
        
        # 重新选中文本
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(text))
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(text))
        self.text_input.setTextCursor(cursor)

    def search_in_text(self):
        search_text = self.search_input.text()
        if not search_text:
            return
        
        # 获取文本编辑器的内容
        cursor = self.text_input.textCursor()
        
        # 从头开始查找
        cursor.movePosition(QTextCursor.Start)
        self.text_input.setTextCursor(cursor)
        
        # 设置查找格式（蓝色背景）
        format = QTextCharFormat()
        format.setBackground(QColor(173, 216, 230))  # 浅蓝色
        
        # 查找文本并高亮
        found = self.text_input.find(search_text)
        if found:
            # 获取当前选中的文本的格式
            cursor = self.text_input.textCursor()
            cursor.mergeCharFormat(format)
        else:
            QMessageBox.information(self, '查找结果', '没有匹配内容')
    
    def search_next(self):
        search_text = self.search_input.text()
        if not search_text:
            return
        
        # 设置查找格式（蓝色背景）
        format = QTextCharFormat()
        format.setBackground(QColor(173, 216, 230))  # 浅蓝色
        
        # 从当前位置继续查找
        found = self.text_input.find(search_text)
        if found:
            # 获取当前选中的文本的格式
            cursor = self.text_input.textCursor()
            cursor.mergeCharFormat(format)
        else:
            # 如果没找到，从头开始查找
            cursor = self.text_input.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.text_input.setTextCursor(cursor)
            found = self.text_input.find(search_text)
            if found:
                cursor = self.text_input.textCursor()
                cursor.mergeCharFormat(format)
            else:
                QMessageBox.information(self, '查找结果', '没有匹配内容')

    def search_in_google(self):
        search_text = self.search_input.text()
        if not search_text:
            return
        
        # 构建Google搜索URL
        google_url = f"https://www.google.com/search?q={search_text}"
        
        # 使用默认浏览器打开URL
        import webbrowser
        webbrowser.open(google_url)

    def filter_content(self):
        search_text = self.search_input.text()
        if not search_text:
            return
        
        # 获取文本编辑器的内容
        document = self.text_input.document()
        text = document.toPlainText()
        
        # 筛选包含搜索文本的行
        filtered_lines = [line for line in text.split('\n') if search_text in line]
        
        # 创建新窗口显示筛选结果
        self.filter_window = QMainWindow(self)
        self.filter_window.setWindowTitle('筛选结果')
        self.filter_window.resize(400, 300)
        
        # 创建文本编辑器显示筛选结果
        result_text = QTextEdit()
        result_text.setPlainText('\n'.join(filtered_lines))
        result_text.setReadOnly(True)
        
        self.filter_window.setCentralWidget(result_text)
        self.filter_window.show()
    
    def show_color_dialog(self):
        try:
            color = QColorDialog.getColor(initial=self.text_input.textColor(), parent=self)
            if color.isValid():
                cursor = self.text_input.textCursor()
                char_format = cursor.charFormat()
                char_format.setForeground(color)
                
                if cursor.hasSelection():
                    # 如果有选中的文本，应用颜色到选中文本
                    cursor.mergeCharFormat(char_format)
                else:
                    # 如果没有选中文本，应用颜色到当前光标位置
                    self.text_input.mergeCurrentCharFormat(char_format)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"设置颜色时出错: {str(e)}")
            print(f"设置颜色时出错: {str(e)}")

    def open_save_files(self):
        try:
            # 尝试打开今日任务.html
            today_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '今日任务.html')
            if os.path.exists(today_file):
                os.startfile(today_file)

            # 尝试打开自动保存.html
            auto_save_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '自动保存.html')
            if os.path.exists(auto_save_file):
                os.startfile(auto_save_file)
        except Exception as e:
            print(f"打开文件失败：{str(e)}")

    def open_readme(self):
        try:
            readme_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
            if os.path.exists(readme_file):
                os.startfile(readme_file)
        except Exception as e:
            print(f"打开README.md失败：{str(e)}")

    def load_config(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                    # 这里可以添加配置文件的解析逻辑
                    print("配置文件加载成功")
        except Exception as e:
            print(f"加载配置文件失败：{str(e)}")

    def setup_system_tray(self):
        try:
            # 创建系统托盘图标
            self.tray_icon = QSystemTrayIcon(self)
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'tray_icon.svg')
            if os.path.exists(icon_path):
                self.tray_icon.setIcon(QIcon(icon_path))
            else:
                # 如果找不到自定义图标，使用默认图标
                self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

            # 创建托盘菜单
            tray_menu = QMenu()
            show_action = QAction('显示', self)
            quit_action = QAction('退出', self)
            show_action.triggered.connect(self.show)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(show_action)
            tray_menu.addAction(quit_action)

            # 设置托盘图标的菜单
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
        except Exception as e:
            print(f"设置系统托盘失败：{str(e)}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 获取窗口边框区域
            rect = self.geometry()
            self.resize_edge = None
            
            # 检测鼠标是否在窗口边缘（设置5像素的判定区域）
            if event.x() <= 5:  # 左边缘
                self.resize_edge = 'left'
            elif event.x() >= rect.width() - 5:  # 右边缘
                self.resize_edge = 'right'
            
            if self.resize_edge:
                self.resize_start_x = event.globalX()
                self.resize_start_width = rect.width()
            else:
                # 如果不是调整大小，那就是拖动窗口
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.resize_edge:
                # 计算宽度变化
                delta = event.globalX() - self.resize_start_x
                if self.resize_edge == 'left':
                    new_width = max(30, self.resize_start_width - delta)  # 确保最小宽度为30
                    self.setGeometry(event.globalX(), self.y(), new_width, self.height())
                elif self.resize_edge == 'right':
                    new_width = max(30, self.resize_start_width + delta)  # 确保最小宽度为30
                    self.resize(new_width, self.height())
            else:
                # 移动窗口
                self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            # 当鼠标移动但没有按下按钮时，检查是否在边缘并更新鼠标样式
            if event.x() <= 5 or event.x() >= self.width() - 5:
                if self.cursor().shape() != Qt.SizeHorCursor:
                    self.setCursor(Qt.SizeHorCursor)
            else:
                if self.cursor().shape() != Qt.ArrowCursor:
                    self.setCursor(Qt.ArrowCursor)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.resize_edge = None
            self.unsetCursor()
            event.accept()
            
    def highlight_links(self):
        # 保存当前光标位置
        cursor = self.text_input.textCursor()
        current_position = cursor.position()
        
        # 重置所有文本格式
        cursor.select(QTextCursor.Document)
        default_format = QTextCharFormat()
        cursor.setCharFormat(default_format)
        
        # 获取全部文本
        text = self.text_input.toPlainText()
        words = text.split()
        
        # 遍历每个单词检查是否是链接
        for word in words:
            if word.startswith(('http://', 'https://', 'www.')) or os.path.exists(word):
                # 查找单词位置并应用格式
                cursor = self.text_input.document().find(word)
                while not cursor.isNull():
                    cursor.mergeCharFormat(self.link_format)
                    cursor = self.text_input.document().find(word, cursor)
        
        # 恢复光标位置
        cursor = self.text_input.textCursor()
        cursor.setPosition(current_position)
        self.text_input.setTextCursor(cursor)
    
    def text_input_mouse_press_event(self, event):
        cursor = self.text_input.cursorForPosition(event.pos())
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText().strip()
        
        # 检查是否是链接
        if word.startswith(('http://', 'https://', 'www.')):
            if word.startswith('www.'):
                word = 'http://' + word
            os.startfile(word)
        elif os.path.exists(word):
            os.startfile(word)
        else:
            QTextEdit.mousePressEvent(self.text_input, event)
            
    def drag_button_mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            # 记录按钮按下时的全局位置和窗口位置的差值
            self.drag_position = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()
            
    def drag_button_mouse_move_event(self, event):
        if event.buttons() == Qt.LeftButton:
            # 移动窗口到新位置
            self.window().move(event.globalPos() - self.drag_position)
            event.accept()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 更新关闭按钮位置
        self.close_button.move(self.width() - 14, 4)
        
    def increase_opacity(self):
        self.opacity = min(1.0, self.opacity + 0.1)
        self.update_opacity()
        
    def decrease_opacity(self):
        self.opacity = max(0.1, self.opacity - 0.1)
        self.update_opacity()
        
    def update_opacity(self):
        self.central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(240, 240, 240, {self.opacity});
                border: 1px solid rgba(200, 200, 200, 0.8);
                border-radius: 5px;
            }}
            QTextEdit {{
                background-color: rgba(240, 240, 240, {self.opacity});
                border: 1px solid rgba(200, 200, 200, 0.8);
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
            }}
        """)

    def save_to_auto_save_file(self):
        # 获取文本框内容
        content = self.text_input.toHtml()
        if content:
            try:
                # 使用绝对路径覆盖写入文件
                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '自动保存.html')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                print(f"保存到自动保存.html失败：{str(e)}")
                print(f"尝试保存的文件路径：{file_path}")

    def setup_daily_save_timer(self):
        # 计算距离下一个16:00的毫秒数
        current_time = QTime.currentTime()
        target_time = QTime(16, 0)  # 16:00
        
        if current_time >= target_time:
            # 如果当前时间已过16:00，设置为明天的16:00
            msec_to_target = (24 * 60 - (current_time.hour() * 60 + current_time.minute()) + 16 * 60) * 60 * 1000
        else:
            # 如果当前时间未到16:00，设置为今天的16:00
            msec_to_target = ((16 * 60) - (current_time.hour() * 60 + current_time.minute())) * 60 * 1000
        
        # 使用singleShot设置一次性定时器
        QTimer.singleShot(msec_to_target, self.save_to_today_file)
    
    def save_to_today_file(self):
        # 获取文本框内容
        content = self.text_input.toHtml()
        if content:
            # 获取当前日期和时间
            current_datetime = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
            # 准备要保存的内容
            save_content = f"\n=== {current_datetime} ===\n{content}"
            
            try:
                # 使用绝对路径覆盖写入内容到文件
                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '今日任务.html')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(save_content)
            except Exception as e:
                print(f"保存到今日任务.html失败：{str(e)}")
                print(f"尝试保存的文件路径：{file_path}")
        
        # 保存完成后，设置下一个16:00的定时器
        self.setupDailySaveTimer()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    toolbar = ToolBar()
    toolbar.show()
    sys.exit(app.exec_())