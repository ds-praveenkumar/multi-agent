import sqlite3
import pandas as pd
from rich.console import Console
from rich.markdown import Markdown
console = Console()

def query_db(query):
  conn = sqlite3.connect('telco.db')
  try:
    return pd.read_sql_query(query, conn)
  finally:
    conn.close()

def display_text(text):
    markdown = Markdown( text )
    console.print(markdown)