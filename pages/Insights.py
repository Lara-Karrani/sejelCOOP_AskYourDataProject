#LF
import streamlit as st
import pandas as pd
from backend import generate_insights, get_data_summary

import streamlit as st
import pandas as pd
from backend import generate_insights, get_data_summary, decide_chart_type, render_chart

st.title("📈 AI-Generated Data Insights")
st.caption("Let AI analyze your fleet data and surface meaningful trends.")

if st.button("Generate Insights", type="primary"):
    with st.spinner("Analyzing your data..."):
        summary = get_data_summary()
        insights = generate_insights()

    st.markdown(insights)

    st.divider()
    st.subheader("📊 Visual Breakdown")

    datasets = [
        {
            "df": pd.DataFrame(summary["bus_participation_by_company"],
                                columns=["Company", "Total Buses", "Participating Buses"]),
            "description": "Number of participating buses vs total buses per company",
            "title": "Bus Participation by Company"
        },
        {
            "df": pd.DataFrame(summary["active_vs_total_buses"],
                                columns=["Company", "Total Buses", "Active Buses"]),
            "description": "Active buses vs total buses per company",
            "title": "Active vs Total Buses by Company"
        },
        {
            "df": pd.DataFrame(summary["pending_requests_by_company"],
                                columns=["Company", "Pending Requests"]),
            "description": "Number of pending requests per company",
            "title": "Pending Requests by Company"
        },
        {
            "df": pd.DataFrame(summary["companies_by_city"],
                                columns=["City", "Company Count"]),
            "description": "Number of transportation companies per city",
            "title": "Companies by City"
        },
        {
            "df": pd.DataFrame(summary["fleet_size_by_company"],
                                columns=["Company", "Fleet Size"]),
            "description": "Fleet size (number of buses) per company",
            "title": "Fleet Size by Company"
        },
    ]

    for dataset in datasets:
        chart_type = decide_chart_type(
            dataset["description"],
            list(dataset["df"].columns)
        )
        render_chart(dataset["df"], chart_type, dataset["title"])