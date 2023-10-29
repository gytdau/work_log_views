import sqlite3
import re
import os
from tqdm import tqdm

import re
import os
from tqdm import tqdm
from db import Database
from views import ViewRunner

ALWAYS_REFRESH_FIRST_N_BLOCKS = 3
ONLY_FIRST_N_BLOCKS = 15


class MarkdownBlockProcessor:
    def __init__(self):
        self.db = Database()

    def process_file(self, file_path):
        """Process the given markdown file and extract blocks."""
        with open(file_path, "r") as f:
            content = f.read()

        # Split by headers, assuming headers are denoted with '#' at the start
        blocks = re.split(r"\n(?=#+ .+\n)", content)

        blocks = blocks[:ONLY_FIRST_N_BLOCKS]

        new_blocks = []

        for i, block in enumerate(blocks):
            # Split block into header and content
            header, content = re.split(r"\n", block, 1)
            header = header.strip()
            content = content.strip()

            if header.startswith("# "):
                continue

            inserted = self.db.insert_block(header, content)

            if i < ALWAYS_REFRESH_FIRST_N_BLOCKS or inserted:
                new_block = (header, content)
                new_blocks += [new_block]

        return new_blocks

    def close(self):
        """Close the database connection."""
        self.db.close()


def main():
    markdown_file = "/Users/gytis/Library/Mobile Documents/27N4MQEA55~pro~writer/Documents/Work Log.txt"
    # markdown_file = "./work_log.md"

    if not os.path.exists(markdown_file):
        print(f"File '{markdown_file}' not found.")
        return

    processor = MarkdownBlockProcessor()

    try:
        new_blocks = processor.process_file(markdown_file)
        ViewRunner().run(new_blocks)
    finally:
        processor.close()


if __name__ == "__main__":
    main()
