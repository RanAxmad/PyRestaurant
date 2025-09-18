import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QListWidget, QLineEdit, QComboBox, QMessageBox, QSpinBox
from PyQt6.QtCore import Qt
import database

class RestaurantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyRestaurant Management System")
        self.setGeometry(100, 100, 800, 600)

        self.conn = database.create_connection("restaurant.db")
        if self.conn:
            database.create_tables(self.conn)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.title_label = QLabel("Welcome to PyRestaurant!")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.interface_label = QLabel("Select Interface:")
        self.layout.addWidget(self.interface_label)

        self.interface_combo = QComboBox()
        self.interface_combo.addItems(["Customer", "Staff/Manager"])
        self.interface_combo.currentTextChanged.connect(self.switch_interface)
        self.layout.addWidget(self.interface_combo)

        self.customer_widget = QWidget()
        self.customer_layout = QVBoxLayout(self.customer_widget)
        self.menu_list = QListWidget()
        self.customer_layout.addWidget(QLabel("Menu:"))
        self.customer_layout.addWidget(self.menu_list)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.customer_layout.addWidget(QLabel("Quantity:"))
        self.customer_layout.addWidget(self.quantity_spin)
        self.order_button = QPushButton("Place Order")
        self.order_button.clicked.connect(self.place_order)
        self.customer_layout.addWidget(self.order_button)
        self.customer_widget.setVisible(False)
        self.layout.addWidget(self.customer_widget)

        self.staff_widget = QWidget()
        self.staff_layout = QVBoxLayout(self.staff_widget)
        self.orders_list = QListWidget()
        self.staff_layout.addWidget(QLabel("Orders:"))
        self.staff_layout.addWidget(self.orders_list)
        self.update_status_button = QPushButton("Update Status")
        self.update_status_button.clicked.connect(self.update_order_status)
        self.staff_layout.addWidget(self.update_status_button)
        self.staff_widget.setVisible(False)
        self.layout.addWidget(self.staff_widget)

        self.load_menu()

    def switch_interface(self, interface):
        if interface == "Customer":
            self.customer_widget.setVisible(True)
            self.staff_widget.setVisible(False)
        elif interface == "Staff/Manager":
            self.customer_widget.setVisible(False)
            self.staff_widget.setVisible(True)
            self.load_orders()

    def load_menu(self):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name, price FROM menu")
            items = cursor.fetchall()
            self.menu_list.clear()
            for item in items:
                self.menu_list.addItem(f"{item[0]} - {item[1]} TL")

    def place_order(self):
        selected_item = self.menu_list.currentItem()
        if selected_item:
            QMessageBox.information(self, "Sipariş", f"Sipariş verildi: {selected_item.text()}")
            # Burada sipariş veritabanına ekleme kodu eklenecek
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir yemek seçin!")

    def load_orders(self):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, menu_id, quantity, status FROM orders")
            orders = cursor.fetchall()
            self.orders_list.clear()
            for order in orders:
                self.orders_list.addItem(f"Sipariş ID: {order[0]}, Durum: {order[3]}")

    def update_order_status(self):
        selected_order = self.orders_list.currentItem()
        if selected_order:
            QMessageBox.information(self, "Güncelleme", f"Durum güncellendi: {selected_order.text()}")
            # Burada durum güncelleme kodu eklenecek
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir sipariş seçin!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RestaurantApp()
    window.show()
    sys.exit(app.exec())
