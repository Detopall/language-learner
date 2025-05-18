import sqlite3

def add_session_token(db, user_id, token, expires_at):
	cur = db.cursor()
	cur.execute("INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)", (user_id, token, expires_at))
	db.commit()

def get_session_token_from_user(db, username, password):
	cur = db.cursor()
	cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
	user = cur.fetchone()

	if user:
		cur.execute("SELECT * FROM sessions WHERE user_id = ?", (user[0],))
		session = cur.fetchone()
		return session

	return None

def delete_session_token(db, token):
	cur = db.cursor()
	cur.execute("DELETE FROM sessions WHERE token = ?", (token,))
	db.commit()

def update_session_token(db, token, expires_at):
	cur = db.cursor()
	cur.execute("UPDATE sessions SET expires_at = ? WHERE token = ?", (expires_at, token))
	db.commit()
