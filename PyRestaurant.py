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
        self.selected_menu_id = None

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
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Preparing", "In Service", "Completed"])
        self.staff_layout.addWidget(QLabel("New Status:"))
        self.staff_layout.addWidget(self.status_combo)
        self.staff_menu_list = QListWidget()
        self.staff_layout.addWidget(QLabel("Current Menu:"))
        self.staff_layout.addWidget(self.staff_menu_list)
        self.staff_menu_list.itemClicked.connect(self.select_menu_item)
        self.staff_layout.addWidget(QLabel("Menu Management:"))
        self.name_input = QLineEdit()
        self.staff_layout.addWidget(QLabel("Item Name:"))
        self.staff_layout.addWidget(self.name_input)
        self.price_input = QLineEdit()
        self.staff_layout.addWidget(QLabel("Price:"))
        self.staff_layout.addWidget(self.price_input)
        self.add_button = QPushButton("Add Item")
        self.add_button.clicked.connect(self.add_menu_item)
        self.staff_layout.addWidget(self.add_button)
        self.edit_button = QPushButton("Edit Item")
        self.edit_button.clicked.connect(self.edit_menu_item)
        self.staff_layout.addWidget(self.edit_button)
        self.delete_button = QPushButton("Delete Item")
        self.delete_button.clicked.connect(self.delete_menu_item)
        self.staff_layout.addWidget(self.delete_button)
        self.view_reports_button = QPushButton("View Reports")
        self.view_reports_button.clicked.connect(self.view_reports)
        self.staff_layout.addWidget(self.view_reports_button)
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
            if hasattr(self, 'staff_menu_list'):
                self.staff_menu_list.clear()
                for item in items:
                    self.staff_menu_list.addItem(f"{item[0]} - {item[1]} TL")

    def place_order(self):
        selected_item = self.menu_list.currentItem()
        if selected_item:
            quantity = self.quantity_spin.value()
            name = selected_item.text().split(" - ")[0]
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, price FROM menu WHERE name = ?", (name,))
            item = cursor.fetchone()
            if item:
                menu_id, price = item
                total = quantity * price
                cursor.execute("INSERT INTO orders (menu_id, quantity) VALUES (?, ?)", (menu_id, quantity))
                self.conn.commit()
                QMessageBox.information(self, "Order", f"Order placed for {quantity} x {name}. Total: {total} TL")
                self.load_orders()
                try:
                    from reportlab.pdfgen import canvas
                    c = canvas.Canvas("receipt.pdf")
                    c.drawString(100, 750, "Receipt")
                    c.drawString(100, 730, f"Order: {quantity} x {name}")
                    c.drawString(100, 710, f"Total: {total} TL")
                    c.save()
                    QMessageBox.information(self, "Receipt", "PDF generated as receipt.pdf")
                except ImportError:
                    pass
            else:
                QMessageBox.warning(self, "Error", "Item not found!")
        else:
            QMessageBox.warning(self, "Warning", "Please select a dish!")

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
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir sipariş seçin!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RestaurantApp()
    window.show()
    sys.exit(app.exec())
