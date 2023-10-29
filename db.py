import sqlite3


class Database:
    def __init__(self, db_path="blocks.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        """Create the blocks table if it doesn't exist."""
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS blocks (
                    id INTEGER PRIMARY KEY,
                    header TEXT UNIQUE,
                    content TEXT
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transformed_blocks (
                    id INTEGER PRIMARY KEY,
                    header TEXT,
                    content TEXT,
                    view TEXT
                )
                """
            )
            self.conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS header_view_idx ON transformed_blocks (header, view)
            """
            )

    def insert_block(self, header, content):
        """Insert a block into the database if the header doesn't already exist."""
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO blocks (header, content) VALUES (?, ?)",
                    (header, content),
                )
            return True
        except sqlite3.IntegrityError:  # header already exists
            return False

    def insert_transformed_block(self, header, content, view):
        """Insert a block into the database if the header doesn't already exist."""
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO transformed_blocks (header, content, view) VALUES (?, ?, ?)",
                    (header, content, view),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def insert_or_update_transformed_block(self, header, content, view):
        """Insert a block into the database if the header doesn't already exist."""
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO transformed_blocks (header, content, view) VALUES (?, ?, ?)",
                    (header, content, view),
                )
            return True
        except sqlite3.IntegrityError:
            with self.conn:
                self.conn.execute(
                    "UPDATE transformed_blocks SET content = ? WHERE header = ? AND view = ?",
                    (content, header, view),
                )
            return True

    def get_transformed_blocks(self, view):
        """Get all transformed blocks for the given view."""
        with self.conn:
            return self.conn.execute(
                "SELECT * FROM transformed_blocks WHERE view = ?", (view,)
            ).fetchall()

    def close(self):
        """Close the database connection."""
        self.conn.close()
