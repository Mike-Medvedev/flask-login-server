import pyodbc
import json
from sqlalchemy import create_engine
import sqlalchemy.pool as pool





def connect():
    connectionString = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:guitars.database.windows.net,1433;Database=store;Uid=CloudSA61792ed2;Pwd=vQLcu4zWvKTPgu2;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    conn = pyodbc.connect(connectionString)
    return conn

mypool = pool.QueuePool(connect, max_overflow=10, pool_size=10)


def connect_pool():
    conn = mypool.connect()
    return conn
    
def signup(data, bcrypt):
    username = data['username']
    password = data['password']
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    try:
        conn = connect_pool()
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
        conn = connect_pool()
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
        conn = connect_pool()
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
        conn = connect_pool()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guitars')
        result = cursor.fetchall()
        print(result)
        t_result = tuple(result)

        my_dict = dict({})

        guitar_list = [tuple(x) for x in result ]
        print(type(guitar_list))
        if not result:
            return json.dumps({"data": [], "message": "No records found"})

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
        
        conn = connect_pool()
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


def delete():
    delete_query = """
DELETE FROM guitars 
WHERE guitar_id = (SELECT MAX(guitar_id) FROM guitars)
"""
    try:
        conn = connect_pool()
        cursor = conn.cursor()
        cursor.execute(delete_query)

        conn.commit()

        return 'Deleted record successfully'
    except Exception as e:
        print('error deleting data', e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
def update(id, data):
    brand = data.get('brand', None)
    model = data.get('model', None)
    color = data.get('color', None)
    year = data.get('year', None)
    try:
        conn = connect_pool()
        cursor = conn.cursor()
        cursor.execute('UPDATE guitars SET brand=?, model=?, color=?, year=? WHERE guitar_id=?', (brand, model, color, year, id))

        cursor.commit()
        return json.dumps({"message": f'successfully updated record where id is {id}'})
    except Exception as e:
        print('error caught during updation: ', e)
        cursor.rollback()
        raise


    finally:
        cursor.close()
        conn.close()

def updateChanges(data):
    try:
        conn = connect_pool()
        cursor = conn.cursor()
        print('printing data: ', data)
        for record in data:
            _id = data[record].get('id', None)
            brand = data[record].get(f'brand-{record}', None)
            model = data[record].get(f'model-{record}', None)
            color = data[record].get(f'color-{record}', None)
            year = data[record].get(f'year-{record}', None)

            if _id:
                cursor.execute('UPDATE guitars SET brand=?, model=?, color=?, year=? WHERE guitar_id=?', (brand, model, color, year, _id))

            if not _id:
                cursor.execute('INSERT INTO guitars VALUES (?, ?, ?, ?)', (brand, model, color, year))    

        cursor.commit()
        return json.dumps({"message": f'successfully updated records'})
    except Exception as e:
        print('error caught during updation: ', e)
        cursor.rollback()
        raise


    finally:
        cursor.close()
        conn.close()