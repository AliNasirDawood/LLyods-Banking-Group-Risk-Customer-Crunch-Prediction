import plotly.express as px

def plot_histogram(df, x_column, title, x_label=None, y_label=None, color_column=None, barmode='overlay'):
    """
    Generic function to plot a histogram.
    :param df: DataFrame containing the data
    :param x_column: Column name for the x-axis
    :param title: Title of the plot
    :param x_label: Label for the x-axis (optional)
    :param y_label: Label for the y-axis (optional)
    :param color_column: Column for color differentiation (optional)
    :param barmode: Type of histogram (default: 'overlay', other options: 'stack')
    :return: Plotly figure
    """
    fig = px.histogram(df, x=x_column, color=color_column, barmode=barmode, title=title)
    fig.update_layout(
        xaxis_title=x_label if x_label else x_column,
        yaxis_title=y_label if y_label else 'Count',
        template="plotly_white",  # Clean professional design
        title_x=0.5  # Center the title
    )
    fig.update_traces(marker=dict(line=dict(width=1, color='black')))  # Add black borders for clarity
    return fig


def plot_pie(df, names_column, title, color_column=None):
    """
    Generic function to plot a pie chart.
    :param df: DataFrame containing the data
    :param names_column: Column name for the categories (values will be used as pie slices)
    :param title: Title of the plot
    :param color_column: Column to define color groups (optional)
    :return: Plotly figure
    """
    fig = px.pie(df, names=names_column, color=color_column, title=title, hole=0.3)  # Donut chart style
    fig.update_traces(textinfo='percent+label', pull=[0.1 for _ in range(len(df))])  # Pull out slices for emphasis
    fig.update_layout(
        title_x=0.5,  # Center the title
        template="plotly_white"  # Clean professional design
    )
    return fig


def plot_box(df, x_column, y_column, title, x_label=None, y_label=None, color_column=None):
    """
    Generic function to plot a box plot.
    :param df: DataFrame containing the data
    :param x_column: Column for the x-axis (categorical)
    :param y_column: Column for the y-axis (numeric)
    :param title: Title of the plot
    :param x_label: Label for the x-axis (optional)
    :param y_label: Label for the y-axis (optional)
    :param color_column: Column for color differentiation (optional)
    :return: Plotly figure
    """
    fig = px.box(df, x=x_column, y=y_column, color=color_column, title=title)
    fig.update_layout(
        xaxis_title=x_label if x_label else x_column,
        yaxis_title=y_label if y_label else y_column,
        template="plotly_white",
        title_x=0.5  # Center the title
    )
    fig.update_traces(boxmean='sd', jitter=0.1, marker=dict(size=6))  # Enhance box plot readability
    return fig


def plot_bar(df, x_column, y_column, title, x_label=None, y_label=None, color_column=None, orientation='v'):
    """
    Generic function to plot a bar chart.
    :param df: DataFrame containing the data
    :param x_column: Column for the x-axis (categorical)
    :param y_column: Column for the y-axis (numeric)
    :param title: Title of the plot
    :param x_label: Label for the x-axis (optional)
    :param y_label: Label for the y-axis (optional)
    :param color_column: Column for color differentiation (optional)
    :param orientation: Bar orientation ('v' for vertical, 'h' for horizontal)
    :return: Plotly figure
    """
    fig = px.bar(df, x=x_column, y=y_column, color=color_column, title=title, orientation=orientation)
    fig.update_layout(
        xaxis_title=x_label if x_label else x_column,
        yaxis_title=y_label if y_label else y_column,
        template="plotly_white",
        title_x=0.5  # Center the title
    )
    fig.update_traces(marker=dict(line=dict(width=1, color='black')))  # Add black borders for clarity
    return fig


def plot_scatter(df, x_column, y_column, title, x_label=None, y_label=None, color_column=None):
    """
    Generic function to plot a scatter plot.
    :param df: DataFrame containing the data
    :param x_column: Column for the x-axis
    :param y_column: Column for the y-axis
    :param title: Title of the plot
    :param x_label: Label for the x-axis (optional)
    :param y_label: Label for the y-axis (optional)
    :param color_column: Column for color differentiation (optional)
    :return: Plotly figure
    """
    fig = px.scatter(df, x=x_column, y=y_column, color=color_column, title=title)
    fig.update_layout(
        xaxis_title=x_label if x_label else x_column,
        yaxis_title=y_label if y_label else y_column,
        template="plotly_white",
        title_x=0.5  # Center the title
    )
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color='black')))  # Marker styling
    return fig
