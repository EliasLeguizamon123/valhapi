# VALHALLA API

## Description
Valhapi is an API developed with FastAPI. This project includes instructions for setting up and running the API on a Windows environment.

> [!NOTE]  
> This project currently only works on Windows OS for the database URL, but Im working on changing this.


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

pip install -r requirements.txt || pip install fastapi uvicorn pyinstaller
```

### Run project

```bash
uvicorn app.main:app --reload  || python -m uvicorn app.main:app --reload

```

### Docs

Just go to the following URL to see the API documentation:

```bash
http://127.0.0.1:8000/docs
```

### Build 

for build this project you need to check first if you venv is activated, then you can run the following command:

```bash
pyinstaller --clean valhapi.spec
```
