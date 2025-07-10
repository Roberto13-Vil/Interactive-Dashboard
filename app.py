import streamlit as st
import pandas as pd
import dask.dataframe as dd
import plotly.express as px
import altair as alt
import warnings

warnings.filterwarnings("ignore")

# ---------- Streamlit Configuration ---------- #
st.set_page_config(
    page_title="Mexico Incidents Dashboard",
    page_icon=":oncoming_police_car:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
    }
    .subtitle {
        font-size: 1.25rem;
        color: #FFFFFF;
    }
    .stPlotlyChart {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'> Mexico Incidents Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Explore reported incidents in Mexico with interactive visualizations by date, location, and crime type.</div>", unsafe_allow_html=True)

alt.themes.enable("dark")
# ---------- Data loading ---------- #
def load_dask():
    df = dd.read_parquet("Data/cleaned_data")

    df_sorted = df.sort_values("Fecha", ascending=False)

    df_sampled = df_sorted.head(2_000_000, compute=False)

    return df_sampled.persist()

df = load_dask()

# ---------- Sidebar filters ---------- #
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/16139/16139852.png", width=80)
    st.title("Filters")

    # ---- Date range ---- #
    min_date, max_date = (df["Fecha"].min().compute(), df["Fecha"].max().compute())
    start_date = st.date_input("Start Date", value=min_date,
                               min_value=min_date, max_value=max_date)
    end_date   = st.date_input("End Date",   value=max_date,
                               min_value=min_date, max_value=max_date)
    start_date, end_date = map(pd.to_datetime, (start_date, end_date))

    st.divider()

    # ---- States ---- #
    @st.cache_data
    def get_states():
        return sorted(df["Entidad"].unique().compute().tolist())

    selected_states = st.multiselect("Select States",
                                     options=get_states(), default=[])

    st.divider()

    # ---- Municipalities ---- #
    if selected_states:
        @st.cache_data
        def mun_by_states(states):
            return (df[df["Entidad"].isin(states)]
                    ["Municipio"].unique().compute().tolist())

        municipalities = sorted(mun_by_states(selected_states))
    else:
        municipalities = []

    selected_municipalities = st.multiselect("Select Municipalities",
                                             options=municipalities,
                                             default=[],
                                             disabled=not selected_states)

    st.divider()

    # ---- Affected legal good ---- #
    @st.cache_data
    def get_affectations():
        return sorted(df["Bien jurídico afectado"].unique().compute().tolist())

    affectations_list = get_affectations()
    selected_affectations = st.multiselect("Select Affectation Types",
                                        options=affectations_list, default=[])

    st.divider()

    # ---- Incident type ---- #
    @st.cache_data
    def get_incident_types(selected_affectations=None):
        if not selected_affectations:
            return sorted(df["Tipo de delito"].unique().compute().tolist())
        else:
            return sorted(df[df["Bien jurídico afectado"].isin(selected_affectations)]
                        ["Tipo de delito"].unique().compute().tolist())

    incident_types_list = get_incident_types(selected_affectations)

    selected_incidents = st.multiselect("Select Incident Types",
                                        options=incident_types_list, default=[])

    # ---- Modality ---- #
    @st.cache_data
    def get_modalities_by_types(types):
        return sorted(df[df["Tipo de delito"].isin(types)]
                    ["Modalidad"].unique().compute().tolist())

    modalities_list = get_modalities_by_types(selected_incidents) if selected_incidents else []

    selected_modalities = st.multiselect("Select Modalities",
                                        options=modalities_list, default=[],
                                        disabled=not selected_incidents)

# ---------- Filtering pipeline ---------- #
df_range = df[(df["Fecha"] >= start_date) & (df["Fecha"] <= end_date)]
df_filt = df_range.copy()

if selected_states:
    df_filt = df_filt[df_filt["Entidad"].isin(selected_states)]
if selected_municipalities:
    df_filt = df_filt[df_filt["Municipio"].isin(selected_municipalities)]
if selected_affectations:
    df_filt = df_filt[df_filt["Bien jurídico afectado"].isin(selected_affectations)]
if selected_incidents:
    df_filt = df_filt[df_filt["Tipo de delito"].isin(selected_incidents)]
if selected_modalities:
    df_filt = df_filt[df_filt["Modalidad"].isin(selected_modalities)]

# ---------- Aggregations (computed ONCE) ---------- #
df_line = (df_filt.groupby(["Fecha", "Entidad"])["Incidentes"]
           .sum().compute().reset_index().sort_values("Fecha"))

df_line_mun = (df_filt.groupby(["Entidad", "Municipio"])["Incidentes"]
                .sum().compute().reset_index()
                .sort_values("Incidentes", ascending=False).head(20))
    
df_line_aff = (df_filt.groupby(["Fecha", "Bien jurídico afectado"])["Incidentes"]
                   .sum().compute().reset_index().sort_values("Fecha"))
df_line_aff_sorted = (df_filt.groupby(["Bien jurídico afectado"])["Incidentes"]
                     .sum().compute().reset_index().sort_values("Incidentes", ascending=False))
df_line_aff_sorted = df_line_aff[df_line_aff['Incidentes'] > 0].sort_values('Incidentes', ascending=False)

df_line_type = (df_filt.groupby(["Fecha", "Tipo de delito"])["Incidentes"]
                .sum().compute().reset_index().sort_values("Fecha"))
df_line_type_sorted = (df_filt.groupby(["Tipo de delito"])["Incidentes"]
                      .sum().compute().reset_index().sort_values("Incidentes", ascending=False))
df_line_type_sorted = df_line_type_sorted[df_line_type_sorted['Incidentes'] > 0]

if selected_incidents:
    df_line_mod = (df_filt.groupby(["Fecha", "Modalidad"])["Incidentes"]
                   .sum().compute().reset_index().sort_values("Fecha"))
    df_line_mod_sorted = (df_filt.groupby(["Modalidad"])["Incidentes"]
                         .sum().compute().reset_index().sort_values("Incidentes", ascending=False))
    df_line_mod_sorted = df_line_mod_sorted[df_line_mod_sorted['Incidentes'] > 0]

df_kpi  = (df_range.groupby("Entidad")["Incidentes"]
           .sum().compute().reset_index(name="Total Incidents")
           .query("`Total Incidents` > 0")
           .sort_values("Total Incidents", ascending=False))

most_state, least_state = df_kpi.iloc[0], df_kpi.iloc[-1]

# ---------- KPI cards ---------- #
st.markdown("### 🔎 Incident Overview by State")
col1, _, col3 = st.columns([1, .1, 1])

with col1:
    st.metric("📈 State with Most Incidents",
              most_state["Entidad"],
              f"{most_state['Total Incidents']:,} incidents",
              delta_color="inverse")
with col3:
    st.metric("📉 State with Least Incidents",
              least_state["Entidad"],
              f"{least_state['Total Incidents']:,} incidents")

# ---------- Bar chart of incidents by state ---------- #
with col1:
    with st.expander("Show/Hide Incident Counts by State", expanded=True):
        st.markdown("### 📊 Incidents by State")
        if selected_states:
            bar_df = df_kpi[df_kpi["Entidad"].isin(selected_states)]
        else:
            bar_df = df_kpi.copy()
        bar_df = bar_df.sort_values("Total Incidents", ascending=False)
        fig = px.bar(bar_df, x="Entidad", y="Total Incidents",
                        labels={"Total Incidents": "Total Incidents", "Entidad": "State"},
                        color="Total Incidents", color_continuous_scale="Bluered_r")
        fig.update_layout(xaxis_title="State", yaxis_title="Total Incidents",
                        legend_title="Total Incidents",
                        xaxis_tickangle=-45, xaxis_categoryorder="total descending")
        st.plotly_chart(fig, use_container_width=True)

# ---------- Time‑series plot ---------- #
with col3:
    with st.expander("Show/Hide Time Series of Incidents", expanded=True):
        st.markdown("### 📈 Time Series of Incidents")
        if selected_states:
            plot_df = df_line[df_line["Entidad"].isin(selected_states)]
            plot_df = plot_df[plot_df['Incidentes'] > 0]
        else:
            plot_df = (df_line.groupby("Fecha")["Incidentes"]
                    .sum().reset_index()).assign(Entidad="National")

        fig = px.line(plot_df, x="Fecha", y="Incidentes", color="Entidad")
        fig.update_layout(xaxis_title="Date", yaxis_title="Incidents",
                        legend_title="State")
        st.plotly_chart(fig, use_container_width=True)

# ---------- Bar chart of incidents and KPI card by municipality ---------- #
with col1:
    st.markdown("### 🔎 Incident Overview by Municipality")
    with st.expander("Show/Hide Incident Counts by Municipality", expanded=True):
        st.metric("📈 Municipality with Most Incidents",
                    df_line_mun.iloc[0]["Municipio"],
                    f"{df_line_mun.iloc[0]['Incidentes']:,} incidents",
                    delta_color="inverse")

        st.markdown("### 📊 Incidents by Municipality")

        fig = px.bar(
            df_line_mun[df_line_mun['Incidentes'] > 0],
            x="Municipio",
            y="Incidentes",
            color="Incidentes",
            color_continuous_scale="Reds",
            labels={"Incidentes": "Total Incidents", "Municipio": "Municipality"},
            title="Top Municipalities by Total Incidents" if not selected_municipalities else "Selected Municipalities"
        )
        fig.update_layout(
            xaxis_title="Municipality",
            yaxis_title="Total Incidents",
            coloraxis_showscale=True,
            xaxis_tickangle=-45,
            xaxis_categoryorder="total descending",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("### 🔎 Incident Overview by Affectation")
    with st.expander("Show/Hide Incident Overview by Affectation", expanded=True):
        st.metric("📈 Affectation with Most Incidents",
                df_line_aff_sorted.iloc[0]["Bien jurídico afectado"],
                f"{df_line_aff_sorted.iloc[0]['Incidentes']:,} incidents",
                delta_color="inverse")
        
        st.metric("📈 Affectation with Least Incidents",
                df_line_aff_sorted.iloc[-1]["Bien jurídico afectado"],
                f"{df_line_aff_sorted.iloc[-1]['Incidentes']:,} incidents")
        
        st.markdown("### 📈 Time Series of Incidents by Affectation")
        fig = px.line(df_line_aff[df_line_aff['Incidentes'] > 0], 
                    x="Fecha", y="Incidentes",
                    color="Bien jurídico afectado",
                    labels={"Incidentes": "Total Incidents", "Fecha": "Date"},
                    title="Time Series of Incidents by Affectation")
        fig.update_layout(xaxis_title="Date", yaxis_title="Total Incidents",
                        legend_title="Affectation Type")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📊 Incident Counts by Affectation")
        fig = px.bar(df_line_aff[df_line_aff['Incidentes'] > 0],
                    x="Bien jurídico afectado", y="Incidentes",
                    color="Incidentes", color_continuous_scale="Bluered_r",
                    labels={"Incidentes": "Total Incidents", "Bien jurídico afectado": "Affectation Type"},
                    title="Incident Counts by Affectation")
        fig.update_layout(xaxis_title="Affectation Type", yaxis_title="Total Incidents",
                        xaxis_tickangle=-45, xaxis_categoryorder="total descending")
        st.plotly_chart(fig, use_container_width=True)

# ---------- Type of incident and modality charts ---------- #
with col1:
    st.markdown("### 🔎 Incident Overview by Type")
    with st.expander("Show/Hide Incident Overview by Type", expanded=True):
        st.metric("📈 Type with Most Incidents",
                df_line_type_sorted.iloc[0]["Tipo de delito"],
                f"{df_line_type_sorted.iloc[0]['Incidentes']:,} incidents",
                delta_color="inverse")
        st.metric("📉 Type with Least Incidents",
                df_line_type_sorted.iloc[-1]["Tipo de delito"],
                f"{df_line_type_sorted.iloc[-1]['Incidentes']:,} incidents")
        
        st.markdown("### 📈 Time Series of Incidents by Type")
        fig = px.line(df_line_type[df_line_type['Incidentes'] > 0],
                    x="Fecha", y="Incidentes",
                    color="Tipo de delito",
                    labels={"Incidentes": "Total Incidents", "Fecha": "Date"},
                    title="Time Series of Incidents by Type")
        fig.update_layout(xaxis_title="Date", yaxis_title="Total Incidents",
                        legend_title="Incident Type")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📊 Top Incident Counts by Type")
        fig = px.bar(df_line_type_sorted.head(20),
                    x="Tipo de delito", y="Incidentes",
                    color="Incidentes", color_continuous_scale=px.colors.sequential.Reds,
                    labels={"Incidentes": "Total Incidents", "Tipo de delito": "Incident Type"},
                    title="Incident Counts by Type")
        fig.update_layout(xaxis_title="Incident Type", yaxis_title="Total Incidents",
                        xaxis_tickangle=-45, xaxis_categoryorder="total descending")
        st.plotly_chart(fig, use_container_width=True)
with col3:
    st.markdown("### 🔎 Incident Overview by Modality")
    with st.expander("Show/Hide Incident Overview by Modality", expanded=True):
        if selected_incidents:
            st.markdown("### 📈 Time Series of Incidents by Modality")
            fig = px.line(df_line_mod[df_line_mod['Incidentes'] > 0],
                        x="Fecha", y="Incidentes",
                        color="Modalidad",
                        labels={"Incidentes": "Total Incidents", "Fecha": "Date"},
                        title="Time Series of Incidents by Modality")
            fig.update_layout(xaxis_title="Date", yaxis_title="Total Incidents",
                            legend_title="Modality")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 📊 Incident Counts by Modality")
            fig = px.bar(df_line_mod_sorted.head(20),
                        x="Modalidad", y="Incidentes",
                        color="Incidentes", color_continuous_scale=px.colors.sequential.Reds,
                        labels={"Incidentes": "Total Incidents", "Modalidad": "Modality"},
                        title="Incident Counts by Modality")
            fig.update_layout(xaxis_title="Modality", yaxis_title="Total Incidents",
                            xaxis_tickangle=-45, xaxis_categoryorder="total descending")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("### 📊 No Modality Data Available")
            st.write("Please select incident types to view modality data.")

# ---------- Footer ---------- #
st.markdown("""
    <hr style="margin-top: 2rem;">
    <div style="text-align: center; color: gray;">
        Built by Roberto Vilchis | Powered by Streamlit + Dask + Plotly
    </div>
""", unsafe_allow_html=True)