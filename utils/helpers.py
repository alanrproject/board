import datetime

def format_date(date_str):
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return date.strftime("%d/%m/%Y")

def fetch_data_from_db(query):
    # Lógica para obtener datos de la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
