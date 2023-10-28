import sqlite3
import re
import os


class MarkdownBlockProcessor:
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

    def process_file(self, file_path):
        """Process the given markdown file and extract blocks."""
        with open(file_path, "r") as f:
            content = f.read()

        # Split by headers, assuming headers are denoted with '#' at the start
        blocks = re.split(r"\n(?=#+ .+\n)", content)

        new_blocks = []

        for block in blocks:
            # Split block into header and content
            header, content = re.split(r"\n", block, 1)
            header = header.strip()
            content = content.strip()

            if self.insert_block(header, content):
                new_blocks.append((header, content))

        return new_blocks

    def close(self):
        """Close the database connection."""
        self.conn.close()


def process_new_blocks(blocks):
    """Placeholder function to extend processing for new blocks."""
    for header, content in blocks:
        print(f"Header: {header}\nContent:\n{content}\n\n")
        # TODO: Further processing here if needed


def main():
    markdown_file = "/Users/gytis/Library/Mobile Documents/27N4MQEA55~pro~writer/Documents/Work Log.txt"

    if not os.path.exists(markdown_file):
        print(f"File '{markdown_file}' not found.")
        return

    processor = MarkdownBlockProcessor()

    try:
        new_blocks = processor.process_file(markdown_file)
        if new_blocks:
            print("New blocks found:")
            process_new_blocks(new_blocks)
        else:
            print("No new blocks found.")
    finally:
        processor.close()


if __name__ == "__main__":
    main()
