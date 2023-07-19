from scipy import stats as st
import pandas as pd


def test_group_means(
        samples,
        category_labels=None,
        anova_alpha=0.05,
        hsd_confidence_level=0.95
):
    """
    Perform 1-way ANOVA to check for differences between means in supplied samples and, if ANOVA is statistically
    significant, proceed with post-hoc pairwise comparisons using Tukey's Honestly Significant Difference test.

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
        'p_value': anova_result[1]
    }

    if anova_dict['p_value'] < anova_alpha:
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

    else:
        # no Tukey HSD if ANOVA was not statsig
        hsd_dict = None

    return anova_dict, hsd_dict
