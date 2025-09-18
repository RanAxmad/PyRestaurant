import sqlite3

def create_connection(db_file):
    """ SQLite veritabanı bağlantısı oluşturur """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ Menü ve sipariş tablolarını oluşturur """
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
                status TEXT NOT NULL DEFAULT 'Hazırlanıyor',
                FOREIGN KEY (menu_id) REFERENCES menu (id)
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)
