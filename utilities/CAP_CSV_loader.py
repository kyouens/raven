# IMPORTANT!!
# The .xls files from CAP must be converted into .xlsx files before running this script.

import os
import pandas as pd
import sqlite3
from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    print("Generating encryption key...")
    print(f"Save encryption key in an environmental variable: {key}")
    return Fernet(key)

def init_db():
    print("Initializing database...")
    conn = sqlite3.connect("./sources/SQLite/encrypted_checklist_data.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS checklist_data")
    c.execute('''CREATE TABLE IF NOT EXISTS checklist_data (Source TEXT, Content TEXT)''')
    conn.commit()
    print("Database initialized.")
    return c, conn

def get_excel_files(directory_path='./sources/original/'):
    print("Scanning for Excel files...")
    files = [f for f in os.listdir(directory_path) if f.endswith('.xlsx')]
    print(f"Found {len(files)} Excel files.")
    return files

def process_file(file_path):
    print(f"Processing file: {file_path}")
    df = pd.read_excel(file_path, header=None)
    # ... (rest of your function)

def insert_into_db(cursor, conn, source, content, cipher_suite):
    print(f"Inserting data into database for source: {source}")
    encrypted_content = cipher_suite.encrypt(content.encode())
    cursor.execute("INSERT INTO checklist_data (Source, Content) VALUES (?, ?)", (source, encrypted_content))
    conn.commit()

def process_file(file_path):
    print(f"Processing file: {file_path}")
    df = pd.read_excel(file_path, header=None)
    
    # Read cell B2
    cell_B2 = df.at[1, 1]

    # Drop the first 6 rows
    df = df.iloc[6:].reset_index(drop=True)
    
    # Rename columns
    df.columns = [
        "Source", "Procedure Required", "Phase",
        "Title", "Requirement", "Note", "Evidence of Compliance"
    ]

    # Create DataFrame for markdown export (SQLite)
    df_md = df[['Source']].copy()
    
    def concatenate_md_content(row):
        sections = []
        sections.append(f"### Checklist\n{cell_B2}")
        if not pd.isna(row['Title']):
            sections.append(f"### Subject\n{row['Title']}")
        sections.append("### Procedure Required") 
        if not pd.isna(row['Procedure Required']):
            sections.append("Yes")
        else:
            sections.append("No")
        if not pd.isna(row['Phase']):
            sections.append(f"### Phase\n{row['Phase']}")
        if not pd.isna(row['Requirement']):
            sections.append(f"### Requirement\n{row['Requirement']}")
        if not pd.isna(row['Note']):
            sections.append(f"### Note\n{row['Note']}")
        if not pd.isna(row['Evidence of Compliance']):
            sections.append(f"### Evidence of Compliance\n{row['Evidence of Compliance']}")
        return '\n\n'.join(sections)
    
    df_md['Content'] = df.apply(concatenate_md_content, axis=1)
    
    # Create DataFrame for CSV export
    df_csv = df[['Source']].copy()
    
    def concatenate_csv_content(row):
        sections = []
        sections.append(f"### Checklist\n{cell_B2}")
        if not pd.isna(row['Title']):
            sections.append(f"### Subject\n{row['Title']}")
        if not pd.isna(row['Requirement']):
            sections.append(f"### Requirement\n{row['Requirement']}")
        if not pd.isna(row['Note']):
            sections.append(f"### Note\n{row['Note']}")
        if not pd.isna(row['Evidence of Compliance']):
            sections.append(f"### Evidence of Compliance\n{row['Evidence of Compliance']}")
        return '\n\n'.join(sections)
    
    df_csv['Content'] = df.apply(concatenate_csv_content, axis=1)
    
    return df_md, df_csv

def insert_into_db(cursor, conn, source, content, cipher_suite):
    encrypted_content = cipher_suite.encrypt(content.encode())
    cursor.execute("INSERT INTO checklist_data (Source, Content) VALUES (?, ?)", (source, encrypted_content))
    conn.commit()

def main():
    print("Starting main execution...")
    cipher_suite = generate_key()
    c, conn = init_db()
    
    excel_files = get_excel_files()
    
    print("Processing Excel files...")
    all_data_csv = []
    all_data_md = []
    
    for excel_file in excel_files:
        file_path = os.path.join('./sources/original/', excel_file)
        df_md, df_csv = process_file(file_path)
        all_data_md.append(df_md)
        all_data_csv.append(df_csv)
        
    print("Combining all data...")
    combined_data_md = pd.concat(all_data_md, ignore_index=True)
    combined_data_csv = pd.concat(all_data_csv, ignore_index=True)
    
    print("Inserting data into SQLite database...")
    for _, row in combined_data_md.iterrows():
        insert_into_db(c, conn, row['Source'], row['Content'], cipher_suite)
        
    print("Closing database connection...")
    conn.close()
    
    print("Exporting to CSV...")
    combined_data_csv.to_csv('./sources/temp/temporary_checklist_data_ready.csv')
    
    print("Script execution completed.")

if __name__ == "__main__":
    main()
