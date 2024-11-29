CREATE TABLE person (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	birthday DATE, 
	PRIMARY KEY (id)
);

CREATE TABLE relationship (
	id INTEGER NOT NULL, 
	person1_id INTEGER NOT NULL, 
	person2_id INTEGER NOT NULL, 
	relationship_type VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(person1_id) REFERENCES person (id), 
	FOREIGN KEY(person2_id) REFERENCES person (id)
);

