"""CREATE TABLE invitation_tokens (
	user_id INTEGER PRIMARY KEY NOT NULL,
	invitation_token TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id)
);"""

"""CREATE TABLE pages (
	id INTEGER PRIMARY KEY NOT NULL,
	uri TEXT NOT NULL
);"""

"""CREATE TABLE permit_view_page (
	user_id INTEGER NOT NULL,
	page_id INTEGER NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id),
	FOREIGN KEY (page_id) REFERENCES pages(id)
);"""

"""CREATE TABLE side_menu_items (
	id INTEGER PRIMARY KEY NOT NULL,
	name TEXT NOT NULL,
	parent_id INTEGER NOT NULL,
	page_id INTEGER NULL
);"""

"""CREATE TABLE user_authorization (
	user_id INTEGER NOT NULL,
	hashed_password TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id)
);"""
"""CREATE TABLE bpm (
	id INTEGER PRIMARY KEY NOT NULL,
	code TEXT NOT NULL,
	name TEXT NOT NULL,
	id_company INTEGER NOT NULL,
	id_owner INTEGER NULL,
	lvl INTEGER NOT NULL,
	id_parent INTEGER NULL,
	FOREIGN KEY (id_company) REFERENCES company(id),
	FOREIGN KEY (id_owner) REFERENCES users(id),
	FOREIGN KEY (id_parent) REFERENCES bpm(id)
);"""

"""CREATE TABLE types_documents (
	id INTEGER PRIMARY KEY NOT NULL AUTOINCREMENT,
	name TEXT NOT NULL UNIQUE,
	abv TEXT NOT NULL UNIQUE,
	layer TEXT CHECK(layer IN ('in', 'out')) NOT NULL
);"""

"""CREATE TABLE code_documents (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	id_bpm INTEGER NOT NULL,
	id_type_doc INTEGER NOT NULL,
	id_company INTEGER NOT NULL,
	number INTEGER NOT NULL,
	id_creator INTEGER NOT NULL,
	FOREIGN KEY (id_bpm) REFERENCES bpm(id),
	FOREIGN KEY (id_type_doc) REFERENCES types_documents(id),
	FOREIGN KEY (id_company) REFERENCES company(id),
	FOREIGN KEY (id_creator) REFERENCES users(id)
);"""
