#LF

import streamlit as st
import pandas as pd
import plotly.express as px
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

    # 1. مشاركة الحافلات - رسم مقارنة (Total vs Participating)
    participation_df = pd.DataFrame(
        summary["bus_participation_by_company"],
        columns=["Company", "Total Buses", "Participating Buses"]
    )
    st.write("**Bus Participation by Company**")
    fig1 = px.bar(
        participation_df,
        x="Company",
        y=["Total Buses", "Participating Buses"],
        barmode="group"
    )
    st.plotly_chart(fig1, use_container_width=True, key="chart_participation")

    # 2. النشطة مقابل الإجمالي - رسم مقارنة (Total vs Active)
    active_df = pd.DataFrame(
        summary["active_vs_total_buses"],
        columns=["Company", "Total Buses", "Active Buses"]
    )
    st.write("**Active vs Total Buses by Company**")
    fig2 = px.bar(
        active_df,
        x="Company",
        y=["Total Buses", "Active Buses"],
        barmode="group"
    )
    st.plotly_chart(fig2, use_container_width=True, key="chart_active")

    # باقي البيانات (عمودين بس) تستخدم render_chart العادية مع قرار Claude
    remaining_datasets = [
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

    for dataset in remaining_datasets:
        chart_type = decide_chart_type(
            dataset["description"],
            list(dataset["df"].columns)
        )
        render_chart(dataset["df"], chart_type, dataset["title"])