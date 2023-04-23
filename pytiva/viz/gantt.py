import pandas as pd
import matplotlib.pyplot as plt


def activity_data_to_gantt_data(
        df_data, strata=['activity'], start_col='activity_start',
        end_col='activity_end', duration_col='duration',
        strata_separator=';', include_label_in_stratification=False
):
    """
    Generate data for a gantt chart, i.e. a sorted horizontal bar chart
    of activities where x is time and y is the activities.

    Starts, durations, etc. are all generated in terms of seconds.
    """

    _gantt_task_label = 'gtask'
    _gantt_start_label = 'gstart'
    _gantt_end_label = 'gend'
    _gantt_duration_label = 'gduration'

    # sort asc
    df_data = df_data.sort_values(by=start_col, ascending=True)

    # create empty DataFrame with the same index as the incoming activity data
    df_gantt = pd.DataFrame(index=df_data.index)

    # generate task label entries according to intended stratification
    # if strata is only ['activity'], this step (inefficiently) duplicates
    # the existing activity labels
    for i, row in df_data.iterrows():
        df_gantt.loc[i, _gantt_task_label] = strata_separator.join(
            f"{stratum}:{row[stratum]}" if include_label_in_stratification
            else row[stratum]
            for stratum in strata
        )

    # create unique label for each task
    # in effect, deal with possibility of repeat labels to not confuse the charting
    a_counts = {a: 0 for a in df_gantt[_gantt_task_label].unique()}
    for i, row in df_gantt.iterrows():
        activity = df_gantt[_gantt_task_label].loc[i]
        count = a_counts[activity] + 1
        df_gantt.loc[i, _gantt_task_label] = f"{activity} {count}"
        a_counts[activity] = count

    g_lower_bound = df_data[start_col].min()

    df_gantt[_gantt_start_label] = df_data[start_col].apply(lambda x: (x - g_lower_bound).total_seconds())

    df_gantt[_gantt_duration_label] = df_data[duration_col].apply(lambda x: x.total_seconds())

    return df_gantt.reset_index(drop=True)


def gantt_plot(gantt_df, filepath_out=None, task_col='gtask', start_col='gstart',
               duration_col='gduration', figsize=(20, 30), hide_xaxis_label=True,
               title=None):
    plt.figure(figsize=figsize)
    plt.title(title)
    plt.barh(y=gantt_df[task_col],
             left=gantt_df[start_col],
             width=gantt_df[duration_col])
    plt.gca().invert_yaxis()
    plt.gca().axes.xaxis.set_visible(not hide_xaxis_label)

    if filepath_out is not None:
        plt.savefig(filepath_out)

    return plt
