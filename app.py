from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from setup import datagen
import openai
import sqlite3
import os

app = Flask(__name__)
app.secret_key = '*z*3$ufo0i=fg+7el)7tcrpzgxa=qvins6p2(ni0x8x@k7)8e'    

@app.route('/', methods=['GET', 'POST'])
def home():
    get_gen_data = None  # Initialize the variable to handle cases where no data is generated
    if request.method == 'POST':
        # Check if the form field 'text_name' is not empty
        if 'text_name' in request.form and request.form['text_name'].strip():
            req_text = request.form['text_name'].strip()
            location = request.form['location'].strip()
            print(location)
            notification_type = "hospital"  # response from ISis system. 
            if notification_type in ['police', 'hospital', 'fire_station', 'others']:
                add_notification(location, notification_type, 'user-info')  # user-info is device info

            # get_gen_data = datagen(req_text)  # api key is not working...
            insert_data_to_db(req_text, str(get_gen_data))
            flash('Data successfully generated!', 'success')
        else:
            flash('Please enter valid text.', 'error')
    loaddata = save_data_load()
    return render_template('index.html', query=get_gen_data,showdata=loaddata)

def save_data_load():
    # Connect to SQLite database
    conn = sqlite3.connect('isi_solution.db')
    cursor = conn.cursor()

    # Select top 6 questions based on counter
    cursor.execute('''
        SELECT * FROM user_question_bank
        ORDER BY counter DESC
        LIMIT 6
    ''')

    # Fetch and print the result
    rows = cursor.fetchall()
    return rows

@app.route('/chat', methods=['GET'])
def chat():
    user_message ="Health information request in barcelona"
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    # Initialize messages with system context
    messages = [{"role": "system", "content": "Eres un asistente muy útil."}]


    # Append user's message to the messages list
    messages.append({"role": "user", "content": user_message})

    try:
        # Check if the user_message already exists in the database
        # response_content = check_user_message_in_db(user_message)
        response_content = ''
        if not response_content:
            # If the response is not found in the database, call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-1106",
                messages=messages
            )

            # Extract the response content from the API response
            response_content = response.choices[0].message.content

            # Insert data into the database
                            
            insert_data_to_db(response_content, user_message)

            # Return the assistant's response
        return response_content

    except openai.error.OpenAIError as e:
        # Handle OpenAI API errors
        return f"Error al llamar a la API de OpenAI: {e}"

def check_user_message_in_db(user_message):
    conn = sqlite3.connect('isi_solution.db') 
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, counter, response
        FROM user_question_bank
        WHERE user_question = ?;
    ''', (user_message,))

    result = cursor.fetchone()

    if result:
        # If user_message exists, update the counter and get the response
        record_id, counter, response = result

        # Ensure that counter is not None before performing the addition
        counter = int(counter) + 1 

        cursor.execute('''
            UPDATE user_question_bank
            SET counter = ?
            WHERE id = ?;
        ''', (counter, record_id))
    conn.commit()
    conn.close()

    return response if result else None

def insert_data_to_db(response_content, user_message):
    conn = sqlite3.connect('isi_solution.db') 
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_question_bank ( user_question, response)
        VALUES (?, ?)
    ''', (user_message, response_content))

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('isi_solution.db') 
    conn.row_factory = sqlite3.Row
    return conn

# @app.route('/add_notification/<location>/<notification_type>/<user_info>', methods=['POST'])
def add_notification(location, notification_type, user_info):
    query = """
    INSERT INTO notification (location, notification_type, user_info) 
    VALUES (?, ?, ?);
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, (location, notification_type, user_info))
        conn.commit()
    except sqlite3.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'status': 'success'}), 201



if __name__ == '__main__':
    app.run(debug=True)
