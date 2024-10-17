import sqlite3

def init_db():
    conn = sqlite3.connect('alerts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            cryptocurrency TEXT NOT NULL,
            warning_price REAL NOT NULL,
            price_condition TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
def save_response(chat_id, cryptocurrency, warning_price, price_condition):
    conn = sqlite3.connect('alerts.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts (chat_id, cryptocurrency, warning_price, price_condition)
        VALUES (?, ?, ?, ?)
    ''', (chat_id, cryptocurrency, warning_price, price_condition))
    conn.commit()
    conn.close()

def get_all_alerts():
    conn = sqlite3.connect('alerts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, chat_id, cryptocurrency, warning_price, price_condition FROM alerts")
    alerts = cursor.fetchall()
    conn.close()
    alert_list = []
    for alert in alerts:
        alert_list.append({
            'id': alert[0],
            'chat_id': alert[1],
            'cryptocurrency': alert[2],
            'warning_price': alert[3],
            'price_condition': alert[4]
        })
    return alert_list

def delete_alert(alert_id):
    conn = sqlite3.connect('alerts.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
