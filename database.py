import sqlite3

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                menu_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Preparing',
                FOREIGN KEY (menu_id) REFERENCES menu (id)
            )
        ''')
        # Performans için indeksler ekle
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_menu_name ON menu (name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_menu_id ON orders (menu_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status)')
        conn.commit()
    except sqlite3.Error as e:
        print(e)
