import openai
import dotenv
import os

from tqdm import tqdm
from db import Database

dotenv.load_dotenv()  # Load the .env file containing the OpenAI API key

openai.api_key = os.getenv("OPENAI_API_KEY")

OUTPUT_DIR = "log_views"


class InsightsView:
    def process(self, header, content, db: Database):
        prompt = "---\nAbove is a work log. Discarding all irrelevant content, extract the information relating to a markdown list of long-term goals, insights, or ideas. Quote the relevant extracts and reproduce them exactly.\n\nIf there is nothing to extract, write 'None'.\n\n "

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content + prompt},
            ],
        )

        new_content = response.choices[0].message.content

        db.insert_or_update_transformed_block(header, new_content, "insights")

    def output_file(self, db):
        with open(f"{OUTPUT_DIR}/insights.md", "w") as f:
            f.write("# Insights\n\n")
            for row in db.get_transformed_blocks("insights"):
                f.write(f"{row[1]}\n\n")
                f.write(f"{row[2]}\n\n")


class TimeView:
    def process(self, header, content, db: Database):
        prompt = """Above is a work log. Discarding all irrelevant content, exact the time log related information, such as information on what was being done and when. Include the time and duration of the event in the standard format:

**XX:XXpm (X hours)** - "event"

If the hours cannot be inferred, write your best guess instead.

Quote the relevant extracts and reproduce them exactly."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content + prompt},
            ],
        )

        new_content = response.choices[0].message.content

        db.insert_or_update_transformed_block(header, new_content, "time")

    def output_file(self, db):
        with open(f"{OUTPUT_DIR}/time.md", "w") as f:
            f.write("# Time\n\n")
            for row in db.get_transformed_blocks("time"):
                f.write(f"{row[1]}\n\n")
                f.write(f"{row[2]}\n\n")


class ViewRunner:
    def __init__(self):
        self.db = Database()

    def run(self, blocks):
        views = [InsightsView(), TimeView()]
        for header, content in tqdm(blocks):
            for view in views:
                view.process(header, content, self.db)

        for view in views:
            view.output_file(self.db)
