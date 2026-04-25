import csv
import io
import re

import pandas as pd


AIRCRAFT_MAP = {
    "CR2": "CRJ2",
    "CR5": "CRJ5",
    "CR7": "CRJ7",
    "CR9": "CRJ9",
    "E75": "E175",
    "E175": "E175",
    "ERJ175": "E175",
    "ERJ 175": "E175",
    "ERJ-175": "E175",
    "EMB175": "E175",
    "EMBRAER175": "E175",
}

AIRCRAFT_DETAILS_MAP = {
    "CRJ2": {
        "equipType": "aircraft",
        "Make": "Bombardier",
        "Model": "CRJ200",
        "GearType": "RT",
        "EngineType": "Turbofan",
        "Category/Class": "AMEL",
        "complexAircraft": "true",
        "highPerformance": "true",
        "pressurized": "true",
        "taa": "true",
    },
    "CRJ5": {
        "equipType": "aircraft",
        "Make": "Bombardier",
        "Model": "CRJ550",
        "GearType": "RT",
        "EngineType": "Turbofan",
        "Category/Class": "AMEL",
        "complexAircraft": "true",
        "highPerformance": "true",
        "pressurized": "true",
        "taa": "true",
    },
    "CRJ7": {
        "equipType": "aircraft",
        "Make": "Bombardier",
        "Model": "CRJ700",
        "GearType": "RT",
        "EngineType": "Turbofan",
        "Category/Class": "AMEL",
        "complexAircraft": "true",
        "highPerformance": "true",
        "pressurized": "true",
        "taa": "true",
    },
    "CRJ9": {
        "equipType": "aircraft",
        "Make": "Bombardier",
        "Model": "CRJ900",
        "GearType": "RT",
        "EngineType": "Turbofan",
        "Category/Class": "AMEL",
        "complexAircraft": "true",
        "highPerformance": "true",
        "pressurized": "true",
        "taa": "true",
    },
    "E175": {
        "equipType": "aircraft",
        "Make": "Embraer",
        "Model": "ERJ175",
        "GearType": "RT",
        "EngineType": "Turbofan",
        "Category/Class": "AMEL",
        "complexAircraft": "true",
        "highPerformance": "true",
        "pressurized": "true",
        "taa": "true",
    },
}

REQUIRED_COLUMNS = ["Date", "A/C Type", "Tail", "Origin", "Dest", "Block"]
PERSON_COLUMNS = [f"Person{index}" for index in range(1, 7)]
PILOT_ROLE_COLUMNS = ["Captain", "First Officer"]
CREW_SOURCE_COLUMNS = [
    ("Captain", "PIC"),
    ("First Officer", "First Officer"),
    ("Flight Attendant", "Flight Attendant"),
]
CREW_ENTRY_PATTERN = re.compile(
    r"(?P<employee_id>\d{4,})\s+(?P<name>.*?)(?=(?:\s+\d{4,}\s+)|$)"
)

AIRCRAFT_TYPE_ROW = [
    "Text",
    "Text",
    "Text",
    "YYYY",
    "Text",
    "Text",
    "Text",
    "Text",
    "Text",
    "Boolean",
    "Boolean",
    "Boolean",
    "Boolean",
]

AIRCRAFT_HEADER_ROW = [
    "AircraftID",
    "equipType",
    "TypeCode",
    "Year",
    "Make",
    "Model",
    "GearType",
    "EngineType",
    "Category/Class",
    "complexAircraft",
    "highPerformance",
    "pressurized",
    "taa",
]

FLIGHT_TYPE_ROW = [
    "Date",
    "Text",
    "Text",
    "Text",
    "Text",
    "HH:MM",
    "HH:MM",
    "HH:MM",
    "HH:MM",
    "HH:MM",
    "HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Number",
    "Decimal",
    "Number",
    "Number",
    "Number",
    "Number",
    "Number",
    "Number",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal",
    "Decimal",
    "Decimal",
    "Decimal",
    "Number",
    "Packed Detail",
    "Packed Detail",
    "Packed Detail",
    "Packed Detail",
    "Packed Detail",
    "Packed Detail",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Decimal or HH:MM",
    "Text",
    "Text",
    "Packed Detail",
    "Packed Detail",
    "Packed Detail",
    "Packed Detail",
    "Packed Detail",
    "Packed Detail",
    "Text",
    "Boolean",
    "Boolean",
    "Boolean",
    "Boolean",
    "Boolean",
    "Text",
    "Decimal",
    "Decimal or HH:MM",
    "Number",
    "Date",
    "DateTime",
    "Boolean",
]

FLIGHT_HEADER_ROW = [
    "Date",
    "AircraftID",
    "From",
    "To",
    "Route",
    "TimeOut",
    "TimeOff",
    "TimeOn",
    "TimeIn",
    "OnDuty",
    "OffDuty",
    "TotalTime",
    "PIC",
    "SIC",
    "Night",
    "Solo",
    "CrossCountry",
    "PICUS",
    "MultiPilot",
    "IFR",
    "Examiner",
    "NVG",
    "NVGOps",
    "Distance",
    "Takeoff Day",
    "Takeoff Night",
    "Landing Full-Stop Day",
    "Landing Full-Stop Night",
    "Landing Touch-and-Go Day",
    "Landing Touch-and-Go Night",
    "ActualInstrument",
    "SimulatedInstrument",
    "GroundTraining",
    "GroundTrainingGiven",
    "HobbsStart",
    "HobbsEnd",
    "TachStart",
    "TachEnd",
    "Holds",
    "Approach1",
    "Approach2",
    "Approach3",
    "Approach4",
    "Approach5",
    "Approach6",
    "DualGiven",
    "DualReceived",
    "SimulatedFlight",
    "InstructorName",
    "InstructorComments",
    "Person1",
    "Person2",
    "Person3",
    "Person4",
    "Person5",
    "Person6",
    "PilotComments",
    "Flight Review",
    "IPC",
    "Checkride",
    "FAA 61.58",
    "NVG Proficiency",
    "[Text]CustomFieldName",
    "[Numeric]CustomFieldName",
    "[Hours]CustomFieldName",
    "[Counter]CustomFieldName",
    "[Date]CustomFieldName",
    "[DateTime]CustomFieldName",
    "[Toggle]CustomFieldName",
]


class MissingColumnsError(Exception):
    def __init__(self, missing_columns):
        self.missing_columns = missing_columns
        super().__init__(
            "Missing required columns: " + ", ".join(missing_columns)
        )


def _blank_flight_row():
    return {column: "" for column in FLIGHT_HEADER_ROW}


def _clean_text(value):
    if value is None:
        return ""

    if pd.isna(value):
        return ""

    return str(value).strip()


def _format_foreflight_date(date_text):
    cleaned_date = _clean_text(date_text)
    if not cleaned_date:
        return ""

    parsed_date = pd.to_datetime(cleaned_date, format="%m/%d/%Y", errors="coerce")
    if pd.isna(parsed_date):
        parsed_date = pd.to_datetime(cleaned_date, errors="coerce")

    if pd.isna(parsed_date):
        return cleaned_date

    return parsed_date.strftime("%Y-%m-%d")


def _format_foreflight_time(time_text):
    cleaned_time = _clean_text(time_text)
    if not cleaned_time:
        return ""

    time_match = re.match(r"^(?P<hours>\d{1,2}):(?P<minutes>\d{2})$", cleaned_time)
    if time_match:
        return (
            f"{int(time_match.group('hours')):02d}:"
            f"{time_match.group('minutes')}"
        )

    parsed_time = pd.to_datetime(cleaned_time, errors="coerce")
    if pd.isna(parsed_time):
        return cleaned_time

    return parsed_time.strftime("%H:%M")


def _default_aircraft_details():
    return {
        "equipType": "aircraft",
        "Make": "",
        "Model": "",
        "GearType": "",
        "EngineType": "",
        "Category/Class": "AMEL",
        "complexAircraft": "true",
        "highPerformance": "true",
        "pressurized": "true",
        "taa": "true",
    }


def _normalize_person_name(name):
    return re.sub(r"\s+", " ", _clean_text(name).upper())


def _build_crew_member_key(crew_member):
    employee_id = _clean_text(crew_member.get("employee_id", ""))
    if employee_id:
        return f"id:{employee_id}"

    normalized_name = _normalize_person_name(crew_member.get("name", ""))
    if normalized_name:
        return f"name:{normalized_name}"

    return ""


def _build_crew_member_label(crew_member):
    name = _clean_text(crew_member.get("name", ""))
    employee_id = _clean_text(crew_member.get("employee_id", ""))
    if not name:
        return ""

    if employee_id:
        return f"{name} ({employee_id})"

    return name


def _normalize_aircraft_type_key(aircraft_type):
    return re.sub(r"[^A-Z0-9]+", "", _clean_text(aircraft_type).upper())


def _map_aircraft_type(aircraft_type):
    cleaned_type = _clean_text(aircraft_type)
    if not cleaned_type:
        return ""

    return AIRCRAFT_MAP.get(
        cleaned_type,
        AIRCRAFT_MAP.get(_normalize_aircraft_type_key(cleaned_type), cleaned_type),
    )


def _parse_crew_members(crew_text):
    cleaned_crew = re.sub(r"\s+", " ", _clean_text(crew_text))
    if not cleaned_crew:
        return []

    crew_members = []
    for match in CREW_ENTRY_PATTERN.finditer(cleaned_crew):
        name = _clean_text(match.group("name"))
        if not name:
            continue

        crew_members.append(
            {
                "employee_id": _clean_text(match.group("employee_id")),
                "name": name,
            }
        )

    if crew_members:
        return crew_members

    return [{"employee_id": "", "name": cleaned_crew}]


def _matches_user_identifier(crew_member, user_identifier):
    cleaned_identifier = _clean_text(user_identifier)
    if not cleaned_identifier:
        return False

    employee_id = _clean_text(crew_member.get("employee_id", ""))
    if employee_id and cleaned_identifier == employee_id:
        return True

    normalized_identifier = _normalize_person_name(cleaned_identifier)
    normalized_name = _normalize_person_name(crew_member.get("name", ""))

    if not normalized_name:
        return False

    return (
        normalized_identifier == normalized_name
        or normalized_identifier in normalized_name
    )


def _summarize_pilot_candidates(source_df):
    pilot_candidates = {}

    for column in PILOT_ROLE_COLUMNS:
        if column not in source_df.columns:
            continue

        for crew_text in source_df[column]:
            for crew_member in _parse_crew_members(crew_text):
                candidate_key = _build_crew_member_key(crew_member)
                if not candidate_key:
                    continue

                if candidate_key not in pilot_candidates:
                    pilot_candidates[candidate_key] = {
                        "key": candidate_key,
                        "name": _clean_text(crew_member.get("name", "")),
                        "employee_id": _clean_text(
                            crew_member.get("employee_id", "")
                        ),
                        "label": _build_crew_member_label(crew_member),
                        "count": 0,
                    }

                pilot_candidates[candidate_key]["count"] += 1

    return pilot_candidates


def _resolve_logged_pilot(source_df, user_identifier=""):
    pilot_candidates = _summarize_pilot_candidates(source_df)
    if not pilot_candidates:
        return {
            "key": "",
            "label": "",
            "source": "auto",
            "matched": False,
            "ambiguous": False,
            "options": [],
        }

    cleaned_identifier = _clean_text(user_identifier)
    if cleaned_identifier:
        manual_matches = [
            candidate
            for candidate in pilot_candidates.values()
            if _matches_user_identifier(candidate, cleaned_identifier)
        ]

        if manual_matches:
            selected_candidate = max(
                manual_matches,
                key=lambda candidate: (
                    candidate["count"],
                    candidate["label"],
                ),
            )
            return {
                "key": selected_candidate["key"],
                "label": selected_candidate["label"],
                "source": "manual",
                "matched": True,
                "ambiguous": False,
                "options": [],
            }

        return {
            "key": "",
            "label": cleaned_identifier,
            "source": "manual",
            "matched": False,
            "ambiguous": False,
            "options": [],
        }

    highest_count = max(
        candidate["count"] for candidate in pilot_candidates.values()
    )
    top_candidates = [
        candidate
        for candidate in pilot_candidates.values()
        if candidate["count"] == highest_count
    ]

    if len(top_candidates) > 1:
        return {
            "key": "",
            "label": "",
            "source": "auto",
            "matched": False,
            "ambiguous": True,
            "options": sorted(candidate["label"] for candidate in top_candidates),
        }

    selected_candidate = top_candidates[0]
    return {
        "key": selected_candidate["key"],
        "label": selected_candidate["label"],
        "source": "auto",
        "matched": True,
        "ambiguous": False,
        "options": [],
    }


def _determine_logged_role(row, logged_pilot):
    if logged_pilot.get("matched"):
        for crew_member in _parse_crew_members(row.get("Captain", "")):
            if _build_crew_member_key(crew_member) == logged_pilot["key"]:
                return "PIC"

        for crew_member in _parse_crew_members(row.get("First Officer", "")):
            if _build_crew_member_key(crew_member) == logged_pilot["key"]:
                return "SIC"

    return "SIC"


def _sanitize_packed_detail(value):
    return _clean_text(value).replace(";", ",")


def _build_person_detail(name, role, employee_id=""):
    display_name = _sanitize_packed_detail(name)
    if employee_id:
        display_name = f"{display_name} ({employee_id})"

    return ";".join([display_name, _sanitize_packed_detail(role), ""])


def _collect_crew_people(row):
    people = []
    for source_column, role_name in CREW_SOURCE_COLUMNS:
        for crew_member in _parse_crew_members(row.get(source_column, "")):
            if not crew_member["name"]:
                continue

            packed_detail = _build_person_detail(
                crew_member["name"],
                role_name,
                crew_member["employee_id"],
            )
            overflow_label = crew_member["name"]
            if crew_member["employee_id"]:
                overflow_label = f"{overflow_label} ({crew_member['employee_id']})"

            people.append(
                {
                    "packed_detail": packed_detail,
                    "overflow_label": f"{overflow_label} - {role_name}",
                }
            )

    return people


def _build_pilot_comments(row, overflow_people):
    comment_parts = []

    flight_number = _clean_text(row.get("Flight", ""))
    if flight_number:
        comment_parts.append(f"Flight {flight_number}")

    credit = _clean_text(row.get("Credit", ""))
    if credit:
        comment_parts.append(f"Credit {credit}")

    if overflow_people:
        comment_parts.append(
            "Additional crew not exported: " + ", ".join(overflow_people)
        )

    return " | ".join(comment_parts)


def convert_schedule(uploaded_file, user_identifier=""):
    uploaded_file.seek(0)
    source_df = pd.read_csv(uploaded_file, dtype=str).fillna("")

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in source_df.columns
    ]
    if missing_columns:
        raise MissingColumnsError(missing_columns)

    working_df = source_df.copy()
    columns_to_strip = [
        "Flight",
        "Date",
        "A/C Type",
        "Tail",
        "Origin",
        "Dest",
        "Depart",
        "Arrive",
        "Block",
        "Credit",
        "Captain",
        "First Officer",
        "Flight Attendant",
    ]
    for column in columns_to_strip:
        if column in working_df.columns:
            working_df[column] = working_df[column].astype(str).str.strip()

    input_rows = len(working_df)
    logged_pilot = _resolve_logged_pilot(working_df, user_identifier)

    # Rows without a tail number are skipped completely.
    retained_df = working_df[working_df["Tail"] != ""].copy()
    retained_df["MappedTypeCode"] = retained_df["A/C Type"].apply(_map_aircraft_type)

    flight_rows = []
    pic_rows = 0
    sic_rows = 0
    for index, row in retained_df.reset_index(drop=True).iterrows():
        flight_row = _blank_flight_row()
        flight_row["Date"] = _format_foreflight_date(row["Date"])
        flight_row["AircraftID"] = row["Tail"]
        flight_row["From"] = row["Origin"]
        flight_row["To"] = row["Dest"]
        flight_row["TimeOut"] = _format_foreflight_time(row.get("Depart", ""))
        flight_row["TimeIn"] = _format_foreflight_time(row.get("Arrive", ""))
        flight_row["TotalTime"] = row["Block"]
        flight_row["CrossCountry"] = row["Block"]
        flight_row["MultiPilot"] = row["Block"]

        logged_role = _determine_logged_role(row, logged_pilot)
        if logged_role == "PIC":
            flight_row["PIC"] = row["Block"]
            pic_rows += 1
        else:
            flight_row["SIC"] = row["Block"]
            sic_rows += 1

        # Mark every other kept leg with one takeoff and one landing.
        if index % 2 == 0:
            flight_row["Takeoff Day"] = "1"
            flight_row["Landing Full-Stop Day"] = "1"

        crew_people = _collect_crew_people(row)
        overflow_people = []
        for person_column, person in zip(PERSON_COLUMNS, crew_people):
            flight_row[person_column] = person["packed_detail"]

        if len(crew_people) > len(PERSON_COLUMNS):
            overflow_people = [
                person["overflow_label"] for person in crew_people[len(PERSON_COLUMNS) :]
            ]

        flight_row["PilotComments"] = _build_pilot_comments(row, overflow_people)

        flight_rows.append(flight_row)

    flights_df = pd.DataFrame(flight_rows, columns=FLIGHT_HEADER_ROW)

    aircraft_rows = []
    for _, row in retained_df.iterrows():
        aircraft_details = _default_aircraft_details()
        aircraft_details.update(AIRCRAFT_DETAILS_MAP.get(row["MappedTypeCode"], {}))

        aircraft_rows.append(
            {
                "AircraftID": row["Tail"],
                "equipType": aircraft_details["equipType"],
                "TypeCode": row["MappedTypeCode"],
                "Year": "",
                "Make": aircraft_details["Make"],
                "Model": aircraft_details["Model"],
                "GearType": aircraft_details["GearType"],
                "EngineType": aircraft_details["EngineType"],
                "Category/Class": aircraft_details["Category/Class"],
                "complexAircraft": aircraft_details["complexAircraft"],
                "highPerformance": aircraft_details["highPerformance"],
                "pressurized": aircraft_details["pressurized"],
                "taa": aircraft_details["taa"],
            }
        )

    aircraft_df = pd.DataFrame(aircraft_rows, columns=AIRCRAFT_HEADER_ROW)
    aircraft_df = aircraft_df.drop_duplicates(
        subset=["AircraftID", "TypeCode"]
    ).reset_index(drop=True)

    kept_rows = len(flights_df)
    stats = {
        "input_rows": input_rows,
        "kept_rows": kept_rows,
        "skipped_rows": input_rows - kept_rows,
        "pic_rows": pic_rows,
        "sic_rows": sic_rows,
        "logged_pilot_label": logged_pilot["label"],
        "logged_pilot_source": logged_pilot["source"],
        "logged_pilot_matched": logged_pilot["matched"],
        "logged_pilot_ambiguous": logged_pilot["ambiguous"],
        "logged_pilot_options": logged_pilot["options"],
    }

    return flights_df, aircraft_df, stats


def build_foreflight_csv_rows(flights_df, aircraft_df):
    total_columns = len(FLIGHT_HEADER_ROW)

    def pad_row(row_values):
        row_as_list = list(row_values)
        if len(row_as_list) < total_columns:
            row_as_list.extend([""] * (total_columns - len(row_as_list)))
        return row_as_list

    # Build the final single CSV file in the same section order
    # used by the ForeFlight import template.
    rows = [
        pad_row(
            [
                "ForeFlight Logbook Import",
                "This row is required for importing into ForeFlight. Do not delete or modify.",
            ]
        ),
        pad_row([]),
        pad_row(["Aircraft Table"]),
        pad_row(AIRCRAFT_TYPE_ROW),
        pad_row(AIRCRAFT_HEADER_ROW),
    ]

    for _, row in aircraft_df.iterrows():
        rows.append(pad_row([row[column] for column in AIRCRAFT_HEADER_ROW]))

    rows.append(pad_row([]))
    rows.append(pad_row(["Flights Table"]))
    rows.append(pad_row(FLIGHT_TYPE_ROW))
    rows.append(pad_row(FLIGHT_HEADER_ROW))

    for _, row in flights_df.iterrows():
        rows.append(pad_row([row[column] for column in FLIGHT_HEADER_ROW]))

    return rows


def convert_rows_to_csv_text(rows):
    # Convert the row list into the downloadable CSV text.
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerows(rows)
    return output.getvalue()
