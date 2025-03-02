from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self._employee_id = employee_id  # Initialize the private variable
        self.id = id
        self.year = year
        self.summary = summary
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        if not isinstance(employee_id, int):
            raise ValueError("Employee ID must be an integer.")
        # Check if the employee_id exists in the database
        from employee import Employee  # Local import to avoid circular dependency
        if Employee.find_by_id(employee_id) is None:
            raise ValueError("Employee ID does not exist.")
        self._employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self): 
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        if not isinstance(self.year, int):
            raise ValueError("Year must be an integer.")
        if self.year < 2000:
            raise ValueError("Year must be greater than or equal to 2000.")
        if not isinstance(self.summary, str) or len(self.summary) == 0:
            raise ValueError("Summary must be a non-empty string.")
        if not isinstance(self.employee_id, int):
            raise ValueError("Employee ID must be an integer.")
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        self.id = CURSOR.lastrowid
        Review.all[self.id] = self
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id): 
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        if not isinstance(year, int):
            raise ValueError("Year must be an integer.")
        if year < 2000:
            raise ValueError("Year must be greater than or equal to 2000.")
        if not isinstance(summary, str) or len(summary) == 0:
            raise ValueError("Summary must be a non-empty string.")
        if not isinstance(employee_id, int):
            raise ValueError("Employee ID must be an integer.")
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        if row[0] in cls.all:
            return cls.all[row[0]]
        review = cls(row[1], row[2], row[3], row[0])
        cls.all[row[0]] = review
        return review

        """Return an Review instance having the attribute values from the table row."""
        if row[0] in cls.all:
            return cls.all[row[0]]
        review = cls(row[1], row[2], row[3], row[0])
        cls.all[row[0]] = review
        return review
   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        del Review.all[self.id]
        self.id = None
        CONN.commit()

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
