import streamlit as st

from converter import (
    MissingColumnsError,
    build_foreflight_csv_rows,
    convert_rows_to_csv_text,
    convert_schedule,
)


st.set_page_config(page_title="Airline Logbook Converter")

st.title("Airline Logbook Converter")
st.write(
    "Upload your airline schedule CSV, preview the converted data, "
    "and download one ForeFlight import CSV."
)

with st.expander("How to Use This Converter"):
    st.markdown(
        """
1. Log in to SkedPlus+ and export the month you want to log.
2. In the export options, choose `CSV - as block in decimal`.
3. Optional: enter your employee number or name if you want to override the app's automatic pilot detection.
4. Upload that CSV here.
5. Preview the converted entries and confirm they look right.
6. Scroll down and click `Download ForeFlight Import CSV`.
7. Open the ForeFlight website, go to `Logbook` > `Import`, and upload the converted file.
8. Complete the import, then review your entries in ForeFlight.

Notes:
- Doing this once at the end of each month is usually the easiest workflow.
- You can export more often, but that can create duplicate entries, so double-check before importing.
- The converter auto-detects which pilot is you and logs each leg as `PIC` or `SIC` based on whether your name appears in the Captain or First Officer column.
- If you run into issues, email `HaydenTeteak@gmail.com` and include a short description of what went wrong.
- This tool was built from scratch and may still have a few rough edges, so please do not hesitate to report problems.
"""
    )

user_identifier = st.text_input(
    "Your employee number or name (optional)",
    help=(
        "Leave this blank to let the converter auto-detect which pilot is you "
        "from the Captain and First Officer columns."
    ),
)

uploaded_file = st.file_uploader("Upload airline schedule CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Convert the uploaded airline CSV into ForeFlight-ready tables.
        flights_df, aircraft_df, stats = convert_schedule(
            uploaded_file,
            user_identifier=user_identifier,
        )
        final_rows = build_foreflight_csv_rows(flights_df, aircraft_df)
        final_csv_text = convert_rows_to_csv_text(final_rows)

        st.subheader("Stats")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total input rows", stats["input_rows"])
        col2.metric("Total kept rows", stats["kept_rows"])
        col3.metric("Total skipped rows", stats["skipped_rows"])
        col4.metric("PIC rows", stats["pic_rows"])
        col5.metric("SIC rows", stats["sic_rows"])

        if stats["logged_pilot_label"]:
            detection_label = (
                "Manual override"
                if stats["logged_pilot_source"] == "manual"
                else "Auto-detected"
            )
            st.caption(
                f"{detection_label} pilot: {stats['logged_pilot_label']}"
            )

        if user_identifier and not stats["logged_pilot_matched"]:
            st.warning(
                "Your manual pilot entry did not match the Captain or First "
                "Officer columns in this file, so unmatched rows defaulted to SIC."
            )
        elif stats["logged_pilot_ambiguous"]:
            pilot_options = ", ".join(stats["logged_pilot_options"])
            st.warning(
                "The converter found more than one pilot with the same number "
                f"of matching rows: {pilot_options}. Enter your employee number "
                "or name above to make PIC/SIC assignment exact. Until then, "
                "unmatched rows default to SIC."
            )

        st.subheader("Converted Flights Preview")
        st.dataframe(flights_df, width="stretch")

        st.subheader("Aircraft Preview")
        st.dataframe(aircraft_df, width="stretch")

        st.download_button(
            label="Download ForeFlight Import CSV",
            data=final_csv_text,
            file_name="foreflight_import.csv",
            mime="text/csv",
        )
    except MissingColumnsError as error:
        missing_columns_text = ", ".join(error.missing_columns)
        st.error(
            "Your CSV is missing required columns: "
            f"{missing_columns_text}. "
            "Please upload a file with all required columns."
        )
    except Exception as error:
        st.error(f"Something went wrong while converting the file: {error}")
else:
    st.info("Required input columns: Date, A/C Type, Tail, Origin, Dest, Block")
