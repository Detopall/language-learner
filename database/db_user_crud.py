import sqlite3
import bcrypt

def add_user(db, username, password):
	hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
	cur = db.cursor()
	cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
	db.commit()
	return get_user(db, username)

def get_user(db, username):
	cur = db.cursor()
	cur.execute("SELECT * FROM users WHERE username = ?", (username,))
	return cur.fetchone()

def delete_user(db, username):
	cur = db.cursor()
	cur.execute("DELETE FROM users WHERE username = ?", (username,))
	db.commit()

def update_user(db, username, password):
	hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
	cur = db.cursor()
	cur.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
	db.commit()

def verify_user_password(plain_password, hashed_password):
	return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
