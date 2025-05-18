import sqlite3

def get_db():
	db = sqlite3.connect("database/database.db", check_same_thread=False)
	try:
		yield db
	finally:
		db.close()

def create_tables(db):
	create_users_table(db)
	create_sessions_table(db)

def create_users_table(db):
	cur = db.cursor()
	cur.execute(
		"""
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL
		)
		""")
	db.commit()

def create_sessions_table(db):
	cur = db.cursor()
	cur.execute(
		"""
		CREATE TABLE IF NOT EXISTS sessions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id INTEGER NOT NULL,
			token TEXT NOT NULL UNIQUE,
			expires_at DATETIME NOT NULL,
			FOREIGN KEY(user_id) REFERENCES users(id)
		)
		""")
	db.commit()
