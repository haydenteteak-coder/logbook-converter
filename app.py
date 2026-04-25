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
3. Choose whether you want the imported time logged as `PIC` or `SIC`.
4. Upload that CSV here.
5. Preview the converted entries and confirm they look right.
6. Scroll down and click `Download ForeFlight Import CSV`.
7. Open the ForeFlight website, go to `Logbook` > `Import`, and upload the converted file.
8. Complete the import, then review your entries in ForeFlight.

Notes:
- Doing this once at the end of each month is usually the easiest workflow.
- You can export more often, but that can create duplicate entries, so double-check before importing.
- The `PIC / SIC` selector applies that role to every imported flight in the file.
- If you run into issues, email `HaydenTeteak@gmail.com` and include a short description of what went wrong.
- This tool was built from scratch and may still have a few rough edges, so please do not hesitate to report problems.
"""
    )

time_role = st.radio(
    "Log imported time as",
    options=["SIC", "PIC"],
    index=0,
    horizontal=True,
)

uploaded_file = st.file_uploader("Upload airline schedule CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Convert the uploaded airline CSV into ForeFlight-ready tables.
        flights_df, aircraft_df, stats = convert_schedule(
            uploaded_file,
            time_role=time_role,
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
        st.caption(f"Selected time role: {stats['selected_time_role']}")

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
