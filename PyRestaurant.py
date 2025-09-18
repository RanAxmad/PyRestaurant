import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QListWidget, QLineEdit, QComboBox, QMessageBox, QSpinBox, QStyle, QTabWidget, QHBoxLayout
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
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_orders_tab(), "Orders")
        self.tab_widget.addTab(self.create_menu_tab(), "Menu Management")
        self.tab_widget.addTab(self.create_reports_tab(), "Reports")
        self.staff_layout.addWidget(self.tab_widget)
        self.staff_widget.setVisible(False)
        self.layout.addWidget(self.staff_widget)

        self.load_menu()

    def create_orders_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.orders_list = QListWidget()
        layout.addWidget(QLabel("Orders:"))
        layout.addWidget(self.orders_list)
        self.update_status_button = QPushButton("Update Status")
        self.update_status_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
        self.update_status_button.setToolTip("Update the selected order status")
        self.update_status_button.clicked.connect(self.update_order_status)
        layout.addWidget(self.update_status_button)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Preparing", "In Service", "Completed"])
        layout.addWidget(QLabel("New Status:"))
        layout.addWidget(self.status_combo)
        return widget

    def create_menu_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.staff_menu_list = QListWidget()
        layout.addWidget(QLabel("Current Menu:"))
        layout.addWidget(self.staff_menu_list)
        self.staff_menu_list.itemClicked.connect(self.select_menu_item)
        layout.addWidget(QLabel("Menu Management:"))
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Item Name:"))
        layout.addWidget(self.name_input)
        self.price_input = QLineEdit()
        layout.addWidget(QLabel("Price:"))
        layout.addWidget(self.price_input)
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Item")
        self.add_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.add_button.setToolTip("Add a new menu item")
        self.add_button.clicked.connect(self.add_menu_item)
        button_layout.addWidget(self.add_button)
        self.edit_button = QPushButton("Edit Item")
        self.edit_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        self.edit_button.setToolTip("Edit the selected menu item")
        self.edit_button.clicked.connect(self.edit_menu_item)
        button_layout.addWidget(self.edit_button)
        self.delete_button = QPushButton("Delete Item")
        self.delete_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.delete_button.setToolTip("Delete the selected menu item")
        self.delete_button.clicked.connect(self.delete_menu_item)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)
        return widget

    def create_reports_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.view_reports_button = QPushButton("View Reports")
        self.view_reports_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.view_reports_button.setToolTip("View sales reports")
        self.view_reports_button.clicked.connect(self.view_reports)
        layout.addWidget(self.view_reports_button)
        layout.addStretch()
        return widget

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
                order_id = cursor.lastrowid
                QMessageBox.information(self, "Order", f"Order placed for {quantity} x {name}. Total: {total} TL")
                self.load_orders()
                try:
                    from reportlab.pdfgen import canvas
                    from datetime import datetime
                    filename = f"receipt_{order_id}.pdf"
                    c = canvas.Canvas(filename)
                    c.drawString(100, 750, "PyRestaurant Receipt")
                    c.drawString(100, 730, f"Order ID: {order_id}")
                    c.drawString(100, 710, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    c.drawString(100, 690, f"Item: {name}")
                    c.drawString(100, 670, f"Quantity: {quantity}")
                    c.drawString(100, 650, f"Price per item: {price} TL")
                    c.drawString(100, 630, f"Total: {total} TL")
                    c.drawString(100, 600, "Thank you for your order!")
                    c.save()
                    QMessageBox.information(self, "Receipt", f"PDF generated as {filename}")
                except ImportError:
                    QMessageBox.warning(self, "Receipt", "ReportLab not installed, PDF not generated.")
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
                self.orders_list.addItem(f"Order ID: {order[0]}, Status: {order[3]}")

    def update_order_status(self):
        selected_order = self.orders_list.currentItem()
        if selected_order:
            order_id = int(selected_order.text().split(", ")[0].split(": ")[1])
            new_status = self.status_combo.currentText()
            cursor = self.conn.cursor()
            cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
            self.conn.commit()
            self.load_orders()
            QMessageBox.information(self, "Update", f"Status updated to {new_status}")
        else:
            QMessageBox.warning(self, "Warning", "Please select an order!")

    def select_menu_item(self, item):
        name = item.text().split(" - ")[0]
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM menu WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            self.selected_menu_id = result[0]
            self.name_input.setText(name)
            price = item.text().split(" - ")[1].replace(" TL", "")
            self.price_input.setText(price)

    def add_menu_item(self):
        name = self.name_input.text()
        price = self.price_input.text()
        if name and price:
            try:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, float(price)))
                self.conn.commit()
                self.load_menu()
                self.name_input.clear()
                self.price_input.clear()
                QMessageBox.information(self, "Success", "Item added to menu!")
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid price!")
        else:
            QMessageBox.warning(self, "Warning", "Enter name and price!")

    def edit_menu_item(self):
        if self.selected_menu_id is None:
            QMessageBox.warning(self, "Warning", "Select an item to edit!")
            return
        name = self.name_input.text()
        price = self.price_input.text()
        if name and price:
            try:
                cursor = self.conn.cursor()
                cursor.execute("UPDATE menu SET name = ?, price = ? WHERE id = ?", (name, float(price), self.selected_menu_id))
                self.conn.commit()
                self.load_menu()
                self.name_input.clear()
                self.price_input.clear()
                self.selected_menu_id = None
                QMessageBox.information(self, "Success", "Item updated!")
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid price!")
        else:
            QMessageBox.warning(self, "Warning", "Enter name and price!")

    def delete_menu_item(self):
        if self.selected_menu_id is None:
            QMessageBox.warning(self, "Warning", "Select an item to delete!")
            return
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM menu WHERE id = ?", (self.selected_menu_id,))
        self.conn.commit()
        self.load_menu()
        self.name_input.clear()
        self.price_input.clear()
        self.selected_menu_id = None
        QMessageBox.information(self, "Success", "Item deleted!")

    def view_reports(self):
        try:
            import matplotlib.pyplot as plt
            cursor = self.conn.cursor()
            cursor.execute("SELECT menu.name, SUM(orders.quantity) FROM orders JOIN menu ON orders.menu_id = menu.id GROUP BY menu.id")
            data = cursor.fetchall()
            if data:
                names = [row[0] for row in data]
                quantities = [row[1] for row in data]
                plt.bar(names, quantities)
                plt.title("Sales Report")
                plt.xlabel("Items")
                plt.ylabel("Quantity Sold")
                plt.show()
            else:
                QMessageBox.information(self, "Reports", "No orders yet!")
        except ImportError:
            QMessageBox.warning(self, "Error", "Matplotlib not installed!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RestaurantApp()
    window.show()
    sys.exit(app.exec())
