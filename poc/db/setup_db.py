import sqlite3
import os

# Pfad zur Datenbankdatei
db_path = './poc/db/produkte.db'

# Überprüfen, ob die Datenbankdatei existiert
if not os.path.exists(db_path):
    # Erstellen der Datenbankdatei
    open(db_path, 'w').close()

    # Verbindung zur SQLite-Datenbank herstellen (wird erstellt, wenn sie nicht existiert)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabelle erstellen
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produkte (
        product_number INTEGER PRIMARY KEY,
        input_voltage INTEGER,
        input_current INTEGER,
        output_voltage INTEGER,
        output_current INTEGER,
        number_io_ports INTEGER,
        bus_protocol TEXT
    )
    ''')

    # Add example data
    cursor.execute('''
    INSERT INTO produkte (product_number, input_voltage, input_current, output_voltage, output_current, number_io_ports, bus_protocol)
    VALUES
    (1, 24, 2, 24, 2, 4, 'Modbus TCP'),
    (2, 12, 1, 24, 2, 2, 'Modbus RTU'),
    (3, 17, 2, 12, 1, 4, 'Profinet'),
    (4, 12, 1, 12, 1, 2, 'Ethernet/IP')
    ''')

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()
else:
    print("Datenbank existiert bereits.")
