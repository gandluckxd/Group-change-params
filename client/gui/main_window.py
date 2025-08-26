"""
Main Window for Group Change Params
Modern minimalist interface on PyQt6
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QPushButton,
    QListWidget, QLabel, QMessageBox, QStatusBar,
    QSplitter, QFrame, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from core.api_client import get_api_client
from .styles import (
    MAIN_WINDOW_STYLE, TAB_STYLE, GROUP_BOX_STYLE, BUTTON_STYLES,
    INPUT_STYLE, LIST_STYLE, LABEL_STYLES
)


class DataLoadThread(QThread):
    """Thread for loading data from API"""
    
    data_loaded = pyqtSignal(dict)  # Signal when data is loaded
    error_occurred = pyqtSignal(str)  # Signal when error occurs
    
    def __init__(self, api_client, data_type: str, **kwargs):
        super().__init__()
        self.api_client = api_client
        self.data_type = data_type
        self.kwargs = kwargs
    
    def run(self):
        """Load data in background thread"""
        try:
            if self.data_type == "breeds":
                data = self.api_client.get_breeds()
            elif self.data_type == "color_groups":
                data = self.api_client.get_color_groups()
            elif self.data_type == "colors":
                group_title = self.kwargs.get("group_title")
                data = self.api_client.get_colors_by_group(group_title)
            elif self.data_type == "order_colors":
                order_id = self.kwargs.get("order_id")
                data = self.api_client.get_order_colors(order_id)
            elif self.data_type == "order_info":
                order_id = self.kwargs.get("order_id")
                data = self.api_client.get_order_info(order_id)
            elif self.data_type == "all_order_data":
                order_id = self.kwargs.get("order_id")
                # Load all data for order
                order_info = self.api_client.get_order_info(order_id)
                order_colors = self.api_client.get_order_colors(order_id)
                color_groups = self.api_client.get_color_groups()
                data = {
                    "order_info": order_info,
                    "order_colors": order_colors,
                    "color_groups": color_groups
                }
            else:
                raise ValueError(f"Unknown data type: {self.data_type}")
            
            self.data_loaded.emit({self.data_type: data})
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to load {self.data_type}: {str(e)}")


class BreedChangeTab(QWidget):
    """Tab for changing breed (wood type)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.breeds_data = []
        self.init_ui()
        self.load_breeds()  # Load breeds automatically
    
    def init_ui(self):
        """Initialize UI for breed change tab"""
        layout = QVBoxLayout(self)
        
        # Main group
        main_group = QGroupBox("Изменение породы дерева")
        main_group.setStyleSheet(GROUP_BOX_STYLE)
        main_layout = QFormLayout(main_group)
        
        # Breed selection
        self.breed_combo = QComboBox()
        self.breed_combo.setStyleSheet(INPUT_STYLE)
        self.breed_combo.setEnabled(False)
        main_layout.addRow("Новая порода:", self.breed_combo)
        
        # Apply button
        self.apply_breed_btn = QPushButton("Применить изменения")
        self.apply_breed_btn.setStyleSheet(BUTTON_STYLES["success"])
        self.apply_breed_btn.clicked.connect(self.apply_breed_change)
        self.apply_breed_btn.setEnabled(False)
        main_layout.addRow("", self.apply_breed_btn)
        
        # Status label
        self.status_label = QLabel("Загрузка пород...")
        self.status_label.setStyleSheet(LABEL_STYLES["info"])
        main_layout.addRow("Статус:", self.status_label)
        
        layout.addWidget(main_group)
        layout.addStretch()
    
    def load_breeds(self):
        """Load available breeds from API automatically"""
        api_client = get_api_client()
        
        # Create and start data loading thread
        self.data_thread = DataLoadThread(api_client, "breeds")
        self.data_thread.data_loaded.connect(self.on_data_loaded)
        self.data_thread.error_occurred.connect(self.on_error)
        self.data_thread.start()
    
    def on_data_loaded(self, data):
        """Handle loaded data"""
        self.breeds_data = data.get("breeds", [])
        
        # Populate combo box
        self.breed_combo.clear()
        for breed in self.breeds_data:
            self.breed_combo.addItem(breed["code"], breed)
        
        # Enable controls
        self.breed_combo.setEnabled(True)
        self.apply_breed_btn.setEnabled(True)
        self.status_label.setText(f"Загружено {len(self.breeds_data)} пород")
    
    def on_error(self, error_msg):
        """Handle error"""
        self.status_label.setText("Ошибка загрузки пород")
        QMessageBox.critical(self, "Ошибка", error_msg)
    
    def apply_breed_change(self):
        """Apply breed change"""
        # Get order ID from parent window
        order_id = self.parent_window.get_current_order_id()
        if not order_id:
            QMessageBox.warning(self, "Ошибка", "Введите ID заказа в общем поле")
            return
        
        if self.breed_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите породу")
            return
        
        breed_data = self.breed_combo.currentData()
        breed_code = breed_data["code"]
        
        # Confirm action
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Изменить породу на '{breed_code}' в заказе {order_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            api_client = get_api_client()
            result = api_client.change_breed(order_id, breed_code)
            
            if result.get("success"):
                QMessageBox.information(self, "Успех", result.get("message", "Порода успешно изменена"))
                self.status_label.setText("Порода изменена успешно")
            else:
                QMessageBox.warning(self, "Предупреждение", result.get("error", "Не удалось изменить породу"))
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при изменении породы: {str(e)}")


class ColorChangeTab(QWidget):
    """Tab for changing color"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.color_groups_data = []
        self.colors_data = []
        self.order_colors_data = []
        self.init_ui()
        self.load_color_groups()  # Load color groups automatically
    
    def init_ui(self):
        """Initialize UI for color change tab"""
        layout = QVBoxLayout(self)
        
        # Main group
        main_group = QGroupBox("Изменение цвета")
        main_group.setStyleSheet(GROUP_BOX_STYLE)
        main_layout = QVBoxLayout(main_group)
        
        # Splitter for two columns
        splitter = QSplitter(Qt.Horizontal)
        
        # Right column - Old colors selection (now first)
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        old_colors_group = QGroupBox("Цвета для замены")
        old_colors_group.setStyleSheet(GROUP_BOX_STYLE)
        old_colors_layout = QVBoxLayout(old_colors_group)
        
        old_colors_layout.addWidget(QLabel("Выберите цвета, которые нужно заменить:"))
        
        self.old_colors_list = QListWidget()
        self.old_colors_list.setStyleSheet(LIST_STYLE)
        self.old_colors_list.setSelectionMode(QListWidget.MultiSelection)
        old_colors_layout.addWidget(self.old_colors_list)
        
        right_layout.addWidget(old_colors_group)
        
        # Left column - New color selection (now second)
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        
        new_color_group = QGroupBox("Новый цвет")
        new_color_group.setStyleSheet(GROUP_BOX_STYLE)
        new_color_layout = QFormLayout(new_color_group)
        
        # Color group selection
        self.color_group_combo = QComboBox()
        self.color_group_combo.setStyleSheet(INPUT_STYLE)
        self.color_group_combo.setEnabled(False)
        self.color_group_combo.currentTextChanged.connect(self.on_color_group_changed)
        new_color_layout.addRow("Категория цвета:", self.color_group_combo)
        
        # Color selection
        self.color_combo = QComboBox()
        self.color_combo.setStyleSheet(INPUT_STYLE)
        self.color_combo.setEnabled(False)
        new_color_layout.addRow("Цвет:", self.color_combo)
        
        left_layout.addWidget(new_color_group)
        left_layout.addStretch()
        
        splitter.addWidget(right_frame)
        splitter.addWidget(left_frame)
        splitter.setSizes([400, 400])
        
        main_layout.addWidget(splitter)
        
        # Bottom section - Apply button and status
        bottom_section = QFrame()
        bottom_layout = QFormLayout(bottom_section)
        
        self.apply_color_btn = QPushButton("Применить изменения")
        self.apply_color_btn.setStyleSheet(BUTTON_STYLES["success"])
        self.apply_color_btn.clicked.connect(self.apply_color_change)
        self.apply_color_btn.setEnabled(False)
        bottom_layout.addRow("", self.apply_color_btn)
        
        self.status_label = QLabel("Загрузка категорий цветов...")
        self.status_label.setStyleSheet(LABEL_STYLES["info"])
        bottom_layout.addRow("Статус:", self.status_label)
        
        main_layout.addWidget(bottom_section)
        
        layout.addWidget(main_group)
    
    def load_color_groups(self):
        """Load color groups from API automatically"""
        api_client = get_api_client()
        
        self.status_label.setText("Загрузка категорий цветов...")
        
        self.data_thread = DataLoadThread(api_client, "color_groups")
        self.data_thread.data_loaded.connect(self.on_color_groups_loaded)
        self.data_thread.error_occurred.connect(self.on_error)
        self.data_thread.start()
    
    def load_order_colors(self, order_id):
        """Load colors used in order"""
        api_client = get_api_client()
        
        self.status_label.setText("Загрузка цветов заказа...")
        
        self.data_thread = DataLoadThread(api_client, "order_colors", order_id=order_id)
        self.data_thread.data_loaded.connect(self.on_order_colors_loaded)
        self.data_thread.error_occurred.connect(self.on_error)
        self.data_thread.start()
    
    def on_color_groups_loaded(self, data):
        """Handle loaded color groups"""
        self.color_groups_data = data.get("color_groups", [])
        
        self.color_group_combo.clear()
        for group in self.color_groups_data:
            self.color_group_combo.addItem(group["title"])
        
        self.color_group_combo.setEnabled(True)
        self.status_label.setText(f"Загружено {len(self.color_groups_data)} категорий")
    
    def on_order_colors_loaded(self, data):
        """Handle loaded order colors"""
        self.order_colors_data = data.get("order_colors", [])
        
        self.old_colors_list.clear()
        for color in self.order_colors_data:
            item = QListWidgetItem(color["title"])
            item.setData(Qt.UserRole, color["title"])
            self.old_colors_list.addItem(item)
        
        self.apply_color_btn.setEnabled(True)
        self.status_label.setText(f"Загружено {len(self.order_colors_data)} цветов заказа")
    
    def on_color_group_changed(self, group_title):
        """Handle color group change"""
        if not group_title:
            self.color_combo.clear()
            self.color_combo.setEnabled(False)
            return
        
        print(f"🔄 Смена категории цвета на: '{group_title}'")
        
        api_client = get_api_client()
        
        self.color_combo.setEnabled(False)
        self.color_combo.clear()
        self.status_label.setText(f"Загрузка цветов группы '{group_title}'...")
        
        # Clear previous colors data
        self.colors_data = []
        
        print(f"🔄 Запуск загрузки цветов для группы '{group_title}'")
        
        self.data_thread = DataLoadThread(api_client, "colors", group_title=group_title)
        self.data_thread.data_loaded.connect(self.on_colors_loaded)
        self.data_thread.error_occurred.connect(self.on_error)
        self.data_thread.start()
    
    def on_colors_loaded(self, data):
        """Handle loaded colors"""
        self.colors_data = data.get("colors", [])
        
        print(f"🔄 Загружено {len(self.colors_data)} цветов для группы '{self.color_group_combo.currentText()}'")
        
        self.color_combo.clear()
        for color in self.colors_data:
            # Ensure we have the group_title for each color
            if "group_title" not in color:
                # Get current selected group title
                current_group = self.color_group_combo.currentText()
                color["group_title"] = current_group
                print(f"🔄 Добавлен group_title '{current_group}' для цвета '{color['title']}'")
            
            self.color_combo.addItem(color["title"], color)
        
        self.color_combo.setEnabled(True)
        self.status_label.setText(f"Загружено {len(self.colors_data)} цветов для группы '{self.color_group_combo.currentText()}'")
    
    def on_error(self, error_msg):
        """Handle error"""
        self.status_label.setText("Ошибка загрузки")
        QMessageBox.critical(self, "Ошибка", error_msg)
    
    def apply_color_change(self):
        """Apply color change"""
        # Get order ID from parent window
        order_id = self.parent_window.get_current_order_id()
        if not order_id:
            QMessageBox.warning(self, "Ошибка", "Введите ID заказа в общем поле")
            return
        
        if self.color_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите новый цвет")
            return
        
        selected_items = self.old_colors_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите цвета для замены")
            return
        
        color_data = self.color_combo.currentData()
        new_color = color_data["title"]
        
        # Get group_title from color data or current selection
        new_colorgroup = color_data.get("group_title")
        if not new_colorgroup:
            # Fallback to current group selection
            new_colorgroup = self.color_group_combo.currentText()
            print(f"🔄 Используем fallback group_title: '{new_colorgroup}'")
        
        print(f"🔄 Выбран цвет: '{new_color}', группа: '{new_colorgroup}'")
        
        old_colors = [item.data(Qt.UserRole) for item in selected_items]
        
        # Confirm action
        old_colors_str = ", ".join(old_colors)
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Заменить цвета '{old_colors_str}' на '{new_color}' ({new_colorgroup}) в заказе {order_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            api_client = get_api_client()
            result = api_client.change_color(order_id, new_color, new_colorgroup, old_colors)
            
            if result.get("success"):
                QMessageBox.information(self, "Успех", result.get("message", "Цвет успешно изменен"))
                self.status_label.setText("Цвет изменен успешно")
            else:
                QMessageBox.warning(self, "Предупреждение", result.get("error", "Не удалось изменить цвет"))
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при изменении цвета: {str(e)}")


class GroupChangeParamsWindow(QMainWindow):
    """Main window for Group Change Params application"""
    
    def __init__(self):
        super().__init__()
        self.current_order_id = None
        self.order_info = {}
        self.init_ui()
        self.setup_window()
    
    def init_ui(self):
        """Initialize user interface"""
        # Set window style
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title label
        title_label = QLabel("Групповое изменение параметров")
        title_label.setStyleSheet(LABEL_STYLES["title"])
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Order section
        order_section = self.create_order_section()
        layout.addWidget(order_section)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_STYLE)
        
        # Add tabs
        self.breed_tab = BreedChangeTab(self)
        self.color_tab = ColorChangeTab(self)
        
        self.tabs.addTab(self.breed_tab, "🌳 Изменение породы")
        self.tabs.addTab(self.color_tab, "🎨 Изменение цвета")
        
        layout.addWidget(self.tabs)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
    
    def create_order_section(self):
        """Create order input and info section"""
        order_group = QGroupBox("Информация о заказе")
        order_group.setStyleSheet(GROUP_BOX_STYLE)
        order_layout = QVBoxLayout(order_group)
        
        # Order ID input section
        input_section = QFrame()
        input_layout = QFormLayout(input_section)
        
        self.order_id_input = QLineEdit()
        self.order_id_input.setPlaceholderText("Введите ID заказа")
        self.order_id_input.setStyleSheet(INPUT_STYLE)
        self.order_id_input.returnPressed.connect(self.load_order_data)
        input_layout.addRow("ID заказа:", self.order_id_input)
        
        self.load_order_btn = QPushButton("Загрузить данные заказа")
        self.load_order_btn.setStyleSheet(BUTTON_STYLES["primary"])
        self.load_order_btn.clicked.connect(self.load_order_data)
        input_layout.addRow("", self.load_order_btn)
        
        order_layout.addWidget(input_section)
        
        # Order info display section
        info_section = QFrame()
        info_layout = QFormLayout(info_section)
        
        self.order_name_label = QLabel("—")
        self.order_name_label.setStyleSheet(LABEL_STYLES["info"])
        info_layout.addRow("Наименование:", self.order_name_label)
        
        self.order_number_label = QLabel("—")
        self.order_number_label.setStyleSheet(LABEL_STYLES["info"])
        info_layout.addRow("Номер заказа:", self.order_number_label)
        
        self.order_date_label = QLabel("—")
        self.order_date_label.setStyleSheet(LABEL_STYLES["info"])
        info_layout.addRow("Дата заказа:", self.order_date_label)
        
        self.customer_name_label = QLabel("—")
        self.customer_name_label.setStyleSheet(LABEL_STYLES["info"])
        info_layout.addRow("Клиент:", self.customer_name_label)
        
        order_layout.addWidget(info_section)
        
        return order_group
    
    def get_current_order_id(self):
        """Get current order ID"""
        return self.current_order_id
    
    def load_order_data(self):
        """Load order data and notify tabs"""
        try:
            order_id = int(self.order_id_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректный ID заказа")
            return
        
        self.current_order_id = order_id
        
        # Disable button during loading
        self.load_order_btn.setEnabled(False)
        self.load_order_btn.setText("Загрузка...")
        
        # Load order info and colors
        api_client = get_api_client()
        self.data_thread = DataLoadThread(api_client, "all_order_data", order_id=order_id)
        self.data_thread.data_loaded.connect(self.on_order_data_loaded)
        self.data_thread.error_occurred.connect(self.on_order_load_error)
        self.data_thread.start()
    
    def on_order_data_loaded(self, data):
        """Handle loaded order data"""
        order_data = data.get("all_order_data", {})
        
        # Update order info
        order_info = order_data.get("order_info", {})
        if order_info:
            self.order_info = order_info
            self.order_name_label.setText(order_info.get("ORDER_NAME", "—"))
            self.order_number_label.setText(str(order_info.get("ORDERNO", "—")))
            self.order_date_label.setText(str(order_info.get("ORDERDATE", "—")))
            self.customer_name_label.setText(order_info.get("CUSTOMER_NAME", "—"))
        
        # Load order colors in color tab
        order_colors = order_data.get("order_colors", [])
        if hasattr(self.color_tab, 'on_order_colors_loaded'):
            self.color_tab.on_order_colors_loaded({"order_colors": order_colors})
        
        # Re-enable button
        self.load_order_btn.setEnabled(True)
        self.load_order_btn.setText("Загрузить данные заказа")
        
        self.status_bar.showMessage(f"Загружены данные заказа {self.current_order_id}")
    
    def on_order_load_error(self, error_msg):
        """Handle order load error"""
        self.load_order_btn.setEnabled(True)
        self.load_order_btn.setText("Загрузить данные заказа")
        self.status_bar.showMessage("Ошибка загрузки заказа")
        QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные заказа: {error_msg}")
    
    def setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("Group Change Params - Групповое изменение параметров")
        self.setMinimumSize(900, 950)  # Increased height by 250
        self.resize(1200, 1050)  # Increased height by 250
    
    def set_order_id(self, order_id: int):
        """Set order ID from command line argument"""
        self.order_id_input.setText(str(order_id))
        self.load_order_data()  # Automatically load order data
    
    def closeEvent(self, event):
        """Handle close event"""
        reply = QMessageBox.question(
            self, "Выход",
            "Вы действительно хотите выйти?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
