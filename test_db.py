import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))
database_id = os.getenv("NOTION_DATABASE_ID")

try:
    response = notion.databases.retrieve(database_id=database_id)
    print("--- Database Properties ---")
    for name, props in response.get("properties", {}).items():
        print(f"Property Name: '{name}' | Type: {props['type']}")
        
    print("\n--- Database Pages / Rows ---")
    pages = notion.databases.query(database_id=database_id)
    for page in pages.get("results", []):
        props = page.get("properties", {})
        print(props)
except Exception as e:
    print(f"Error connecting to Notion: {e}")