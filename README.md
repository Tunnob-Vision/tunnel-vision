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
pytest tests/ --cov=. --cov-report=term-missing
```

**Generate HTML coverage report:**

```bash
pytest tests/ --cov=. --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## 5) Deployment

The app is deployed and running at: **https://tunnel-vision.streamlit.app**

## Python 3.10 — Environment Setup (Team)

This project targets Python 3.10 to ensure compatibility with packages such as `mediapipe`. Below are concise, copyable instructions for getting a Python 3.10 environment on different systems and for making a reproducible team setup.

**Windows — winget (recommended)**

```powershell
winget install --id=Python.Python.3.10 -e
# then create venv explicitly with that interpreter
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version  # should show 3.10.x
```

**Create / Activate a venv (copyable commands)**

- PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- Command Prompt:

```cmd
py -3.10 -m venv .venv
.venv\Scripts\activate.bat
```

- macOS / Linux:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```
