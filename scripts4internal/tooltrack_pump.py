from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL database configuration
db_config = {
    'host': 'your_mysql_host',
    'user': 'your_mysql_user',
    'password': 'your_mysql_password',
    'database': 'your_mysql_database',
}

# Establish a connection to the MySQL database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Endpoint to handle HTTP payload and update MySQL database
@app.route('/update_database', methods=['POST'])
def update_database():
    try:
        # Parse JSON payload
        data = request.get_json()

        # Extract relevant data from the payload
        # Modify this section based on the structure of your payload
        user_id = data.get('user_id')
        new_value = data.get('new_value')

        # Update MySQL database
        update_query = "UPDATE your_table SET column_name = %s WHERE user_id = %s"
        cursor.execute(update_query, (new_value, user_id))
        conn.commit()

        return jsonify({'status': 'success', 'message': 'Database updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
