import base64
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

## Set the page config1uration

st.set_page_config(page_title= "Nassau Candy Distributor", page_icon= "🍭", layout= "wide")
st.markdown("""
<style>
/* FORCE DARK + PURPLE THEME */
html, body, [class*="css"]  {
    background-color: #0E1117 !important;
    color: white !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #1F1B2E !important;
}

/* REMOVE ORANGE ACCENTS */
* {
    accent-color: #7B2CBF !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🚚 Factory-to-Customer Shipping Route Efficiency Analysis for Nassau Candy Distributor")
st.markdown('<style>div.block-container{padding-top: 2rem;}</style>', unsafe_allow_html=True)


## Load data


data = st.file_uploader("Upload CSV", type=["csv"])

if data is not None:
    df = pd.read_csv(data)
else:
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "Nassau Candy Distributor.csv")
    df = pd.read_csv(file_path, encoding="ISO-8859-1")

## Feature Engineering

df["Order Date"] = pd.to_datetime(df["Order Date"],errors='coerce')
df = df.dropna(subset=['Order Date'])
# st.write(df['Order Date'].size)
df["Ship Date"] = pd.to_datetime(df["Ship Date"],errors='coerce')
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
df = df[df['Lead Time'] >= 0]
df = df.rename(columns={'Lead Time': 'Shipping Lead Time'})
factory_map = {
    "Wonka Bar - Nutty Crunch Surprise" : "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows" : "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious" : "Lot's O' Nuts", 
    "Wonka Bar - Milk Chocolate" : "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel" : "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS" : "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip" : "Sugar Shack",
    "Fizzy Lifting Drinks" : "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum" : "Secret Factory", 
    "Kazookles" : "The Other Factory",      
    "Hair Toffee": "The Other Factory" }

df["Factory"] = df["Product Name"].map(factory_map)


# df["Shipping Lead Time"] = pd.to_numeric(df["Shipping Lead Time"], errors="coerce")
df['Factory to Customer Region'] = df['Factory'] + " → " + df['Country/Region']
df['Factory to Customer State'] = df['Factory'] + " → " + df['State/Province']
df['City'] = df['City'].str.strip().str.title()
df['State/Province'] = df['State/Province'].str.strip().str.upper()




# Company Logo


# st.sidebar.markdown(
#     """
#     <div style="text-align: center;">
#         <img src="data:image/png;base64,{}" width="220">
#     </div>
#     """.format(base64.b64encode(open("logo.png", "rb").read()).decode()),
#     unsafe_allow_html=True)


logo_path = os.path.join(base_dir, "logo.png")

with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.sidebar.markdown(
    f"""
    <div style="text-align: center; padding: 10px;">
        <img src="data:image/png;base64,{logo_base64}" width="220"
        style="
            box-shadow: 0px 4px 15px rgba(0,0,0,0.25);
        ">
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("## Nassau Candy Distributor Dashboard")
st.sidebar.caption("Real-time Supply Chain Insights")

st.sidebar.markdown("---")


## Filters

#Navigation filter

page = st.sidebar.selectbox(
    "🧩Modules",
    ["Route Efficiency", "Geographic Map", "Ship Mode", "Route Drilldown"]
)

#Region/State Filter 

# Create for Region
region = st.sidebar.multiselect("🌍Select Region", df["Region"].unique())
# if not region:
#     df2 = df.copy()
# else:
#     df2 = df[df["Region"].isin(region)]

# Create for State
state = st.sidebar.multiselect("📍Select State", df["State/Province"].unique())
# if not state:
#     df3 = df2.copy()
# else:
#     df3 = df2[df2["State/Province"].isin(state)]

# Create for Ship Mode
ship_mode = st.sidebar.multiselect("🚚Select Ship Mode",df["Ship Mode"].unique())

# if not ship_mode:
#     filtered_df = df3.copy()
# else:
#     filtered_df = df3[df3["Ship Mode"].isin(ship_mode)]


#Date Range Filter
st.markdown("### 📅 Select Date Range")
col1, col2 = st.columns(2)
# Getting the min and max date 
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))


#Leead Time Slider
min_lt = int(df["Shipping Lead Time"].min())
max_lt = int(df["Shipping Lead Time"].max())

lead_range = st.sidebar.slider(
    "⏱️Lead-Time Threshold",
    min_value=min_lt,
    max_value=max_lt,
    value=(min_lt, max_lt)
)
#Creating filtered_df for Interpretation
filtered_df = df.copy()

# Region
if region:
    filtered_df = filtered_df[filtered_df["Region"].isin(region)]

# State
if state:
    filtered_df = filtered_df[filtered_df["State/Province"].isin(state)]

# Ship Mode
if ship_mode:
    filtered_df = filtered_df[filtered_df["Ship Mode"].isin(ship_mode)]

# Date
filtered_df = filtered_df[
    (filtered_df["Order Date"] >= pd.to_datetime(date1)) &
    (filtered_df["Order Date"] <= pd.to_datetime(date2))
]

# Lead Time slider
if not filtered_df.empty:
    filtered_df = filtered_df[
        (filtered_df["Shipping Lead Time"] >= lead_range[0]) &
        (filtered_df["Shipping Lead Time"] <= lead_range[1])
    ]

#Column metrics(KPIs)
def get_kpis(filtered_df):
    lead_time = filtered_df['Shipping Lead Time']
    avg_lead_time = lead_time.mean()
    route_volume = len(filtered_df)
    threshold = lead_time.mean() + lead_time.std()
    delay_freq = (lead_time > threshold).mean() * 100

    if lead_time.max() != lead_time.min():
        norm_lead = ((avg_lead_time - lead_time.min()) / (lead_time.max() - lead_time.min()))
    else:
        norm_lead = 0

    route_eff_score = norm_lead * 100
 
    total_sales = filtered_df["Sales"].sum()

    total_routes = filtered_df["Factory to Customer Region"].nunique()

    return avg_lead_time,route_volume,delay_freq,route_eff_score,total_sales,total_routes,threshold

avg_lead_time,route_volume,delay_freq,route_eff_score,total_sales,total_routes,threshold = get_kpis(filtered_df)

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

def metric_box(label, value, delta=None):
    st.markdown(
    """
    <div style="
        background: rgba(106, 13, 173, 0.7);
        background: linear-gradient(135deg, #6a0dad, #9b59b6);;
        padding:16px;
        border-radius:14px;
        text-align:center;
        color:white;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom:10px;
        ">
    """,
    unsafe_allow_html=True
    )

    st.metric(label, value, delta=delta)

    st.markdown("</div>", unsafe_allow_html=True)

# Row 1
# col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
# col2.metric("🌍 Total Routes", total_routes)
# col3.metric("📦 Route Volume", route_volume)

with col1:
    metric_box("💰 Total Sales", f"${total_sales:,.0f}")

with col2:
    metric_box("🌍 Total Routes", total_routes)

with col3:
    metric_box("📦 Route Volume", route_volume)

st.markdown("---")

# Row 2 (Advanced KPIs)
with col4:
    metric_box(
    "⏱ Avg Lead Time", f"{avg_lead_time:.2f} days"
    )

with col5:
    metric_box(
    "⚠️ Delay Frequency",
    f"{delay_freq:.1f}%",
    delta=f"Threshold: {threshold:.1f} days"
    )

with col6:
    metric_box(
    "⚡ Route Efficiency",
    f"{route_eff_score:.1f}%"
    )


#Define functions
def route_efficiency(filtered_df):

    # Metrics
    total_sales = filtered_df["Sales"].sum()

    avg_lead_time = (
        filtered_df["Ship Date"] - filtered_df["Order Date"]
    ).dt.days.mean()

    total_routes = filtered_df["Factory to Customer Region"].nunique()


    st.title("📦 Route Efficiency Overview")
    st.markdown("---")
    route_ranking = filtered_df.groupby('Factory to Customer Region')['Shipping Lead Time'].mean().round(2).sort_values(ascending=True).reset_index()
    Total_Shipments = filtered_df.groupby('Factory to Customer Region')['Sales'].sum().round(2).sort_values(ascending=False).reset_index()

    fig1 = px.bar(
    route_ranking,
    x="Shipping Lead Time",
    y="Factory to Customer Region",
    orientation="h",
    template="plotly_dark",
    title="🚚 Average Shipping Lead Time by Route",
    color="Shipping Lead Time",
    color_continuous_scale="plasma",
    hover_data={"Shipping Lead Time": True})

    fig1.update_layout(
    title_x=0.25,
    xaxis_title="Average Lead Time",
    yaxis_title="Route",
    height=350)

    fig1.update_traces(
    textposition="outside")

    # st.plotly_chart(fig1, width='stretch')

    fig2 = px.bar(
    Total_Shipments,
    x="Sales",
    y="Factory to Customer Region",
    orientation="h",
    template="plotly_dark",
    title="🚚 Route Performance by Total Sales",
    color="Sales",
    color_continuous_scale="plasma",
    hover_data={"Sales": True})

    fig2.update_layout(
    title_x=0.25,
    xaxis_title="Total Sales",
    yaxis_title="Route",
    height=350)

    fig2.update_traces(
    textposition="outside")

    # st.plotly_chart(fig2, width='stretch')
    # st.write("Selected Region:", region)
    # st.write("Filtered Rows:", len(filtered_df))

    return (fig1, fig2)

    


def geographic_map(filtered_df):
    st.title("🗺 Geographic Shipping Map")
    st.markdown("---")

    US_State = df[df['Country/Region'].astype(str).str.strip().str.upper().str.contains('UNITED STATES')]

    US_State['State/Province'] = US_State['State/Province'].astype(str).str.strip().str.upper()
    US_State = US_State[
    US_State['State/Province'].notna() &
    (US_State['State/Province'].str.strip() != "")]
    state_summary = US_State.groupby('State/Province', as_index=False).agg(
                    Total_Orders=('Order ID', 'count'),
                    Avg_Lead_Time=('Shipping Lead Time', 'mean')).round(2)

    # Top_states = US_State.groupby('State/Province')['Shipping Lead Time'].mean().round(2).sort_values(ascending=False).tail(10)
    Top_states = state_summary.sort_values('Avg_Lead_Time',ascending=False).tail(15)


    # Prepare the data for the heatmap's color intensity (Avg_Lead_Time)
    heatmap_values = Top_states.set_index('State/Province')['Avg_Lead_Time']

    # Create annotation strings combining Avg_Lead_Time and Total_Orders
    annotations_text = Top_states.apply(
        lambda row: f"{row['Avg_Lead_Time']:.0f} days\n({int(row['Total_Orders'])} orders)", axis=1).values.reshape(-1, 1)

    fig1,ax1 = plt.subplots(figsize=(15,8))  # ✅ IMPORTANT

    sns.heatmap(
    heatmap_values.to_frame(), 
    cmap='Purples', 
    annot=annotations_text, # Use the custom annotation strings
    fmt="s", # Format as string
    linewidths=0.5,
    cbar_kws={'label': 'Average Shipping Lead Time'},
    ax=ax1)

    ax1.set_title('Top 15 Performing US States (Shipping Analysis)')
    ax1.set_ylabel('State/Province')
    ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0)

    # st.plotply_chart(fig1, use_container_width=True)

    #Fig2
    state_summary['State_Code'] = state_summary['State/Province'].map({
    'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR',
    'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE',
    'DISTRICT OF COLUMBIA': 'DC', 'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI',
    'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS',
    'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS',
    'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
    'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY',
    'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
    'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
    'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV',
    'WISCONSIN': 'WI', 'WYOMING': 'WY'})

# Filter out any states that are not in the US or couldn't be mapped
    state_summary_us = state_summary.dropna(subset=['State_Code'])

    fig2 = px.choropleth(state_summary_us,
                    locations='State_Code',
                    locationmode="USA-states",
                    color='Total_Orders',
                    hover_name='State/Province', 
                    hover_data=['Total_Orders', 'Avg_Lead_Time'], 
                    color_continuous_scale="Viridis",
                    scope="usa",
                    title='🗺️ US Shipping Performance by State',
                    )
    fig2.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    fig2.update_layout(title={
        'text': "<b>🗺️ US Shipping Performance by State</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(size=22)})
    # st.plotly_chart(fig2, use_container_width=True)

    #Fig3

    region_congestion =  filtered_df.groupby('Region').agg(
                         Avg_Lead_Time=('Shipping Lead Time','mean'),
                         Shipment_Count=('Shipping Lead Time','count'),
                         Lead_Time_Std=('Shipping Lead Time','std')).round(2).sort_values(by='Avg_Lead_Time', ascending=False).reset_index()

    #Fig3
    fig3 = px.bar(
    region_congestion,
    x= "Avg_Lead_Time",
    y= "Region",
    orientation="h",
    template="plotly_dark",
    title="🌍 Regional Bottleneck Analysis",
    color="Avg_Lead_Time",
    color_continuous_scale="plasma",
    hover_data={"Avg_Lead_Time": True})

    fig3.update_layout(
    title_x=0.25,
    xaxis_title="Average Lead Time",
    yaxis_title="Region",
    height=350)

    fig3.update_layout(
    title={
        'text': "<b>🌍 Regional Bottleneck Analysis</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(size=22)})

    fig3.update_traces(
    textposition="outside")


    return (fig1,fig2,fig3)

def ship_mode(filtered_df):
    st.title("🚚 Ship Mode Comparison")
    st.markdown("---")
    
    shipmode_analysis = filtered_df.groupby('Ship Mode').agg({'Shipping Lead Time':'mean'}).sort_values('Shipping Lead Time', ascending=True).round(2).reset_index()
    Total_Orders = filtered_df.groupby('Ship Mode').agg({'Order ID':'count'}).sort_values('Order ID', ascending=False).round(2).reset_index()


    fig1 = px.bar(
    shipmode_analysis,
    x= "Shipping Lead Time",
    y= "Ship Mode",
    orientation="h",
    template="plotly_dark",
    title="Lead-Time V/S Ship Mode ",
    color="Shipping Lead Time",
    color_continuous_scale="plasma",
    hover_data={"Shipping Lead Time": True})

    fig1.update_layout(
    title_x=0.25,
    xaxis_title="Average Shipping Lead Time",
    yaxis_title="Ship Mode",
    height=350)

    fig1.update_layout(
    title={
        'text': "<b>⏳Lead Time V/S Ship Mode</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(size=24)})
    
    fig1.update_traces(
    textposition="outside")


    fig2 = px.pie(
    shipmode_analysis,
    values=shipmode_analysis['Shipping Lead Time'],
    names='Ship Mode',
    hole=0.6,
    color_discrete_sequence=[
    "#4B0082", "#6A0DAD", "#8A2BE2", "#BA55D3"]
    )

    fig2.update_layout(
    title={
        'text': "<b>🚛Lead Time Distribution by Ship Mode</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(size=24)})

    fig2.update_traces(
        textinfo='percent+label',
        textfont_size=12,
        marker=dict(line=dict(color='white', width=1))
    )

    fig2.update_layout(
        showlegend=True,
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
    )

    fig2.update_traces(
    marker=dict(
        line=dict(color='rgba(255,255,255,0.2)', width=2))
    )

    fig3 = px.bar(
    Total_Orders,
    x= "Order ID",
    y= "Ship Mode",
    orientation="h",
    template="plotly_dark",
    title="Total Orders V/S Ship Mode ",
    color="Order ID",
    color_continuous_scale="plasma",
    hover_data={"Order ID": True})

    fig3.update_layout(
    title_x=0.25,
    xaxis_title="Total Orders",
    yaxis_title="Ship Mode",
    height=350)

    fig3.update_layout(
    title={
        'text': "<b>📦Total Orders by Ship Mode</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(size=24)})
    
    fig3.update_traces(
    textposition="outside")

    fig4 = px.pie(
    Total_Orders,
    values=Total_Orders['Order ID'],
    names='Ship Mode',
    hole=0.6,
    color_discrete_sequence=[
    "#4B0082", "#6A0DAD", "#8A2BE2", "#BA55D3"]
    )

    fig4.update_layout(
    title={
        'text': "<b>🚛Total Orders Distribution by Ship Mode</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(size=24)})

    fig4.update_traces(
        textinfo='percent+label',
        textfont_size=12,
        marker=dict(line=dict(color='white', width=1))
    )

    fig4.update_layout(
        showlegend=True,
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
    )

    fig4.update_traces(
    marker=dict(
        line=dict(color='rgba(255,255,255,0.2)', width=2))
    )
    


    return(fig1,fig2,fig3,fig4)


def drilldown(filtered_df):
    st.title("🔍 Route Drilldown")
    st.markdown("---")
    
    state_perf = filtered_df.groupby('State/Province').agg({
    'Shipping Lead Time':'mean',
    'Order ID':'count',
    'Sales':'sum',
    'Gross Profit':'sum'}).sort_values('Shipping Lead Time', ascending=True).round(2).head(25).reset_index()

    top_orders = filtered_df.groupby('State/Province').agg({'Order ID':'count'}).sort_values('Order ID', ascending=False).head(25).reset_index()

    order_timelines = filtered_df.groupby("Order Date")["Shipping Lead Time"].mean().round(2).reset_index()


#Fig1
    fig1 = px.bar(
    state_perf,
    x= "Shipping Lead Time",
    y= "State/Province",
    orientation="h",
    template="plotly_dark",
    title="📍 State-Level Performance Insights",
    color="Shipping Lead Time",
    color_continuous_scale="plasma",
    hover_data={"Shipping Lead Time": True})

    fig1.update_layout(
    title_x=0.25,
    xaxis_title="Average Shipping Lead Time",
    yaxis_title="States",
    height=350)

    fig1.update_layout(
    title={
        'text': "<b>📍 State-Level Performance Insights by Lead Time</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(size=24)})
    
    fig1.update_layout(
    yaxis=dict(tickmode='linear'),
    height=650)
    
    fig1.update_traces(
    textposition="outside")

# Fig2
    fig2 = px.bar(
    top_orders,
    x= "Order ID",
    y= "State/Province",
    orientation="h",
    template="plotly_dark",
    title="📍 State-Level Performance Insights",
    color="Order ID",
    color_continuous_scale="plasma",
    hover_data={"Order ID": True})

    fig2.update_layout(
    title_x=0.25,
    xaxis_title="Average Shipping Lead Time",
    yaxis_title="States",
    height=350)

    fig2.update_layout(
    title={
        'text': "<b>📦State-Level Performance Insights by Orders</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(size=24)})
    
    fig2.update_layout(
    yaxis=dict(tickmode='linear'),
    height=650)
    
    fig2.update_traces(
    textposition="outside")



#Fig3

    fig3 = px.line(
        order_timelines,
        x = "Order Date",
        y = "Shipping Lead Time",
        title="📈 Shipping Lead Time Over Time",
        markers=True  # 👈 adds interactivity points
)

    fig3.update_layout(
        template="plotly_dark",  # 🔥 best for dark + purple theme
    
        title={
        "x": 0.5,
        "xanchor": "center",
        "font": dict(size=24)
        },

    # 🟣 Purple line styling
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

    # Axis styling
        xaxis=dict(
        title="Order Date",
        showgrid=False
        ),
        yaxis=dict(
        title="Average Lead Time",
        showgrid=True,
        gridcolor="rgba(128, 0, 128, 0.2)"  # light purple grid
        ),

    # Hover styling
        hovermode="x unified",

    # Legend
        showlegend=False)

# 🟣 Line customization
    fig3.update_traces(
        line=dict(
        color="#9b5de5",  # 🔥 purple
        width=3),
    marker=dict(
        size=6,
        color="#c77dff"
    ),
    hovertemplate=
    "<b>Date:</b> %{x}<br>" +
    "<b>Lead Time:</b> %{y} days<extra></extra>")

# Range slider (important for timeline)
    fig3.update_layout(
    xaxis_rangeslider_visible=True)
    fig3.update_layout(
    height=550,
    margin=dict(l=40, r=40, t=60, b=40))


    return(fig1,fig2,fig3)




# Navigation logic
if page == "Route Efficiency":
    fig1,fig2 = route_efficiency(filtered_df)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True, key="fig1")

    with col2:
        st.plotly_chart(fig2, use_container_width=True, key="fig2")


    st.markdown("---")
    st.write("Total Orders Per Product")
    st.write(
        filtered_df.groupby(['Division', 'Product Name', 'Factory']).size().reset_index(name='Total Orders').set_index('Division')
    )

elif page == "Geographic Map":
    fig1,fig2,fig3 = geographic_map(filtered_df)
    col1,col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig2, use_container_width=True, key="fig2")

    with col2:
        st.plotly_chart(fig3, use_container_width=True, key="fig3")

        
    st.markdown("### ⚡Performance of US States (Shipping Analysis)")
    st.pyplot(fig1)
    
elif page == "Ship Mode":
    fig1,fig2,fig3,fig4 = ship_mode(filtered_df)
    st.plotly_chart(fig1,use_container_width=True,key="fig1" )
    st.plotly_chart(fig2, use_container_width=True, key="fig2")
    st.plotly_chart(fig3, use_container_width=True, key="fig3")
    st.plotly_chart(fig4, use_container_width=True, key="fig4")

elif page == "Route Drilldown":
    fig1,fig2,fig3= drilldown(filtered_df)
    st.plotly_chart(fig1, use_container_width=True, key="fig1")
    st.plotly_chart(fig2, use_container_width=True, key="fig2")
    st.plotly_chart(fig3, use_container_width=True, key="fig3")


 

## Charts
