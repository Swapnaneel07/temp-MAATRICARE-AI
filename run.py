import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import init_db
from ml_pipeline import train_model
from seed_data import seed_demo_data
from app import app
import os

if __name__ == '__main__':
    print('MaatriCare AI - Initializing...')
    init_db()
    print('Training ML model...')
    train_model()
    # Only seed if DB is fresh
    from database import query_db
    if not query_db('SELECT COUNT(*) as c FROM patients', one=True)['c']:
        print('Seeding demo data...')
        seed_demo_data()
    print('Starting MaatriCare AI on http://localhost:5000')
    app.run(debug=True, port=5000)
