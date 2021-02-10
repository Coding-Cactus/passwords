import flask, os, uuid, hashlib, base64, random
from easypydb import DB

app = flask.Flask(__name__)
app.secret_key = os.getenv('secretKey')
session = flask.session

dbToken = os.getenv('dbToken')
loginDB = DB('loginDB', dbToken)
userDB = DB('users', dbToken)


def hash_password(password):
	salt = uuid.uuid4().hex
	return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
    
def check_password(hashed_password, user_password):
	password, salt = hashed_password.split(':')
	return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

def decode(encoded):
	toString = lambda encoded: ''.join(''.join(encoded.split("b'")[1:]).split("'")[:-1])
	return toString(str(base64.b64decode(toString(encoded).encode())))

@app.route('/')
def main():
	if 'user' in session:
		return flask.render_template('index.html', loggedIn=True, session=session, db=userDB[session['user']], decode=lambda a:decode(a))
	else:
		return flask.render_template('index.html', loggedIn=False)

@app.route('/signup')
def getSignupPage():
	return flask.render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
	username = flask.request.form['username']
	password1 = flask.request.form['password1']
	password2 = flask.request.form['password2']
	if username in loginDB.data:
		return flask.render_template('signup.html', error='Already a user with that name.')	
	elif len(username) < 2:
		return flask.render_template('signup.html', error='Username needs to be at least 2 characters long')
	elif len(password1) < 6:
		return flask.render_template('signup.html', error='Password needs to be at least 6 characters long')
	elif password1 != password2:
		return flask.render_template('signup.html', error='Passwords did not match')
	else:
		loginDB[username] = hash_password(password1)
		userDB[username] = {}
		session['user'] = username
		session.modified = True
		return flask.redirect('/')



@app.route('/login')
def getLoginPage():
	return flask.render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
	username = flask.request.form['username']
	password = flask.request.form['password']

	if username not in loginDB.data:
		return flask.render_template('login.html', error='Incorrect username or password.')
	
	elif check_password(loginDB[username], password):
		session['user'] = username
		session.modified = True
		return flask.redirect('/')
	
	else:
		return flask.render_template('login.html', error='Incorrect username or password.')


@app.route('/add')
def getAddPage():
	if 'user' in session:
		return flask.render_template('add.html', db=userDB[session['user']], url='/add', button='add')
	else:
		return flask.redirect('/')

@app.route('/add', methods=['POST'])
def add():
	if 'user' in session:
		name = flask.request.form['name']
		password = flask.request.form['password']

		db = userDB[session['user']]

		biggest = 0
		for i in db:
			if int(i) > biggest:
				biggest = int(i)
		encoded = str(base64.b64encode(password.encode()))
		db[str(biggest+1)] = {'name':name, 'password':encoded}
		userDB[session['user']] = db
		return flask.redirect('/')
	else:
		return flask.redirect('/')


@app.route('/remove/<id>')
def remove(id):
	if 'user' in session:
		db = userDB[session['user']]
		if id in db:
			del db[id]
			userDB[session['user']] = db
			return flask.redirect('/')
		else:
			return flask.redirect('/')
	else:
		return flask.redirect('/')


@app.route('/edit/<id>')
def getEditPage(id):
	if 'user' in session:
		stuff = userDB[session['user']]
		if id in stuff:
			stuff = stuff[id]
			return flask.render_template('add.html', name=stuff['name'], password=decode(stuff['password']), url='/edit/'+id, button='edit')
	else:
		return flask.redirect('/')


@app.route('/edit/<id>', methods=['POST'])
def edit(id):
	if 'user' in session:
		name = flask.request.form['name']
		password = flask.request.form['password']
		stuff = userDB[session['user']]
		if id in stuff:
			stuff[id] = {'name':name, 'password':str(base64.b64encode(password.encode()))}
		userDB[session['user']] = stuff
	return flask.redirect('/')



@app.route('/logout')
def logout():
	if 'user' in session:
		session.pop('user', None)
	return flask.redirect('/')


@app.route('/random')
def randomPassword():
	args = flask.request.args
	if 'length' in args:
		try:
			length = int(args['length'])
		except ValueError:
			length = 20
	else:
		length = 20

	password = ''
	for i in range(length):
		password += chr(random.randint(65,122))

	return password


@app.route('/favicon.ico')
def favicon():
	return flask.send_file('favicon.ico')

app.run('0.0.0.0')