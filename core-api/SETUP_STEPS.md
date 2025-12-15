# Quick Setup Steps for PowerShell

## Step 1: Navigate to core-api directory
```powershell
cd core-api
```

## Step 2: Create virtual environment (if it doesn't exist)
```powershell
python -m venv venv
```

## Step 3: Activate virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

**Note:** If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Step 4: Install dependencies
```powershell
pip install -r requirements.txt
```

## Step 5: Run database migrations
```powershell
alembic upgrade head
```

## Step 6: (Optional) Seed mock data
```powershell
python scripts/seed_mock_trips.py
```

## Step 7: Start the server
```powershell
uvicorn app.main:app --reload
```

## Troubleshooting

**If `alembic` is not recognized:**
- Make sure you activated the virtual environment (Step 3)
- You should see `(venv)` at the start of your PowerShell prompt

**If you get execution policy errors:**
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Then try activating again

**If Python is not found:**
- Make sure Python 3.10+ is installed
- Try `python3` instead of `python`

