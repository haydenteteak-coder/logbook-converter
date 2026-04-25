# logbook_converter

This is a very simple local Streamlit app that converts an airline schedule CSV into one single ForeFlight-compatible import CSV.

The app lets you:

- upload one airline schedule CSV
- preview the converted flights table
- preview the aircraft table
- download one final ForeFlight import CSV file

## 1. Install Python

If you do not already have Python installed:

1. Go to https://www.python.org/downloads/
2. Download Python 3
3. Run the installer
4. Make sure you check the box that says `Add Python to PATH`

## 2. Open the project in VS Code

Open this folder in VS Code:

`log-book-converter`

## 3. Install dependencies

Open the VS Code terminal and run:

```bash
py -m pip install -r requirements.txt
```

## 4. Run the app

In the same terminal, run:

```bash
py -m streamlit run app.py
```

Streamlit will open the app in your browser.

## 5. Deploy to Streamlit Community Cloud

This repo is already set up for Streamlit Community Cloud with:

- pinned Python dependencies in `requirements.txt`
- project config in `.streamlit/config.toml`
- a single app entrypoint at `app.py`

### What you need to do

1. Create a GitHub repository for this folder.
2. Push this project to GitHub.
3. Sign in to `https://share.streamlit.io/`.
4. Connect your GitHub account to Streamlit Community Cloud.
5. Click `Create app`.
6. Select your GitHub repository, branch, and the entrypoint file `app.py`.
7. In `Advanced settings`, choose Python `3.12`.
8. Click `Deploy`.

After the first deploy, every new push to GitHub will automatically update the app.

### Suggested first push commands

If you have not created a git repo for this folder yet:

```bash
git init -b main
git add .
git commit -m "Prepare logbook converter for deployment"
```

After you create the empty GitHub repository, connect it and push:

```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

### Notes for a public app

- users will upload schedule CSV files to the app server for conversion
- the app itself does not save uploaded CSV files to disk, but you should still avoid hosting sensitive data you would not want processed on a cloud service
- if you want to restrict access, deploy from a private GitHub repo and configure the app as private in Streamlit Community Cloud

## Required input columns

Your airline CSV must include these columns:

- `Date`
- `A/C Type`
- `Tail`
- `Origin`
- `Dest`
- `Block`

If any of these columns are missing, the app will show an error message and list the missing columns.

## Conversion rules used

The app uses these conversion rules:

- `TotalTime = Block`
- `SIC = Block`
- `PIC = blank`
- `CrossCountry = Block`
- `MultiPilot = Block`
- `Date` is normalized to `YYYY-MM-DD` for ForeFlight
- `Depart -> TimeOut`
- `Arrive -> TimeIn`
- `TimeOff` and `TimeOn` stay blank because they are not included in the source CSV
- each kept flight row gets:
- `Takeoff Day = 1`
- `Landing Full-Stop Day = 1`
- `Flight` and `Credit` are added to `PilotComments`
- crew members are exported into ForeFlight `Person1` through `Person6`
- `Captain -> Person`
- `First Officer -> Person`
- `Flight Attendant -> one or more Person fields`
- crew employee numbers are preserved in the person name as `Name (EmployeeID)`
- aircraft type mapping:
- `CR2 -> CRJ2`
- `CR5 -> CRJ5`
- `CR7 -> CRJ7`
- `CR9 -> CRJ9`
- `E75 / E175 / ERJ175 / ERJ 175 -> E175`
- known CRJ aircraft are exported with:
- `equipType = aircraft`
- `Make = Bombardier / Embraer`
- `Model = CRJ200 / CRJ550 / CRJ700 / CRJ900 / ERJ175`
- `GearType = RT`
- `EngineType = Turbofan`
- `Category/Class = AMEL`
- `complexAircraft = true`
- `highPerformance = true`
- `pressurized = true`
- `taa = true`
- `Year` stays blank because it is not included in the input CSV
- if `Tail` is blank, that row is skipped
- all night and instrument fields are left blank
- flights are not combined
- the aircraft table is auto-built from retained flights
- aircraft rows are deduplicated by `AircraftID + TypeCode`
- `Category/Class = AMEL` for all aircraft rows

## Optional source columns used when present

If your airline CSV includes these columns, the converter now uses them:

- `Flight`
- `Depart`
- `Arrive`
- `Credit`
- `Captain`
- `First Officer`
- `Flight Attendant`

## Output

The output is one single CSV file for ForeFlight import.

It includes:

1. the required `ForeFlight Logbook Import` row
2. the Aircraft Table section
3. the Flights Table section

## Files in this project

- `app.py` - the Streamlit app interface
- `converter.py` - the CSV conversion logic and ForeFlight export builder
- `requirements.txt` - the Python packages you need
- `.streamlit/config.toml` - project config for Streamlit deployment
- `.gitignore` - files to keep out of the Git repo
- `README.md` - setup and usage instructions
