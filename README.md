# Tunnel Vision - Quick Start

## 1) Create a virtual environment

- Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

- Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

- Windows (Git Bash):
```bash
python -m venv venv
source venv/Scripts/activate
```

- macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

To deactivate later:
```bash
deactivate
```

## 2) Install dependencies
```bash
pip install -r requirements.txt
```

## 3) Run the Streamlit app
```bash
streamlit run app.py
```

## 4) Run tests

**Without coverage:**
```bash
pytest tests/
```

**With coverage report:**
```bash
pytest tests/ --cov=utils --cov-report=term-missing
```

**Generate HTML coverage report:**
```bash
pytest tests/ --cov=utils --cov-report=html
```
Then open `htmlcov/index.html` in your browser.
