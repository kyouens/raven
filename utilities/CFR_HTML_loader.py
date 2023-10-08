import html2text
import re
import sqlite3
import pandas as pd
from cryptography.fernet import Fernet


def generate_key():
    key = Fernet.generate_key()
    print("Generating encryption key...")
    print(f"Save encryption key in an environmental variable: {key}")
    return Fernet(key)


def init_db():
    print("Initializing database...")
    conn = sqlite3.connect("./sources/SQLite/encrypted_regulatory_data.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS regulatory_data")
    c.execute('''CREATE TABLE IF NOT EXISTS regulatory_data (Source TEXT, Content TEXT)''')
    conn.commit()
    print("Database initialized.")
    return c, conn


def insert_into_db(cursor, conn, source, content, cipher_suite):
    print(f"Inserting data into database for source: {source}")
    encrypted_content = cipher_suite.encrypt(content.encode())
    cursor.execute("INSERT INTO regulatory_data (Source, Content) VALUES (?, ?)", (source, encrypted_content))
    conn.commit()


def process_document(html_content):
    markdown_content = html2text.html2text(html_content)

    internal_link_pattern = r'\[([^\]]+)\]\(\/[^\)]+\)'
    cleaned_content = re.sub(internal_link_pattern, r'\1', markdown_content)

    multiline_headline_pattern = r'^(#+ [^\n]+)\n([^\n]+)\n\n'
    fixed_content = re.sub(multiline_headline_pattern, r'\1 \2\n\n', cleaned_content, flags=re.M)

    h2_text, h3_text = None, None

    def process_match(match):
        nonlocal h2_text, h3_text
        level = match.group(1)
        text = match.group(2)

        if level == "#":
            return "##### Example" if text == "Example" else ""
        elif level == "##":
            h2_text = text
        elif level == "###":
            h3_text = text
        elif level == "####":
            return f"# {text}\n_In {h2_text}_. _Topic: {h3_text}_"
        
        return match.group(0)

    segmented_content = re.sub(r'^(#+) ([^\n]+)', process_match, fixed_content, flags=re.M)

    segmented_content = re.sub(r'^#+\s*\n', '', segmented_content, flags=re.M)
    authority_source_pattern = r'# (Authority|Source):.*?(?=(# |\Z))'
    segmented_content = re.sub(authority_source_pattern, '', segmented_content, flags=re.S | re.M)
    cross_reference_pattern = r'(###### Cross Reference)'
    segmented_content = re.sub(cross_reference_pattern, r'> **Cross Reference**', segmented_content)
    three_lines_after_cross_ref = re.compile(r'(?<=\> \*\*Cross Reference\*\*\n)((?:.*\n){3})')
    segmented_content = re.sub(three_lines_after_cross_ref, lambda m: '> ' + '> '.join(m.group(1).splitlines(True)), segmented_content)

    segments = re.split(r'(?=^# [^\n]+\n)', segmented_content, flags=re.M)

    csv_data = [("Source", "Content")]
    for segment in segments:
        match = re.match(r'^# ([^\n]+)\n', segment, flags=re.M)
        if match:
            source = match.group(1)
            content = segment[len(match.group(0)):].strip()
            csv_data.append((source, content))

    return csv_data


def main():
    print("Starting main execution...")
    cipher_suite = generate_key()
    c, conn = init_db()

    print("Processing HTML file...")
    with open("sources/original/title-42.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    csv_data = process_document(html_content)

    print("Inserting data into SQLite database...")
    for source, content in csv_data[1:]:
        insert_into_db(c, conn, source, content, cipher_suite)

    print("Closing database connection...")
    conn.close()

    print("Exporting to CSV...")
    df = pd.DataFrame(csv_data[1:], columns=csv_data[0])
    df.to_csv('./sources/temp/temporary_regulatory_data_ready.csv', index=False)

    print("Script execution completed.")


if __name__ == "__main__":
    main()
