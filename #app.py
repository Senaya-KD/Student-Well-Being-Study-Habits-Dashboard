# ----------------------------
# Student Well-Being & Study Habits Dashboard
# ----------------------------

import pandas as pd
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px

# ----------------------------
# Load data
# ----------------------------
DATA_PATH = "data/clean_survey.csv"
df = pd.read_csv(DATA_PATH)

# ----------------------------
# Initialize the app
# ----------------------------
app = Dash(__name__)
server = app.server
app.title = "Student Well-Being & Study Habits Dashboard"

# ----------------------------
# App layout (page structure)
# ----------------------------
app.layout = html.Div([
    html.H1("🎓 Student Well-Being & Study Habits Dashboard",
            style={"textAlign": "center", "color": "#2E86C1"}),

    # KPI Row
    html.Div([
        html.Div(id="total_students", className="card"),
        html.Div(id="avg_gpa", className="card"),
        html.Div(id="avg_stress", className="card"),
        html.Div(id="avg_sleep", className="card"),
        html.Div(id="percent_satisfied", className="card")
    ], style={"display": "flex", "justifyContent": "space-around"}),

    html.Hr(),

    # Filters
    html.Div([
        html.Label("Program of Study"),
        dcc.Dropdown(
            options=[{"label": i, "value": i} for i in sorted(df["program_of_study"].unique())],
            id="program_filter",
            placeholder="Select program",
            style={"width": "200px"}
        ),

        html.Label("Gender"),
        dcc.Dropdown(
            options=[{"label": i, "value": i} for i in df["gender"].unique()],
            id="gender_filter",
            placeholder="Select gender",
            style={"width": "200px"}
        ),

        html.Label("Stress Band"),
        dcc.Dropdown(
            options=[{"label": i, "value": i} for i in df["stress_band"].unique()],
            id="stress_filter",
            placeholder="Select stress band",
            style={"width": "200px"}
        ),
    ], style={"display": "flex", "gap": "40px", "justifyContent": "center"}),

    html.Hr(),

    # Charts section (single column)
    html.Div([
        dcc.Graph(id="stress_gpa_chart"),
        dcc.Graph(id="sleep_gpa_chart"),
        dcc.Graph(id="study_gpa_chart"),
        dcc.Graph(id="motivation_time_chart"),
        dcc.Graph(id="satisfaction_chart")
    ], style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "gap": "25px"
    }),

    html.Hr(),

    # Drill-down table
    html.Div([
        html.H3("Drill-Down Details"),
        dash_table.DataTable(
            id="drilldown_table",
            page_size=10,
            style_table={"overflowX": "auto", "width": "95%", "margin": "0 auto"}
        )
    ]),

    html.P(id="update_time", style={"textAlign": "right", "color": "gray"})
])

# ----------------------------
# Callback: KPI Cards
# ----------------------------
@app.callback(
    Output("total_students", "children"),
    Output("avg_gpa", "children"),
    Output("avg_stress", "children"),
    Output("avg_sleep", "children"),
    Output("percent_satisfied", "children"),
    Input("program_filter", "value"),
    Input("gender_filter", "value"),
    Input("stress_filter", "value")
)
def update_kpis(program, gender, stress):
    filtered_df = df.copy()

    if program:
        filtered_df = filtered_df[filtered_df["program_of_study"] == program]
    if gender:
        filtered_df = filtered_df[filtered_df["gender"] == gender]
    if stress:
        filtered_df = filtered_df[filtered_df["stress_band"] == stress]

    total_students = f"👩‍🎓 Total Students: {len(filtered_df)}"
    avg_gpa = f"🎯 Avg GPA: {filtered_df['average_gpa'].mean():.2f}"
    avg_stress = f"😥 Avg Stress: {filtered_df['stress_level'].mean():.1f}"
    avg_sleep = f"😴 Avg Sleep: {filtered_df['sleep_hours_num'].mean():.1f} hrs"
    satisfied = filtered_df[filtered_df['learning_satisfaction'] >= 4]
    percent_satisfied = f"💖 % Satisfied: {len(satisfied)/len(filtered_df)*100:.1f}%" if len(filtered_df)>0 else "💖 % Satisfied: 0%"

    return total_students, avg_gpa, avg_stress, avg_sleep, percent_satisfied

# ----------------------------
# Callback: Stress vs GPA chart
# ----------------------------
@app.callback(
    Output("stress_gpa_chart", "figure"),
    Input("program_filter", "value"),
    Input("gender_filter", "value"),
    Input("stress_filter", "value")
)
def update_stress_gpa_chart(program, gender, stress):
    filtered_df = df.copy()

    if program:
        filtered_df = filtered_df[filtered_df["program_of_study"] == program]
    if gender:
        filtered_df = filtered_df[filtered_df["gender"] == gender]
    if stress:
        filtered_df = filtered_df[filtered_df["stress_band"] == stress]

    fig = px.box(
        filtered_df,
        x="stress_band",
        y="average_gpa",
        color="stress_band",
        title="🎯 GPA Distribution by Stress Level",
        labels={"stress_band": "Stress Band", "average_gpa": "Average GPA"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(title_x=0.5, plot_bgcolor="white", paper_bgcolor="white")
    return fig

# ----------------------------
# Callback: Sleep vs GPA chart
# ----------------------------
@app.callback(
    Output("sleep_gpa_chart", "figure"),
    Input("program_filter", "value"),
    Input("gender_filter", "value"),
    Input("stress_filter", "value")
)
def update_sleep_gpa_chart(program, gender, stress):
    filtered_df = df.copy()

    if program:
        filtered_df = filtered_df[filtered_df["program_of_study"] == program]
    if gender:
        filtered_df = filtered_df[filtered_df["gender"] == gender]
    if stress:
        filtered_df = filtered_df[filtered_df["stress_band"] == stress]

    sleep_avg = filtered_df.groupby("sleep_band", as_index=False)["average_gpa"].mean()
    fig = px.bar(
        sleep_avg,
        x="sleep_band",
        y="average_gpa",
        color="sleep_band",
        title="😴 Average GPA by Sleep Quality",
        labels={"sleep_band": "Sleep Band", "average_gpa": "Average GPA"},
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_layout(title_x=0.5, plot_bgcolor="white", paper_bgcolor="white")
    return fig

# ----------------------------
# Callback: Study Hours vs GPA (Scatter Plot)
# ----------------------------
@app.callback(
    Output("study_gpa_chart", "figure"),
    Input("program_filter", "value"),
    Input("gender_filter", "value"),
    Input("stress_filter", "value")
)
def update_study_gpa_chart(program, gender, stress):
    filtered_df = df.copy()

    if program:
        filtered_df = filtered_df[filtered_df["program_of_study"] == program]
    if gender:
        filtered_df = filtered_df[filtered_df["gender"] == gender]
    if stress:
        filtered_df = filtered_df[filtered_df["stress_band"] == stress]

    fig = px.scatter(
        filtered_df,
        x="study_hours_weekdays_num",
        y="average_gpa",
        color="stress_band",
        hover_data=["program_of_study", "gender", "sleep_hours_num"],
        title="📘 Study Hours (Weekdays) vs GPA",
        labels={"study_hours_weekdays_num": "Study Hours (Weekdays)", "average_gpa": "Average GPA"},
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_layout(title_x=0.5, plot_bgcolor="white", paper_bgcolor="white")
    return fig

# ----------------------------
# Callback: Motivation & Time Management by Program (Grouped Bar)
# ----------------------------
@app.callback(
    Output("motivation_time_chart", "figure"),
    Input("program_filter", "value"),
    Input("gender_filter", "value"),
    Input("stress_filter", "value")
)
def update_motivation_time_chart(program, gender, stress):
    filtered_df = df.copy()

    if program:
        filtered_df = filtered_df[filtered_df["program_of_study"] == program]
    if gender:
        filtered_df = filtered_df[filtered_df["gender"] == gender]
    if stress:
        filtered_df = filtered_df[filtered_df["stress_band"] == stress]

    if filtered_df.empty:
        return px.bar(title="No data available for the selected filters")

    summary = (
        filtered_df.groupby(["program_of_study", "gender"])
        [["motivation_level", "time_management"]]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        summary,
        x="program_of_study",
        y=["motivation_level", "time_management"],
        color="gender",
        barmode="group",
        title="💪 Motivation & Time Management by Program and Gender",
        labels={"program_of_study": "Program of Study", "value": "Average Score", "variable": "Skill Type"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(title_x=0.5, plot_bgcolor="white", paper_bgcolor="white", font=dict(size=13))
    return fig

# ----------------------------
# Callback: Student Satisfaction Distribution (Pie Chart)
# ----------------------------
@app.callback(
    Output("satisfaction_chart", "figure"),
    Input("program_filter", "value"),
    Input("gender_filter", "value"),
    Input("stress_filter", "value")
)
def update_satisfaction_chart(program, gender, stress):
    filtered_df = df.copy()

    if program:
        filtered_df = filtered_df[filtered_df["program_of_study"] == program]
    if gender:
        filtered_df = filtered_df[filtered_df["gender"] == gender]
    if stress:
        filtered_df = filtered_df[filtered_df["stress_band"] == stress]

    if filtered_df.empty:
        return px.pie(title="No data available for the selected filters")

    satisfaction_counts = filtered_df["learning_satisfaction"].value_counts().reset_index()
    satisfaction_counts.columns = ["Satisfaction", "Count"]

    fig = px.pie(
        satisfaction_counts,
        values="Count",
        names="Satisfaction",
        title="💖 Learning Satisfaction Distribution",
        color="Satisfaction",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    fig.update_traces(textinfo="percent+label", pull=[0.03]*len(satisfaction_counts))
    fig.update_layout(title_x=0.5, plot_bgcolor="white", paper_bgcolor="white", font=dict(size=13))
    return fig

# ----------------------------
# Run app
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
