import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from schema import get_engine
from queries import QUERIES, run_query

# page setup
st.set_page_config(
    page_title="Air Tracker: Flight Analytics",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# custom css styling
st.markdown("""
<style>
    /* Theme overrides */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f1f5f9;
    }
    
    /* Header styling */
    h1, h2, h3 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    .main-title {
        background: linear-gradient(90deg, #38bdf8 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Custom cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.3);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    /* Query container */
    .query-box {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Courier New', Courier, monospace;
        color: #34d399;
        margin-bottom: 1rem;
        overflow-x: auto;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 4rem;
        color: #64748b;
        font-size: 0.85rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# db loader
@st.cache_data(ttl=60)
def load_table_data(table_name):
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql_table(table_name, conn)
    return df

# validation check
try:
    airports_df = load_table_data("airport")
    flights_df = load_table_data("flights")
    aircraft_df = load_table_data("aircraft")
    delays_df = load_table_data("airport_delays")
except Exception as e:
    st.error(f"Error connecting to database tables: {e}")
    st.warning("Please run `python ingest.py` in the terminal to initialize and populate the database.")
    st.stop()

# navigation menu
st.sidebar.image("https://img.icons8.com/color/96/airport.png", width=64)
st.sidebar.markdown("<h2 style='margin-top:0;'>Air Tracker Panel</h2>", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Navigate to:",
    ["Dashboard Home", "Search & Filter Flights", "Airport Details Viewer", "Delay Analysis", "Route Leaderboards", "Mandatory SQL Queries"]
)

# show database record count
st.sidebar.markdown("---")
st.sidebar.markdown("### Database Connection Status")
db_type = load_table_data("airport").empty
st.sidebar.success("Connected to Database ✅")
st.sidebar.markdown(f"**Loaded Airports:** `{len(airports_df)}`")
st.sidebar.markdown(f"**Loaded Flights:** `{len(flights_df)}`")
st.sidebar.markdown(f"**Loaded Aircraft:** `{len(aircraft_df)}`")

# metrics wrapper
def draw_metric_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# Page 1: Dashboard Home
if page == "Dashboard Home":
    st.markdown("<div class='main-title'>Air Tracker: Flight Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>A comprehensive real-time dashboard visualizing airport networks, flights, and delay statistics.</div>", unsafe_allow_html=True)
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        draw_metric_card("Airports Tracked", len(airports_df))
    with col2:
        draw_metric_card("Total Flights", len(flights_df))
    with col3:
        delayed_pct = (flights_df['status'] == 'Delayed').sum() / len(flights_df) * 100 if len(flights_df) > 0 else 0
        draw_metric_card("Delay Rate", f"{delayed_pct:.1f}%")
    with col4:
        avg_delay = delays_df['avg_delay_min'].mean() if len(delays_df) > 0 else 0
        draw_metric_card("Avg Delay", f"{avg_delay:.1f} min")

    st.markdown("### Tracked Airports Network Map")
    # Plotly Scatter Mapbox
    if not airports_df.empty:
        fig = px.scatter_mapbox(
            airports_df,
            lat="latitude",
            lon="longitude",
            hover_name="name",
            hover_data=["city", "country", "iata_code", "timezone"],
            color="continent",
            size_max=15,
            zoom=1,
            height=450,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color="white"))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Graphs Row
    st.markdown("<br>", unsafe_allow_html=True)
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown("### Flights by Status")
        status_counts = flights_df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_pie = px.pie(
            status_counts, 
            values='Count', 
            names='Status', 
            hole=0.4,
            color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444']
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with g_col2:
        st.markdown("### Top Airlines by Flight Count")
        airline_counts = flights_df['airline_code'].value_counts().reset_index()
        airline_counts.columns = ['Airline', 'Flights']
        fig_bar = px.bar(
            airline_counts.head(10), 
            x='Airline', 
            y='Flights',
            color='Flights',
            color_continuous_scale=px.colors.sequential.Agsunset
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# Page 2: Search & Filter Flights
elif page == "Search & Filter Flights":
    st.markdown("<h2>Search & Filter Flights</h2>", unsafe_allow_html=True)
    
    # Filters
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        search_query = st.text_input("Search Flight Number / Airline Code:", "").strip()
    with f_col2:
        origin_filter = st.multiselect("Origin Airport:", sorted(flights_df['origin_iata'].unique()))
    with f_col3:
        dest_filter = st.multiselect("Destination Airport:", sorted(flights_df['destination_iata'].unique()))
    with f_col4:
        status_filter = st.multiselect("Flight Status:", sorted(flights_df['status'].unique()))
        
    # Apply filters
    filtered_df = flights_df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df['flight_number'].str.contains(search_query, case=False, na=False) |
            filtered_df['airline_code'].str.contains(search_query, case=False, na=False)
        ]
    if origin_filter:
        filtered_df = filtered_df[filtered_df['origin_iata'].isin(origin_filter)]
    if dest_filter:
        filtered_df = filtered_df[filtered_df['destination_iata'].isin(dest_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        
    st.markdown(f"**Found {len(filtered_df)} matching flights**")
    
    # Render table
    st.dataframe(
        filtered_df[[
            "flight_number", "airline_code", "aircraft_registration", 
            "origin_iata", "destination_iata", "scheduled_departure", 
            "scheduled_arrival", "status"
        ]], 
        use_container_width=True
    )

# Page 3: Airport Details Viewer
elif page == "Airport Details Viewer":
    st.markdown("<h2>Airport Details Viewer</h2>", unsafe_allow_html=True)
    
    airport_options = [f"{row['iata_code']} - {row['name']} ({row['city']})" for idx, row in airports_df.iterrows()]
    selected_ap_str = st.selectbox("Select Airport to inspect:", airport_options)
    
    if selected_ap_str:
        iata = selected_ap_str.split(" - ")[0]
        ap_details = airports_df[airports_df['iata_code'] == iata].iloc[0]
        
        # Details layout
        d_col1, d_col2 = st.columns([1, 2])
        
        with d_col1:
            st.markdown(f"### {ap_details['name']}")
            st.markdown(f"**IATA Code:** `{ap_details['iata_code']}`")
            st.markdown(f"**ICAO Code:** `{ap_details['icao_code']}`")
            st.markdown(f"**City:** {ap_details['city']}")
            st.markdown(f"**Country:** {ap_details['country']}")
            st.markdown(f"**Continent:** {ap_details['continent']}")
            st.markdown(f"**Timezone:** `{ap_details['timezone']}`")
            st.markdown(f"**Latitude:** {ap_details['latitude']}")
            st.markdown(f"**Longitude:** {ap_details['longitude']}")
            
        with d_col2:
            # Map of this specific airport
            fig_single = px.scatter_mapbox(
                pd.DataFrame([ap_details]),
                lat="latitude",
                lon="longitude",
                hover_name="name",
                zoom=8,
                height=300
            )
            fig_single.update_layout(
                mapbox_style="carto-darkmatter",
                margin={"r":0,"t":0,"l":0,"b":0},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_single, use_container_width=True)

        st.markdown("---")
        # Departures and Arrivals tables
        tab_dep, tab_arr = st.tabs(["🛫 Outbound Departures", "🛬 Inbound Arrivals"])
        
        with tab_dep:
            deps = flights_df[flights_df['origin_iata'] == iata]
            st.markdown(f"Found **{len(deps)}** outbound departures")
            st.dataframe(deps[["flight_number", "destination_iata", "scheduled_departure", "actual_departure", "status"]], use_container_width=True)
            
        with tab_arr:
            arrs = flights_df[flights_df['destination_iata'] == iata]
            st.markdown(f"Found **{len(arrs)}** inbound arrivals")
            st.dataframe(arrs[["flight_number", "origin_iata", "scheduled_arrival", "actual_arrival", "status"]], use_container_width=True)

# Page 4: Delay Analysis
elif page == "Delay Analysis":
    st.markdown("<h2>Delay Analysis</h2>", unsafe_allow_html=True)
    
    # Delay stats visualizer
    if not delays_df.empty:
        # Merge delays_df with airports_df to get airport names
        merged_delays = pd.merge(delays_df, airports_df, left_on="airport_iata", right_on="iata_code")
        
        # Plot delay rate
        merged_delays['delay_rate'] = (merged_delays['delayed_flights'] / merged_delays['total_flights'] * 100).round(1)
        
        st.markdown("### Delay Percentages by Airport")
        fig_del_rate = px.bar(
            merged_delays,
            x='iata_code',
            y='delay_rate',
            hover_name='name',
            labels={'delay_rate': 'Delay Percentage (%)', 'iata_code': 'Airport Code'},
            color='avg_delay_min',
            color_continuous_scale=px.colors.sequential.YlOrRd
        )
        fig_del_rate.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white")
        )
        st.plotly_chart(fig_del_rate, use_container_width=True)
        
        # Tabular details
        st.markdown("### Delay Statistics Table")
        st.dataframe(
            merged_delays[[
                "iata_code", "name", "city", "total_flights", 
                "delayed_flights", "delay_rate", "avg_delay_min", 
                "median_delay_min", "canceled_flights"
            ]], 
            use_container_width=True
        )
    else:
        st.info("No delay statistics found in database.")

# Page 5: Route Leaderboards
elif page == "Route Leaderboards":
    st.markdown("<h2>Route Leaderboards</h2>", unsafe_allow_html=True)
    
    # Create Route analysis
    flights_df['route'] = flights_df['origin_iata'] + " ➔ " + flights_df['destination_iata']
    route_counts = flights_df['route'].value_counts().reset_index()
    route_counts.columns = ['Route', 'Flight Count']
    
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        st.markdown("### Busiest Flight Routes")
        fig_routes = px.bar(
            route_counts.head(10),
            x='Flight Count',
            y='Route',
            orientation='h',
            color='Flight Count',
            color_continuous_scale=px.colors.sequential.Blugrn
        )
        fig_routes.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_routes, use_container_width=True)
        
    with col_l2:
        st.markdown("### Most Delayed Airport Hubs")
        if not delays_df.empty:
            merged_delays = pd.merge(delays_df, airports_df, left_on="airport_iata", right_on="iata_code")
            fig_delayed_hubs = px.bar(
                merged_delays.sort_values(by="avg_delay_min", ascending=False).head(10),
                x='avg_delay_min',
                y='iata_code',
                orientation='h',
                labels={'avg_delay_min': 'Avg Delay Time (Minutes)', 'iata_code': 'Airport'},
                color='avg_delay_min',
                color_continuous_scale=px.colors.sequential.Electric
            )
            fig_delayed_hubs.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white"),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_delayed_hubs, use_container_width=True)
        else:
            st.info("No delay metrics to calculate hubs.")

# Page 6: Mandatory SQL Queries
elif page == "Mandatory SQL Queries":
    st.markdown("<h2>Required SQL Queries</h2>", unsafe_allow_html=True)
    st.markdown("These 11 SQL queries are run directly against the active relational database schema.")
    
    # Query selector
    selected_query_title = st.selectbox("Select SQL Query to execute:", [q["title"] for q in QUERIES])
    
    query = next(q for q in QUERIES if q["title"] == selected_query_title)
    
    st.markdown(f"### Objective")
    st.write(query["description"])
    
    st.markdown("### SQL Statement")
    st.markdown(f"<div class='query-box'>{query['sql']}</div>", unsafe_allow_html=True)
    
    if st.button("▶️ Execute Query"):
        try:
            results_df = run_query(query["id"])
            st.markdown("### Execution Results")
            st.dataframe(results_df, use_container_width=True)
            
            # Download CSV
            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                csv,
                f"query_{query['id']}_results.csv",
                "text/csv",
                key='download-csv'
            )
        except Exception as e:
            st.error(f"Error executing query: {e}")

# Footer
st.markdown("<div class='footer'>Air Tracker: Flight Analytics • Built with Python, Streamlit & SQL</div>", unsafe_allow_html=True)
