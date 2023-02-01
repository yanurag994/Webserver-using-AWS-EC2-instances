from flask import Flask, request, redirect, render_template, send_from_directory, url_for
import hashlib, sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='.')
app.config['UPLOAD_FOLDER'] = "/home/ubuntu/flaskapp/upload_file"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

conn = sqlite3.connect(':memory:',check_same_thread=False)
cur = conn.cursor()
cur.execute("""DROP TABLE IF EXISTS natlpark""")
cur.execute("""CREATE TABLE natlpark
            (FirstName text, LastName text, email text, username text, password text,filename text,cnt integer)""")
conn.commit()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def front_page():
    return render_template('index.html') #redirects to login screen or registration screen based on buttons

@app.route('/login')
def login_form():
    return render_template('login.html') #login screen asking for user credentials like username and password

@app.route('/login', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    hashed_password = hashlib.sha256(password).hexdigest()
    query = "SELECT FirstName,LastName,email,username,filename,cnt FROM natlpark WHERE username = ? AND password = ?"
    result = cur.execute(query, (username, hashed_password)).fetchone()
    conn.commit()
    if result:
        return render_template('details.html', result=result) #navigate to screen which will display major user details
    else:
        return 'Invalid Login'

@app.route('/details/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/registration')
def registration_form():
    return render_template('registration.html') #registration page with all fields like username, password, firstname, lastnane, email

@app.route('/registration', methods=['POST'])
def registration_submit():
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    hashed_password = hashlib.sha256(password).hexdigest()
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    file_form= request.files["file"]
    if not all([username, password, firstname, lastname, email]):
        return 'Invalid input. All fields are required.'
    try:
        if file_form and allowed_file(file_form.filename):
            filename = secure_filename(file_form.filename)
            cnt=len(file_form.read().split())
            file_form.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename=None
            cnt=0
        cur.execute("""INSERT INTO natlpark VALUES (?,?,?,?,?,?,?)""",(firstname,lastname,email,username,hashed_password,filename,cnt))
        conn.commit()
    except Exception as e:
        print(e)
        return "Error inserting data into database: {}",format(e)
    # Store the data in database or process it as desired.
    return redirect(url_for("login_submit"),code=307)

if __name__ == '__main__':
    app.run()
