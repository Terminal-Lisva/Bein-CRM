
query = """CREATE TABLE invitation_tokens (
	user_id INTEGER PRIMARY KEY NOT NULL,
	invitation_token TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id)
);"""
query = """CREATE TABLE pages (
	id INTEGER PRIMARY KEY NOT NULL,
	uri TEXT NOT NULL
);"""
query = """CREATE TABLE permit_view_page (
	user_id INTEGER NOT NULL,
	page_id INTEGER NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id),
	FOREIGN KEY (page_id) REFERENCES pages(id)
);"""
query = """CREATE TABLE side_menu_items (
	id INTEGER PRIMARY KEY NOT NULL,
	name TEXT NOT NULL,
	parent_id INTEGER NOT NULL,
	page_id INTEGER NULL
);"""
query = """CREATE TABLE user_authorization (
	user_id INTEGER NOT NULL,
	hashed_password TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id)
);"""


