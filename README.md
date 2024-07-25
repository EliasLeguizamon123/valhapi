# VALHALLA API

## Description
Valhapi is an API developed with FastAPI. This project includes instructions for setting up and running the API on a Windows environment.

## Requirements
- Python 3.11 or higher
- Git
- [PyInstaller](https://www.pyinstaller.org/)
- [FastAPI](https://fastapi.tiangolo.com)

## Installation

### Install the project

```bash
git clone https://github.com/EliasLeguizamon123/valhapi.git
cd valhapi
```


```bash
python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt | pip install fastapi uvicorn pyinstaller
```

### Run project

```bash
uvicorn app.main:app --reload

```