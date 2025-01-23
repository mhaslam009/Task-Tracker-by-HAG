import pandas as pd
import plotly.express as px

# Load categorized events from CSV and clean data
def load_events(filename='categorized_calendar_events.csv'):
    try:
        df = pd.read_csv(filename)
        # Drop rows where Category or Duration (hours) is NaN
        df.dropna(subset=["Category", "Duration (hours)"], inplace=True)
        # Ensure Duration (hours) is numeric and handle any non-numeric entries
        df["Duration (hours)"] = pd.to_numeric(df["Duration (hours)"], errors='coerce')
        # Drop rows where Duration (hours) could not be converted to numeric
        df.dropna(subset=["Duration (hours)"], inplace=True)
        return df
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please run calendar_tracker.py first.")
        return None

# Visualize the total duration by category and save as HTML
def visualize_duration_by_category(df, output_file='total_duration_by_category.html'):
    # Group by "Category" and sum the "Duration (hours)"
    category_durations = df.groupby("Category")["Duration (hours)"].sum().reset_index()

    # Create an interactive bar chart with Plotly
    fig = px.bar(
        category_durations, 
        x="Category", 
        y="Duration (hours)", 
        labels={'Duration (hours)': 'Total Duration (hours)', 'Category': 'Event Category'},
        title='Total Duration by Event Category',
        text="Duration (hours)",  # Add text labels for hours on top of bars
        color="Category",  # Different color for each bar
        color_discrete_sequence=px.colors.qualitative.Pastel  # Pastel color palette
    )

    # Update layout for better readability and aesthetics
    fig.update_layout(
        xaxis_title="Event Category",
        yaxis_title="Total Duration (hours)",
        title_x=0.5,
        template="plotly_white",
        font=dict(size=14),
        bargap=0.3,  # Separate the bars for clarity
    )

    # Customize text and hover tooltip
    fig.update_traces(
        texttemplate="Cat: %{x}<br>Hours: %{y:.2f}",  # Show category and hours on top of bars
        textposition="outside",  # Position text labels above the bars
        hovertemplate="Category: %{x}<br>Total Duration: %{y:.2f} hours"  # Tooltip content
    )

    # Save the interactive chart to an HTML file
    fig.write_html(output_file)
    print(f"Visualization saved to {output_file}")

if __name__ == '__main__':
    df = load_events()
    if df is not None:
        visualize_duration_by_category(df)
