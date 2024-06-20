import pyodbc
import json





def connect():
    connectionString = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:guitars.database.windows.net,1433;Database=store;Uid=CloudSA61792ed2;Pwd=vQLcu4zWvKTPgu2;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    conn = pyodbc.connect(connectionString)
    return conn
    
def signup(data, bcrypt):
    username = data['username']
    password = data['password']
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Customers (username, password) VALUES (?, ?)", (username, pw_hash))
        conn.commit()
        return json.dumps({"Message": "User registered successfully", "username": username})
        

    except pyodbc.IntegrityError as e:
        cursor.rollback()
        print(f"Integrity Error: {e}")
        raise 
    finally:
        cursor.close()
        conn.close()

def login(data, bcrypt):
    username=data['username']
    password=data['password']
    # pw_hash = bcrypt.generate_password_hash(password).encode('utf-8')
    print('entered username and password', username, password)
    
    try:
        conn = connect()
        cursor = conn.cursor()
        # Retrieve the stored password hash for the given username
        cursor.execute("SELECT password FROM Customers WHERE username=?", (username,))
        result = cursor.fetchone()
        if not result:
            raise ValueError('Username not found')

        t_result = tuple(result)
        stored_pw_hash = t_result[0]

        # Check the provided password against the stored hash
        if not bcrypt.check_password_hash(stored_pw_hash, password):
            raise ValueError('Incorrect password')
        conn.commit()
        return {"Message": "Username and password found", "username": username}
            
    except Exception as e:
        print(f"error as {e}")
        cursor.rollback()
        raise e
        

    finally:
        cursor.close()
        conn.close()

def get_users(user_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM Customers WHERE username=?', (user_id,))
        result = cursor.fetchone()
        print('stored used is; ', str(result))
        t_result = tuple(result)
        stored_id = t_result[0]
        print('stored used is; ', stored_id)
        if not result:
            raise ValueError('Error locating user data with given user_id: ', user_id)

        cursor.commit()
        return json.dumps({"message": stored_id})
    except Exception as e:
        cursor.rollback()
        print('error caught: ', e)
        raise
    finally:
        cursor.close()
        conn.close()

def get_guitars():
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('SELECT brand, model, color, year FROM guitars')
        result = cursor.fetchall()
        print(result)
        t_result = tuple(result)

        my_dict = dict({})

        guitar_list = [tuple(x) for x in result ]
        print(type(guitar_list))
        if not result:
            raise ValueError('Error getting guitar data')

        cursor.commit()
        return json.dumps({"data": guitar_list})
    except Exception as e:
        cursor.rollback()
        print('error caught: ', e)
        raise
    finally:
        cursor.close()
        conn.close()

def create_guitar(data):
    brand = data.get('brand', None)
    model = data.get('model', None)
    color = data.get('color', None)
    year = data.get('year', None)

    print(data)
    
    try:
        
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO guitars (brand, model, color, year) VALUES (?, ?, ?, ?)', (brand, model, color, year, ))


        cursor.commit()
        return json.dumps({"Message": "successfully inserted data"})
    except Exception as e:
        cursor.rollback()
        print('error caught: ', e)
        raise
    finally:
        cursor.close()
        conn.close()