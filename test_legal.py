from run import app
from app.models.db import init_db

init_db(app)

with app.test_client() as client:
    response = client.get('/legal')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        if b"legal-container" in response.data:
            print("Page loaded successfully.")
        else:
            print("Page loaded but missing legal container class.")
    else:
        print("Failed to load page.")
