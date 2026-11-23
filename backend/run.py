import sys
import os

# app modülünün bulunabilmesi için backend yolunu sisteme ekliyoruz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)