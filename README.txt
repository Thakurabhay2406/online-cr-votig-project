# CR Voting (Flask) — Step by Step

1) Install Python 3 and VS Code.
2) Open this folder in VS Code.
3) Open Terminal in VS Code.
4) Create virtual env:
   - Windows:  python -m venv venv && venv\Scripts\activate
   - macOS/Linux:  python -m venv venv && source venv/bin/activate
5) Install packages:  pip install -r requirements.txt
6) Run the app:  python app.py
7) Open browser: http://127.0.0.1:5000
   - Vote page: /
   - Results: /results
   - Add candidate: /admin/add?key=letmein
8) Change admin key in app.py (ADMIN_KEY).
9) To reset data, stop the app and delete voting.db, then run again.
