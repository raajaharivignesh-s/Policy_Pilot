import asyncio
import sys
import os

# Add backend directory to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath("c:\\Users\\rajah\\OneDrive\\Desktop\\Policy-Pilot\\backend"))

from app.services.search_service import search_service

def test_search():
    try:
        print("Testing search...")
        results = search_service.search("test query")
        print(f"Success! Found {len(results)} results.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
