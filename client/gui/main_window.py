"""
Main Window for Group Change Params
Modern minimalist interface on PyQt6
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QPushButton,
    QLabel, QMessageBox, QStatusBar,
    QSplitter, QFrame, QCheckBox, QScrollArea,
    QAction, QDialog, QDialogButtonBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from core.api_client import get_api_client
from .styles import (
    MAIN_WINDOW_STYLE, TAB_STYLE, GROUP_BOX_STYLE, BUTTON_STYLES,
    INPUT_STYLE, LABEL_STYLES, CHECKBOX_STYLE, DIALOG_BUTTON_STYLE
)


class LoadOrderDialog(QDialog):
    """Dialog for loading order data"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Загрузка заказа")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel("Введите ID заказа для загрузки данных:")
        info_label.setStyleSheet(LABEL_STYLES["subtitle"])
        layout.addWidget(info_label)
        
        # Order ID input
        self.order_id_input = QLineEdit()
        self.order_id_input.setPlaceholderText("Введите ID заказа")
        self.order_id_input.setStyleSheet(INPUT_STYLE)
        self.order_id_input.returnPressed.connect(self.accept)
        layout.addWidget(self.order_id_input)
        
        # Current order info (if any)
        if hasattr(self.parent(), 'current_order_id') and self.parent().current_order_id:
            current_label = QLabel(f"Текущий заказ: {self.parent().current_order_id}")
            current_label.setStyleSheet(LABEL_STYLES["info"])
            layout.addWidget(current_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # Style buttons with Russian text
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Загрузить")
        ok_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("Отмена")
        cancel_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        button_layout.addWidget(self.button_box)
        layout.addLayout(button_layout)
        
        # Focus on input
        self.order_id_input.setFocus()
    
    def get_order_id(self):
        """Get entered order ID"""
        try:
            return int(self.order_id_input.text().strip())
        except ValueError:
            self.parent().show_warning_message("Ошибка ввода", "Введите корректный числовой ID заказа")
            return None


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


class StuffsetsBreedChangeTab(QWidget):
    """Tab for changing breed (wood type) in stuffsets (наборы) orderitems"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.breeds_data = []
        self.current_order_id = None
        self.current_stuffsets_breeds = []
        self.init_ui()
        self.load_breeds()  # Load breeds automatically
    
    def init_ui(self):
        """Initialize UI for stuffsets breed change tab"""
        layout = QVBoxLayout(self)
        
        # Info section
        info_group = QGroupBox("Выбор текущих пород наборов для замены")
        info_group.setStyleSheet(GROUP_BOX_STYLE)
        info_layout = QVBoxLayout(info_group)
        
        # Current breeds selection with checkboxes
        breeds_label = QLabel("Выберите породы наборов для замены:")
        breeds_label.setStyleSheet(LABEL_STYLES["info"])
        info_layout.addWidget(breeds_label)
        
        # Scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setMaximumHeight(120)
        scroll_area.setWidgetResizable(True)
        
        self.breeds_widget = QWidget()
        self.breeds_layout = QVBoxLayout(self.breeds_widget)
        self.breeds_layout.setSpacing(0)  # Ultra compact spacing between checkboxes
        self.breeds_layout.setContentsMargins(3, 3, 3, 3)  # Ultra compact margins
        self.breed_checkboxes = {}  # Dictionary to store checkboxes by breed name
        
        scroll_area.setWidget(self.breeds_widget)
        info_layout.addWidget(scroll_area)
        
        layout.addWidget(info_group)
        
        # Main group
        main_group = QGroupBox("Изменение породы дерева для наборов")
        main_group.setStyleSheet(GROUP_BOX_STYLE)
        main_layout = QFormLayout(main_group)
        
        # Breed selection
        self.breed_combo = QComboBox()
        self.breed_combo.setStyleSheet(INPUT_STYLE)
        self.breed_combo.setEnabled(False)
        self.breed_combo.currentTextChanged.connect(self.update_apply_button_state)
        main_layout.addRow("Новая порода:", self.breed_combo)
        
        # Apply button
        self.apply_breed_btn = QPushButton("Применить изменения для наборов")
        self.apply_breed_btn.setStyleSheet(BUTTON_STYLES["success"])
        self.apply_breed_btn.clicked.connect(self.apply_stuffsets_breed_change)
        self.apply_breed_btn.setEnabled(False)
        main_layout.addRow("", self.apply_breed_btn)
        
        layout.addWidget(main_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def load_breeds(self):
        """Load available breeds in background thread"""
        api_client = get_api_client()
        self.data_thread = DataLoadThread(api_client, "breeds")
        self.data_thread.data_loaded.connect(self.on_breeds_loaded)
        self.data_thread.error_occurred.connect(self.on_data_error)
        self.data_thread.start()
    
    def on_breeds_loaded(self, data):
        """Handle breeds data loaded"""
        self.breeds_data = data.get("breeds", [])
        self.breed_combo.clear()
        self.breed_combo.addItem("Выберите породу...", "")
        
        for breed in self.breeds_data:
            # API returns breeds as dictionaries after JSON serialization
            breed_code = breed["code"]
            self.breed_combo.addItem(breed_code, breed_code)
        
        self.breed_combo.setEnabled(True)
        if self.parent_window:
            self.parent_window.status_bar.showMessage("Породы дерева загружены")
    
    def on_data_error(self, error_message):
        """Handle data loading error"""
        if self.parent_window:
            self.parent_window.status_bar.showMessage(f"Ошибка: {error_message}")
            QMessageBox.warning(self, "Ошибка", error_message)
    
    def load_stuffsets_breeds(self, order_id):
        """Load current stuffsets breeds for order"""
        self.current_order_id = order_id
        try:
            api_client = get_api_client()
            breeds = api_client.get_stuffsets_breeds(order_id)
            self.current_stuffsets_breeds = breeds
            
            # Clear existing checkboxes
            for checkbox in self.breed_checkboxes.values():
                checkbox.setParent(None)
            self.breed_checkboxes.clear()
            
            # Create checkboxes for each breed
            if breeds:
                for breed in breeds:
                    checkbox = QCheckBox(f"🌳 {breed}")
                    checkbox.setStyleSheet(CHECKBOX_STYLE)
                    checkbox.setChecked(True)  # Default to selected
                    checkbox.stateChanged.connect(self.update_apply_button_state)
                    self.breeds_layout.addWidget(checkbox)
                    self.breed_checkboxes[breed] = checkbox
                
                self.update_apply_button_state()
            else:
                label = QLabel("Нет наборов с породой дерева в этом заказе")
                label.setStyleSheet(LABEL_STYLES["info"])
                self.breeds_layout.addWidget(label)
                self.apply_breed_btn.setEnabled(False)
            
            if self.parent_window:
                self.parent_window.status_bar.showMessage(f"Загружено {len(breeds)} пород для stuffsets")
        
        except Exception as e:
            if self.parent_window:
                self.parent_window.status_bar.showMessage(f"Ошибка загрузки пород: {str(e)}")
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить породы stuffsets: {str(e)}")
    
    def update_apply_button_state(self):
        """Update apply button state based on selections"""
        # Check if any breeds are selected and new breed is chosen
        selected_breeds = self.get_selected_breeds()
        selected_new_breed = self.breed_combo.currentData()
        
        is_enabled = (
            len(selected_breeds) > 0 and 
            bool(selected_new_breed) and 
            selected_new_breed != ""
        )
        self.apply_breed_btn.setEnabled(is_enabled)
    
    def get_selected_breeds(self):
        """Get list of selected breeds from checkboxes"""
        selected = []
        for breed_name, checkbox in self.breed_checkboxes.items():
            if checkbox.isChecked():
                selected.append(breed_name)
        return selected
    
    def apply_stuffsets_breed_change(self):
        """Apply breed change for stuffsets"""
        if not self.current_order_id:
            if self.parent_window:
                self.parent_window.show_warning_message("Ошибка", "Не выбран заказ")
            return
        
        selected_breeds = self.get_selected_breeds()
        if not selected_breeds:
            if self.parent_window:
                self.parent_window.show_warning_message("Ошибка", "Выберите породы для замены")
            return
        
        new_breed = self.breed_combo.currentData()
        if not new_breed or new_breed == "":
            if self.parent_window:
                self.parent_window.show_warning_message("Ошибка", "Выберите новую породу")
            return
        
        breeds_text = ", ".join(selected_breeds)
        order_name = self.parent_window.get_order_display_name() if self.parent_window else f"заказ ID: {self.current_order_id}"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение изменения")
        msg_box.setText(f"Изменить породы {breeds_text} на {new_breed} для наборов в {order_name}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Russian button text and styling
        yes_button = msg_box.button(QMessageBox.Yes)
        yes_button.setText("Да")
        yes_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        no_button = msg_box.button(QMessageBox.No)
        no_button.setText("Нет")
        no_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.Yes:
            try:
                api_client = get_api_client()
                # Pass selected breeds to API for selective change
                result = api_client.change_stuffsets_breed(self.current_order_id, new_breed, selected_breeds)
                
                if result.get("success", False):
                    order_name = self.parent_window.get_order_display_name() if self.parent_window else f"заказ ID: {self.current_order_id}"
                    success_msg = f"Породы наборов успешно изменены в {order_name}"
                    if self.parent_window:
                        self.parent_window.show_success_message("Изменение завершено", success_msg)
                    # Reload current breeds
                    self.load_stuffsets_breeds(self.current_order_id)
                    if self.parent_window:
                        self.parent_window.status_bar.showMessage("Породы наборов успешно изменены")
                else:
                    error_msg = result.get("error", "Неизвестная ошибка")
                    if self.parent_window:
                        self.parent_window.show_warning_message("Ошибка", f"Не удалось изменить породы: {error_msg}")
                        self.parent_window.status_bar.showMessage("Ошибка изменения пород stuffsets")
            
            except Exception as e:
                if self.parent_window:
                    self.parent_window.show_error_message("Ошибка", f"Ошибка при изменении пород: {str(e)}")
                    self.parent_window.status_bar.showMessage(f"Ошибка: {str(e)}")


class BreedChangeTab(QWidget):
    """Tab for changing breed (wood type) in adds (дополнения)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.breeds_data = []
        self.current_order_id = None
        self.current_adds_breeds = []
        self.init_ui()
        self.load_breeds()  # Load breeds automatically
    
    def init_ui(self):
        """Initialize UI for breed change tab"""
        layout = QVBoxLayout(self)
        
        # Info section for current breeds selection
        info_group = QGroupBox("Выбор текущих пород дополнений для замены")
        info_group.setStyleSheet(GROUP_BOX_STYLE)
        info_layout = QVBoxLayout(info_group)
        
        # Current breeds selection with checkboxes
        breeds_label = QLabel("Выберите породы дополнений для замены:")
        breeds_label.setStyleSheet(LABEL_STYLES["info"])
        info_layout.addWidget(breeds_label)
        
        # Scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setMaximumHeight(120)
        scroll_area.setWidgetResizable(True)
        
        self.adds_breeds_widget = QWidget()
        self.adds_breeds_layout = QVBoxLayout(self.adds_breeds_widget)
        self.adds_breeds_layout.setSpacing(0)  # Ultra compact spacing between checkboxes
        self.adds_breeds_layout.setContentsMargins(3, 3, 3, 3)  # Ultra compact margins
        self.adds_breed_checkboxes = {}  # Dictionary to store checkboxes by breed name
        
        scroll_area.setWidget(self.adds_breeds_widget)
        info_layout.addWidget(scroll_area)
        
        layout.addWidget(info_group)
        
        # Main group
        main_group = QGroupBox("Изменение породы дерева для дополнений")
        main_group.setStyleSheet(GROUP_BOX_STYLE)
        main_layout = QFormLayout(main_group)
        
        # Breed selection
        self.breed_combo = QComboBox()
        self.breed_combo.setStyleSheet(INPUT_STYLE)
        self.breed_combo.setEnabled(False)
        self.breed_combo.currentTextChanged.connect(self.update_apply_button_state)
        main_layout.addRow("Новая порода:", self.breed_combo)
        
        # Apply button
        self.apply_breed_btn = QPushButton("Применить изменения для дополнений")
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
        self.breed_combo.addItem("Выберите породу...", "")
        for breed in self.breeds_data:
            self.breed_combo.addItem(breed["code"], breed["code"])
        
        # Enable controls
        self.breed_combo.setEnabled(True)
        self.status_label.setText(f"Загружено {len(self.breeds_data)} пород")
        self.update_apply_button_state()
    
    def on_error(self, error_msg):
        """Handle error"""
        self.status_label.setText("Ошибка загрузки пород")
        QMessageBox.critical(self, "Ошибка", error_msg)
    
    def load_adds_breeds(self, order_id):
        """Load current adds breeds for order"""
        self.current_order_id = order_id
        try:
            api_client = get_api_client()
            breeds = api_client.get_adds_breeds(order_id)
            self.current_adds_breeds = breeds
            
            # Clear existing checkboxes
            for checkbox in self.adds_breed_checkboxes.values():
                checkbox.setParent(None)
            self.adds_breed_checkboxes.clear()
            
            # Create checkboxes for each breed
            if breeds:
                for breed in breeds:
                    checkbox = QCheckBox(f"🌳 {breed}")
                    checkbox.setStyleSheet(CHECKBOX_STYLE)
                    checkbox.setChecked(True)  # Default to selected
                    checkbox.stateChanged.connect(self.update_apply_button_state)
                    self.adds_breeds_layout.addWidget(checkbox)
                    self.adds_breed_checkboxes[breed] = checkbox
                
                self.update_apply_button_state()
            else:
                label = QLabel("Нет дополнений с породой дерева в этом заказе")
                label.setStyleSheet(LABEL_STYLES["info"])
                self.adds_breeds_layout.addWidget(label)
                self.apply_breed_btn.setEnabled(False)
            
            if self.parent_window:
                self.parent_window.status_bar.showMessage(f"Загружено {len(breeds)} пород для дополнений")
        
        except Exception as e:
            if self.parent_window:
                self.parent_window.status_bar.showMessage(f"Ошибка загрузки пород: {str(e)}")
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить породы дополнений: {str(e)}")
    
    def update_apply_button_state(self):
        """Update apply button state based on selections"""
        # Check if any breeds are selected and new breed is chosen
        selected_breeds = self.get_selected_adds_breeds()
        selected_new_breed = self.breed_combo.currentData()
        
        is_enabled = (
            len(selected_breeds) > 0 and 
            bool(selected_new_breed) and 
            selected_new_breed != ""
        )
        self.apply_breed_btn.setEnabled(is_enabled)
    
    def get_selected_adds_breeds(self):
        """Get list of selected adds breeds from checkboxes"""
        selected = []
        for breed_name, checkbox in self.adds_breed_checkboxes.items():
            if checkbox.isChecked():
                selected.append(breed_name)
        return selected
    
    def apply_breed_change(self):
        """Apply breed change"""
        if not self.current_order_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран заказ")
            return
        
        selected_breeds = self.get_selected_adds_breeds()
        if not selected_breeds:
            QMessageBox.warning(self, "Ошибка", "Выберите породы дополнений для замены")
            return
        
        new_breed = self.breed_combo.currentData()
        if not new_breed or new_breed == "":
            QMessageBox.warning(self, "Ошибка", "Выберите новую породу")
            return
        
        breeds_text = ", ".join(selected_breeds)
        order_name = self.parent_window.get_order_display_name() if self.parent_window else f"заказ ID: {self.current_order_id}"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение изменения")
        msg_box.setText(f"Изменить породы {breeds_text} на {new_breed} для дополнений в {order_name}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Russian button text and styling
        yes_button = msg_box.button(QMessageBox.Yes)
        yes_button.setText("Да")
        yes_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        no_button = msg_box.button(QMessageBox.No)
        no_button.setText("Нет")
        no_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.Yes:
            try:
                api_client = get_api_client()
                # Pass selected breeds to API for selective change
                result = api_client.change_breed(self.current_order_id, new_breed, selected_breeds)
                
                if result.get("success", False):
                    order_name = self.parent_window.get_order_display_name() if self.parent_window else f"заказ ID: {self.current_order_id}"
                    success_msg = f"Породы дополнений успешно изменены в {order_name}"
                    if self.parent_window:
                        self.parent_window.show_success_message("Изменение завершено", success_msg)
                    # Reload current breeds
                    self.load_adds_breeds(self.current_order_id)
                    if self.parent_window:
                        self.parent_window.status_bar.showMessage("Породы дополнений успешно изменены")
                else:
                    error_msg = result.get("error", "Неизвестная ошибка")
                    QMessageBox.warning(self, "Ошибка", f"Не удалось изменить породы: {error_msg}")
                    if self.parent_window:
                        self.parent_window.status_bar.showMessage("Ошибка изменения пород дополнений")
            
            except Exception as e:
                if self.parent_window:
                    self.parent_window.show_error_message("Ошибка", f"Ошибка при изменении пород: {str(e)}")
                    self.parent_window.status_bar.showMessage(f"Ошибка: {str(e)}")


class StuffsetsColorChangeTab(QWidget):
    """Tab for changing color in stuffsets (наборы) orderitems"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.color_groups_data = []
        self.colors_data = []
        self.order_colors_data = []
        self.color_checkboxes = {}
        self.current_order_id = None
        self.init_ui()
        self.load_color_groups()  # Load color groups automatically
    
    def init_ui(self):
        """Initialize UI for stuffsets color change tab"""
        layout = QVBoxLayout(self)
        
        # Main group
        main_group = QGroupBox("Изменение цвета наборов")
        main_group.setStyleSheet(GROUP_BOX_STYLE)
        main_layout = QVBoxLayout(main_group)
        
        # Splitter for two columns
        splitter = QSplitter(Qt.Horizontal)
        
        # Right column - Old colors selection (now first)
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        old_colors_group = QGroupBox("Цвета наборов для замены")
        old_colors_group.setStyleSheet(GROUP_BOX_STYLE)
        old_colors_layout = QVBoxLayout(old_colors_group)
        
        colors_label = QLabel("Выберите цвета наборов, которые нужно заменить:")
        colors_label.setStyleSheet(LABEL_STYLES["info"])
        old_colors_layout.addWidget(colors_label)
        
        # Scroll area for checkboxes
        colors_scroll_area = QScrollArea()
        colors_scroll_area.setMaximumHeight(200)
        colors_scroll_area.setWidgetResizable(True)
        
        self.colors_widget = QWidget()
        self.colors_layout = QVBoxLayout(self.colors_widget)
        self.colors_layout.setSpacing(0)  # Ultra compact spacing between checkboxes
        self.colors_layout.setContentsMargins(3, 3, 3, 3)  # Ultra compact margins
        self.color_checkboxes = {}  # Dictionary to store checkboxes by color name
        
        colors_scroll_area.setWidget(self.colors_widget)
        old_colors_layout.addWidget(colors_scroll_area)
        
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
        self.color_combo.currentTextChanged.connect(self.update_apply_color_button_state)
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
        
        self.apply_color_btn = QPushButton("Применить изменения для наборов")
        self.apply_color_btn.setStyleSheet(BUTTON_STYLES["success"])
        self.apply_color_btn.clicked.connect(self.apply_color_change)
        self.apply_color_btn.setEnabled(False)
        bottom_layout.addRow("", self.apply_color_btn)
        
        self.status_label = QLabel("Загрузка категорий цветов...")
        self.status_label.setStyleSheet(LABEL_STYLES["info"])
        bottom_layout.addRow("Статус:", self.status_label)
        
        main_layout.addWidget(bottom_section)
        
        layout.addWidget(main_group)
        layout.addStretch()
    
    def load_color_groups(self):
        """Load color groups from API automatically"""
        api_client = get_api_client()
        
        # Create and start data loading thread
        self.data_thread = DataLoadThread(api_client, "color_groups")
        self.data_thread.data_loaded.connect(self.on_data_loaded)
        self.data_thread.error_occurred.connect(self.on_error)
        self.data_thread.start()
    
    def on_data_loaded(self, data):
        """Handle loaded color groups"""
        self.color_groups_data = data.get("color_groups", [])
        
        # Populate combo box
        self.color_group_combo.clear()
        for group in self.color_groups_data:
            self.color_group_combo.addItem(group["title"])
        
        self.color_group_combo.setEnabled(True)
        self.status_label.setText(f"Загружено {len(self.color_groups_data)} категорий")
    
    def load_stuffsets_colors(self, order_id):
        """Load current stuffsets colors for order"""
        self.current_order_id = order_id
        try:
            api_client = get_api_client()
            colors_data = api_client.get_stuffsets_colors(order_id)
            self.order_colors_data = colors_data
            
            # Clear existing checkboxes
            for checkbox in self.color_checkboxes.values():
                checkbox.setParent(None)
            self.color_checkboxes.clear()
            
            # Create checkboxes for each color
            if colors_data:
                for color in colors_data:
                    checkbox = QCheckBox(f"🎨 {color['title']}")
                    checkbox.setStyleSheet(CHECKBOX_STYLE)
                    checkbox.setChecked(True)  # Default to selected
                    checkbox.stateChanged.connect(self.update_apply_color_button_state)
                    self.colors_layout.addWidget(checkbox)
                    self.color_checkboxes[color['title']] = checkbox
            else:
                label = QLabel("Нет цветов наборов в этом заказе")
                label.setStyleSheet(LABEL_STYLES["info"])
                self.colors_layout.addWidget(label)
            
            self.update_apply_color_button_state()
            self.status_label.setText(f"Загружено {len(colors_data)} цветов заказа")
        
        except Exception as e:
            if self.parent_window:
                self.parent_window.status_bar.showMessage(f"Ошибка загрузки цветов: {str(e)}")
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить цвета наборов: {str(e)}")
    
    def on_color_group_changed(self, group_title):
        """Handle color group change"""
        if not group_title:
            self.color_combo.clear()
            self.color_combo.setEnabled(False)
            return
        
        print(f"🔄 Смена категории цвета на: '{group_title}'")
        
        # Disable combo and clear it
        
        self.color_combo.setEnabled(False)
        self.color_combo.clear()
        self.status_label.setText(f"Загрузка цветов группы '{group_title}'...")
        
        # Load colors for this group in background thread
        api_client = get_api_client()
        self.colors_thread = DataLoadThread(api_client, "colors", group_title=group_title)
        self.colors_thread.data_loaded.connect(self.on_colors_loaded)
        self.colors_thread.error_occurred.connect(self.on_error)
        self.colors_thread.start()
    
    def on_colors_loaded(self, data):
        """Handle loaded colors for group"""
        self.colors_data = data.get("colors", [])
        
        self.color_combo.clear()
        for color in self.colors_data:
            self.color_combo.addItem(color["title"], color)
        
        self.color_combo.setEnabled(True)
        self.status_label.setText(f"Загружено {len(self.colors_data)} цветов для группы '{self.color_group_combo.currentText()}'")
    
    def on_error(self, error_msg):
        """Handle error"""
        self.status_label.setText("Ошибка загрузки")
        QMessageBox.critical(self, "Ошибка", error_msg)
    
    def update_apply_color_button_state(self):
        """Update apply color button state based on selections"""
        # Check if any colors are selected and new color is chosen
        selected_colors = self.get_selected_colors()
        selected_new_color = self.color_combo.currentData()
        selected_color_group = self.color_group_combo.currentText()
        
        is_enabled = (
            len(selected_colors) > 0 and 
            bool(selected_new_color) and
            bool(selected_color_group)
        )
        self.apply_color_btn.setEnabled(is_enabled)
    
    def get_selected_colors(self):
        """Get list of selected colors from checkboxes"""
        selected = []
        for color_name, checkbox in self.color_checkboxes.items():
            if checkbox.isChecked():
                selected.append(color_name)
        return selected
    
    def apply_color_change(self):
        """Apply color change"""
        if not self.current_order_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран заказ")
            return
        
        selected_colors = self.get_selected_colors()
        if not selected_colors:
            QMessageBox.warning(self, "Ошибка", "Выберите цвета наборов для замены")
            return
        
        if self.color_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите новый цвет")
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
        
        # Confirm action
        old_colors_str = ", ".join(selected_colors)
        order_name = self.parent_window.get_order_display_name() if self.parent_window else f"заказ ID: {self.current_order_id}"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение изменения")
        msg_box.setText(f"Заменить цвета наборов {old_colors_str} на {new_color} ({new_colorgroup}) в {order_name}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Russian button text and styling
        yes_button = msg_box.button(QMessageBox.Yes)
        yes_button.setText("Да")
        yes_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        no_button = msg_box.button(QMessageBox.No)
        no_button.setText("Нет")
        no_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        reply = msg_box.exec()
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            api_client = get_api_client()
            result = api_client.change_stuffsets_color(self.current_order_id, new_color, new_colorgroup, selected_colors)
            
            if result.get("success"):
                order_name = self.parent_window.get_order_display_name() if self.parent_window else f"заказ ID: {self.current_order_id}"
                success_msg = f"Цвета наборов успешно изменены в {order_name}"
                if self.parent_window:
                    self.parent_window.show_success_message("Изменение завершено", success_msg)
                self.status_label.setText("Цвета наборов изменены успешно")
                # Reload colors to update the checkboxes
                self.load_stuffsets_colors(self.current_order_id)
            else:
                error_msg = result.get("error", "Не удалось изменить цвета наборов")
                QMessageBox.warning(self, "Ошибка", error_msg)
                self.status_label.setText("Ошибка изменения цветов наборов")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при изменении цветов наборов: {str(e)}")
            self.status_label.setText("Критическая ошибка")


class ColorChangeTab(QWidget):
    """Tab for changing color in adds (дополнения)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.color_groups_data = []
        self.colors_data = []
        self.order_colors_data = []
        self.color_checkboxes = {}
        self.init_ui()
        self.load_color_groups()  # Load color groups automatically
    
    def init_ui(self):
        """Initialize UI for color change tab"""
        layout = QVBoxLayout(self)
        
        # Main group
        main_group = QGroupBox("Изменение цвета дополнений")
        main_group.setStyleSheet(GROUP_BOX_STYLE)
        main_layout = QVBoxLayout(main_group)
        
        # Splitter for two columns
        splitter = QSplitter(Qt.Horizontal)
        
        # Right column - Old colors selection (now first)
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        old_colors_group = QGroupBox("Цвета дополнений для замены")
        old_colors_group.setStyleSheet(GROUP_BOX_STYLE)
        old_colors_layout = QVBoxLayout(old_colors_group)
        
        colors_label = QLabel("Выберите цвета дополнений, которые нужно заменить:")
        colors_label.setStyleSheet(LABEL_STYLES["info"])
        old_colors_layout.addWidget(colors_label)
        
        # Scroll area for checkboxes
        colors_scroll_area = QScrollArea()
        colors_scroll_area.setMaximumHeight(200)
        colors_scroll_area.setWidgetResizable(True)
        
        self.colors_widget = QWidget()
        self.colors_layout = QVBoxLayout(self.colors_widget)
        self.colors_layout.setSpacing(0)  # Ultra compact spacing between checkboxes
        self.colors_layout.setContentsMargins(3, 3, 3, 3)  # Ultra compact margins
        self.color_checkboxes = {}  # Dictionary to store checkboxes by color name
        
        colors_scroll_area.setWidget(self.colors_widget)
        old_colors_layout.addWidget(colors_scroll_area)
        
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
        self.color_combo.currentTextChanged.connect(self.update_apply_color_button_state)
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
        
        self.apply_color_btn = QPushButton("Применить изменения для дополнений")
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
        
        # Clear existing checkboxes
        for checkbox in self.color_checkboxes.values():
            checkbox.setParent(None)
        self.color_checkboxes.clear()
        
        # Create checkboxes for each color
        if self.order_colors_data:
            for color in self.order_colors_data:
                checkbox = QCheckBox(f"🎨 {color['title']}")
                checkbox.setStyleSheet(CHECKBOX_STYLE)
                checkbox.setChecked(True)  # Default to selected
                checkbox.stateChanged.connect(self.update_apply_color_button_state)
                self.colors_layout.addWidget(checkbox)
                self.color_checkboxes[color['title']] = checkbox
        else:
            label = QLabel("Нет цветов дополнений в этом заказе")
            label.setStyleSheet(LABEL_STYLES["info"])
            self.colors_layout.addWidget(label)
        
        self.update_apply_color_button_state()
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
    
    def update_apply_color_button_state(self):
        """Update apply color button state based on selections"""
        # Check if any colors are selected and new color is chosen
        selected_colors = self.get_selected_colors()
        selected_new_color = self.color_combo.currentData()
        selected_color_group = self.color_group_combo.currentText()
        
        is_enabled = (
            len(selected_colors) > 0 and 
            bool(selected_new_color) and
            bool(selected_color_group)
        )
        self.apply_color_btn.setEnabled(is_enabled)
    
    def get_selected_colors(self):
        """Get list of selected colors from checkboxes"""
        selected = []
        for color_name, checkbox in self.color_checkboxes.items():
            if checkbox.isChecked():
                selected.append(color_name)
        return selected
    
    def apply_color_change(self):
        """Apply color change"""
        # Get order ID from parent window
        order_id = self.parent_window.get_current_order_id()
        if not order_id:
            QMessageBox.warning(self, "Ошибка", "Загрузите заказ через меню 'Параметры → Загрузить заказ...'")
            return
        
        selected_colors = self.get_selected_colors()
        if not selected_colors:
            QMessageBox.warning(self, "Ошибка", "Выберите цвета для замены")
            return
        
        if self.color_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите новый цвет")
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
        
        # Confirm action
        old_colors_str = ", ".join(selected_colors)
        order_name = self.parent_window.get_order_display_name() if self.parent_window else f"заказ ID: {order_id}"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение изменения")
        msg_box.setText(f"Заменить цвета дополнений {old_colors_str} на {new_color} ({new_colorgroup}) в {order_name}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Russian button text and styling
        yes_button = msg_box.button(QMessageBox.Yes)
        yes_button.setText("Да")
        yes_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        no_button = msg_box.button(QMessageBox.No)
        no_button.setText("Нет")
        no_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        reply = msg_box.exec()
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            api_client = get_api_client()
            result = api_client.change_color(order_id, new_color, new_colorgroup, selected_colors)
            
            if result.get("success"):
                order_name = self.parent_window.get_order_display_name() if self.parent_window else f"заказ ID: {order_id}"
                success_msg = f"Цвета дополнений успешно изменены в {order_name}"
                if self.parent_window:
                    self.parent_window.show_success_message("Изменение завершено", success_msg)
                self.status_label.setText("Цвета изменены успешно")
                # Reload colors to update the checkboxes
                if hasattr(self.parent_window, 'current_order_id') and self.parent_window.current_order_id:
                    self.parent_window.load_order_data_by_id(self.parent_window.current_order_id)
            else:
                error_msg = result.get("error", "Не удалось изменить цвета")
                QMessageBox.warning(self, "Ошибка", error_msg)
                self.status_label.setText("Ошибка изменения цветов")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при изменении цветов: {str(e)}")
            self.status_label.setText("Критическая ошибка")


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
        
        # Create menu bar
        self.create_menu_bar()
        
        # Title label
        title_label = QLabel("Групповое изменение параметров")
        title_label.setStyleSheet(LABEL_STYLES["title"])
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Order info section (display only)
        order_info_section = self.create_order_info_section()
        layout.addWidget(order_info_section)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_STYLE)
        
        # Add tabs
        self.breed_tab = BreedChangeTab(self)
        self.stuffsets_breed_tab = StuffsetsBreedChangeTab(self)
        self.color_tab = ColorChangeTab(self)
        self.stuffsets_color_tab = StuffsetsColorChangeTab(self)
        
        self.tabs.addTab(self.breed_tab, "🌳 Изменение породы дополнений")
        self.tabs.addTab(self.stuffsets_breed_tab, "🌳 Изменение породы наборов")
        self.tabs.addTab(self.color_tab, "🎨 Изменение цвета дополнений")
        self.tabs.addTab(self.stuffsets_color_tab, "🎨 Изменение цвета наборов")
        
        layout.addWidget(self.tabs)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
    
    def create_order_info_section(self):
        """Create order info display section (read-only)"""
        order_group = QGroupBox("Информация о заказе")
        order_group.setStyleSheet(GROUP_BOX_STYLE)
        order_layout = QFormLayout(order_group)
        
        # Order info labels (initialized with default values)
        self.order_number_label = QLabel("—")
        self.order_number_label.setStyleSheet(LABEL_STYLES["info"])
        order_layout.addRow("Номер заказа:", self.order_number_label)
        
        self.order_date_label = QLabel("—")
        self.order_date_label.setStyleSheet(LABEL_STYLES["info"])
        order_layout.addRow("Дата заказа:", self.order_date_label)
        
        self.order_name_label = QLabel("—")
        self.order_name_label.setStyleSheet(LABEL_STYLES["info"])
        order_layout.addRow("Адрес:", self.order_name_label)
        
        self.customer_name_label = QLabel("—")
        self.customer_name_label.setStyleSheet(LABEL_STYLES["info"])
        order_layout.addRow("Клиент:", self.customer_name_label)
        
        # Current order ID label
        self.current_order_label = QLabel("Не загружен")
        self.current_order_label.setStyleSheet(LABEL_STYLES["info"])
        order_layout.addRow("ID заказа:", self.current_order_label)
        
        return order_group

    def get_current_order_id(self):
        """Get current order ID"""
        return self.current_order_id
    
    def get_order_display_name(self):
        """Get order display name for messages"""
        if hasattr(self, 'order_info') and self.order_info:
            order_number = self.order_info.get("ORDERNO", "")
            if order_number:
                return f"заказ №{order_number} (ID: {self.current_order_id})"
        return f"заказ ID: {self.current_order_id}" if self.current_order_id else "заказ"
    
    def show_success_message(self, title, message):
        """Show success message with recalculation warning"""
        full_message = f"{message}\n\nОБЯЗАТЕЛЬНО ПЕРЕСЧИТАЙТЕ ЗАКАЗ!"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(full_message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Style OK button
        ok_button = msg_box.button(QMessageBox.Ok)
        ok_button.setText("ОК")
        ok_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        msg_box.exec()
    
    def show_warning_message(self, title, message):
        """Show warning message with styled button"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Style OK button
        ok_button = msg_box.button(QMessageBox.Ok)
        ok_button.setText("ОК")
        ok_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        msg_box.exec()
    
    def show_error_message(self, title, message):
        """Show error message with styled button"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Style OK button
        ok_button = msg_box.button(QMessageBox.Ok)
        ok_button.setText("ОК")
        ok_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        msg_box.exec()
    
    def load_order_data_by_id(self, order_id: int):
        """Load order data by ID and notify tabs"""
        self.current_order_id = order_id
        
        # Load order info and colors
        api_client = get_api_client()
        self.data_thread = DataLoadThread(api_client, "all_order_data", order_id=order_id)
        self.data_thread.data_loaded.connect(self.on_order_data_loaded)
        self.data_thread.error_occurred.connect(self.on_order_load_error)
        self.data_thread.start()
        
        self.status_bar.showMessage(f"Загрузка данных заказа {order_id}...")
    
    def on_order_data_loaded(self, data):
        """Handle loaded order data"""
        order_data = data.get("all_order_data", {})
        
        # Update order info
        order_info = order_data.get("order_info", {})
        if order_info:
            self.order_info = order_info
            # Update order info labels
            self.order_name_label.setText(order_info.get("ORDER_NAME", "—"))
            self.order_number_label.setText(str(order_info.get("ORDERNO", "—")))
            self.order_date_label.setText(str(order_info.get("ORDERDATE", "—")))
            self.customer_name_label.setText(order_info.get("CUSTOMER_NAME", "—"))
            self.current_order_label.setText(str(self.current_order_id))
            
            # Update window title with order info
            order_number = order_info.get("ORDERNO", "")
            customer_name = order_info.get("CUSTOMER_NAME", "")
            if order_number:
                title = f"Group Change Params - Заказ №{order_number} ({customer_name})"
            else:
                title = f"Group Change Params - ID: {self.current_order_id} ({customer_name})"
            self.setWindowTitle(title)
        
        # Load order colors in color tab
        order_colors = order_data.get("order_colors", [])
        if hasattr(self.color_tab, 'on_order_colors_loaded'):
            self.color_tab.on_order_colors_loaded({"order_colors": order_colors})
        
        # Load stuffsets breeds in stuffsets breed tab
        if hasattr(self.stuffsets_breed_tab, 'load_stuffsets_breeds'):
            self.stuffsets_breed_tab.load_stuffsets_breeds(self.current_order_id)
        
        # Load adds breeds in breed tab
        if hasattr(self.breed_tab, 'load_adds_breeds'):
            self.breed_tab.load_adds_breeds(self.current_order_id)
        
        # Load stuffsets colors in stuffsets color tab
        if hasattr(self.stuffsets_color_tab, 'load_stuffsets_colors'):
            self.stuffsets_color_tab.load_stuffsets_colors(self.current_order_id)
        
        self.status_bar.showMessage(f"Загружены данные заказа {self.current_order_id}")
    
    def on_order_load_error(self, error_msg):
        """Handle order load error"""
        self.status_bar.showMessage("Ошибка загрузки заказа")
        QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные заказа: {error_msg}")
    
    def setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("Group Change Params - Групповое изменение параметров")
        
        # Set smaller window size
        self.setMinimumSize(1100, 800)
        self.resize(1100, 1000)
        
        # Center window on screen
        self.center_on_screen()
    
    def center_on_screen(self):
        """Center window on screen"""
        from PyQt5.QtWidgets import QDesktopWidget
        
        # Get screen geometry
        desktop = QDesktopWidget()
        screen_geometry = desktop.availableGeometry()
        
        # Get window geometry
        window_geometry = self.frameGeometry()
        
        # Calculate center position
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        
        # Move window to center
        self.move(window_geometry.topLeft())
    
    def create_menu_bar(self):
        """Create menu bar with Parameters menu"""
        menubar = self.menuBar()
        
        # Parameters menu
        params_menu = menubar.addMenu('Параметры')
        
        # Load order action
        load_order_action = QAction('Загрузить заказ...', self)
        load_order_action.setShortcut('Ctrl+O')
        load_order_action.setStatusTip('Загрузить данные заказа по ID')
        load_order_action.triggered.connect(self.show_load_order_dialog)
        params_menu.addAction(load_order_action)
        
        # Separator
        params_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Выйти из приложения')
        exit_action.triggered.connect(self.close)
        params_menu.addAction(exit_action)
    
    def show_load_order_dialog(self):
        """Show dialog to load order data"""
        dialog = LoadOrderDialog(self)
        if dialog.exec() == QDialog.Accepted:
            order_id = dialog.get_order_id()
            if order_id:
                self.load_order_data_by_id(order_id)
    
    def set_order_id(self, order_id: int):
        """Set order ID from command line argument"""
        self.load_order_data_by_id(order_id)  # Automatically load order data
    
    def closeEvent(self, event):
        """Handle close event"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Выход из программы")
        msg_box.setText("Вы действительно хотите закрыть программу?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Russian button text and styling
        yes_button = msg_box.button(QMessageBox.Yes)
        yes_button.setText("Да")
        yes_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        no_button = msg_box.button(QMessageBox.No)
        no_button.setText("Нет")
        no_button.setStyleSheet(DIALOG_BUTTON_STYLE)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
