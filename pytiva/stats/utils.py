from scipy import stats as st
import pandas as pd


def test_group_means(
        samples,
        category_labels=None,
        anova_alpha=0.05,
        hsd_confidence_level=0.95
):
    """
    Perform 1-way ANOVA to check for differences between means in supplied samples and post-hoc pairwise comparisons
    using Tukey's Honestly Significant Difference test.

    :param samples: collection of collections, where each member collection contains sample values
    :param category_labels: optional set of human-readable labels; if provided, treated as ordered the same as samples
    :param anova_alpha: threshold for significance for one-way ANOVA
    :param hsd_confidence_level: target confidence level for ensuring pairwise comparisons of means are (honestly)
        significantly different
    :return: a tuple of (anova_dict, tukey_dict), with each containing results from the respective testing step
    """
    # consider: throw an exception if len(samples) differs from len(category_labels) and category_labels is not None

    # if category labels are not supplied, will just use zero-indexed labels
    # based on the number of collections in samples
    if category_labels is None:
        category_labels = [i for i in range(len(samples))]

    category_index_dict = {i: category_labels[i] for i in range(len(category_labels))}

    anova_result = st.f_oneway(*samples)
    anova_dict = {
        'f_statistic': anova_result[0],
        'p_value': anova_result[1],
        'alpha': anova_alpha,
        'reject_h0': anova_result[1] < anova_alpha
    }

    # Tukey HSD part
    hsd_result = st.tukey_hsd(*samples)
    hsd_columns, hsd_data = ["Group 1", "Group 2", "Statistic", "p-value", "Lower CI", "Upper CI"], []
    hsd_ci = hsd_result.confidence_interval(confidence_level=hsd_confidence_level)
    key_pairs = [(k1, k2) for k1 in category_index_dict.keys() for k2 in category_index_dict.keys() if k1 != k2]
    for k in key_pairs:
        hsd_data.append([category_index_dict[k[0]],
                         category_index_dict[k[1]],
                         hsd_result.statistic[k],
                         hsd_result.pvalue[k],
                         hsd_ci.low[k],
                         hsd_ci.high[k]
                         ])

    hsd_df = pd.DataFrame(hsd_data, columns=hsd_columns)
    hsd_df["reject_h0"] = hsd_df["p-value"] < 1 - hsd_confidence_level

    hsd_statsig_pairs = [(v["Group 1"], v["Group 2"]) for i, v in
                         hsd_df.loc[hsd_df["reject_h0"]][["Group 1", "Group 2"]].iterrows()]
    hsd_non_statsig_pairs = [(v["Group 1"], v["Group 2"]) for i, v in
                             hsd_df.loc[~hsd_df["reject_h0"]][["Group 1", "Group 2"]].iterrows()]

    hsd_dict = {
        'confidence_level': hsd_confidence_level,
        'result_df': hsd_df,
        'statsig_pairs': hsd_statsig_pairs,
        'non_statsig_pairs': hsd_non_statsig_pairs
    }

    return anova_dict, hsd_dict


def ci_from_series(series, target_ci=0.95, round_dec=6):
    """
    Determine a confidence interval using supplied pandas Series (or GroupBy[col]) object, target confidence interval,
    and optional number of decimal places to round the values. Assumes numeric data.

    :param series: pandas Series (or GroupBy[col]) object, to which scipy.stats.sem() and mean() will be applied during the
        calculations
    :param target_ci: desired confidence interval as a float-like, default 0.95
    :param round_dec: number of decimal places to round the resulting bounds as an int-like, or None
    :return: 3-tuple of (CI lower bound, CI upper bound, and calculated standard error of mean)
    """
    sem = st.sem(series, ddof=0)
    lower = float(sem * st.norm.ppf((1 - target_ci) / 2) + series.mean())
    upper = float(sem * st.norm.ppf(1 - (1 - target_ci) / 2) + series.mean())

    if round_dec is not None:
        lower = round(lower, round_dec)
        upper = round(upper, round_dec)
    return lower, upper, sem


def describe_plus(data, strata_cols, numeric_cols=None, ci=0.95, ci_round_dec=6):
    """
    Generates descriptive statistics using pandas DataFrame.describe() or Series.describe() as foundation, plus a
    standard error of mean (SEM) and confidence interval for the mean (default 95% confidence interval).
    Returns dictionary of

    :param data:
    :param strata_cols:
    :param numeric_cols:
    :param ci:
    :param ci_round_dec:
    :return: dictionary of
    """
    if numeric_cols is None:
        # infer from pandas's own DataFrame.describe() results
        if isinstance(data.describe(), pd.DataFrame):
            numeric_cols = data.describe().columns
        else:
            numeric_cols = [data.describe().name]

    describe_results = dict()

    for stratum_label in strata_cols:
        described_collection = list()
        for measure_label in numeric_cols:
            gb = data.groupby(stratum_label)
            described = gb[measure_label].describe()
            described['measure'] = measure_label
            ci_result = gb[measure_label].apply(lambda x: ci_from_series(x, target_ci=ci, round_dec=ci_round_dec))
            described['sem'] = ci_result.apply(lambda x: x[2])
            described[f'mean_{ci}_ci'] = ci_result.apply(lambda x: '{} – {}'.format(x[0], x[1]))
            described_collection.append(described)

        df_described = pd.concat(described_collection).reset_index().set_index(['measure', stratum_label])
        describe_results[stratum_label] = df_described

    return describe_results
