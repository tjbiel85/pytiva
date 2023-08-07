import matplotlib.pyplot as plt
from scipy import stats as st
import seaborn as sn

# TODO: move this to package
MEAN_LABEL = 'mean'
SEM_LABEL = 'sem'
LOWER_CI_LABEL = 'lower_ci'
UPPER_CI_LABEL = 'upper_ci'


def df_mean_rate_by_category(
        df_data,
        metric_col,
        category_col,
        timestamp_col=None,
        timestamp_bin_func=lambda x: x.minute + x.hour * 60,
        include_ci=None):
    """
    timestamp_col: a label for datetime column, or will use index if None (default behavior)
    plot_ci: False or a confidence interval (expressed like 0.95) to be shaded above and below the mean

    """
    _timestamp_bin_label = 'timestamp_bin'

    if timestamp_col is None:
        df_data[_timestamp_bin_label] = df_data.index.map(timestamp_bin_func)
    else:
        df_data[_timestamp_bin_label] = df_data[timestamp_col].apply(timestamp_bin_func)

    df_mean = df_data.groupby([category_col, _timestamp_bin_label])[metric_col].mean().to_frame().rename(
        columns={metric_col: MEAN_LABEL})

    if include_ci:
        df_mean[SEM_LABEL] = df_data.groupby([category_col, _timestamp_bin_label])[metric_col].apply(st.sem)
        df_mean[UPPER_CI_LABEL] = st.norm.ppf(1 - (1 - include_ci) / 2) * df_mean[SEM_LABEL] + df_mean[MEAN_LABEL]
        df_mean[LOWER_CI_LABEL] = st.norm.ppf((1 - include_ci) / 2) * df_mean[SEM_LABEL] + df_mean[MEAN_LABEL]

    return df_mean


def fig_lineplot_mean_rate_by_category(
        plot_data,
        plot_value_label='mean',
        palette='muted',
        plot_facecolor='whitesmoke',
        fig_facecolor='white',
        figsize=(11, 8.5),
        linealpha=0.8,
        linewidth=2,
        fill_ci=False,
        cialpha=0.2,
        upper_ci_label=UPPER_CI_LABEL,
        lower_ci_label=LOWER_CI_LABEL,
        # xaxis_label='Hour of day'
):
    sn.set_palette(palette)
    sn.set_theme(rc={
        'figure.figsize': figsize,
        'lines.linewidth': linewidth
    })

    fig, ax = plt.subplots()
    ax.set_facecolor(plot_facecolor)
    figure_lines = []
    figure_line_labels = []

    # could be days of week, or shift labels, or something else
    for category in plot_data.index.levels[0]:
        # this really only works for one-minute bin sizes
        # x = plot_data[plot_value_label].unstack(level=0).index.values/60

        # so this version figures out how many bins there are assuming a 24 hour day
        x = plot_data[plot_value_label].unstack(level=0).index.values / (len(plot_data.unstack(level=0).index) / 24)
        line, = ax.plot(
            x,
            plot_data.unstack(level=0)[(plot_value_label, category)],
            alpha=linealpha
        )
        figure_lines.append(line)
        figure_line_labels.append(category)

        if fill_ci:
            ax.fill_between(
                x,
                plot_data.unstack(level=0)[(lower_ci_label, category)],
                plot_data.unstack(level=0)[(upper_ci_label, category)],
                alpha=cialpha,
                linewidth=0,
                color=line.get_color()
            )

    legend = ax.legend(figure_lines, figure_line_labels)
    frame = legend.get_frame()
    frame.set_facecolor(fig_facecolor)
    plt.xticks(ticks=[x for x in range(0, 24, 4)],
               labels=['{:02d}:00'.format(x) for x in range(0, 24, 4)],
               rotation=15)

    ax.set_ylim(ymin=0)
    ax.set_xlim(xmin=0, xmax=24)

    plt.tight_layout()
    return ax
