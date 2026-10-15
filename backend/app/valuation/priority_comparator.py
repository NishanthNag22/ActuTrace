
"""Compare defect-count priority with financial-impact priority."""

from collections import defaultdict
from math import sqrt


def _average_ranks(values: list[float]) -> list[float]:
    """Assign average ranks when two values are tied."""
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)

    index = 0
    while index < len(ordered):
        end = index + 1

        while (
            end < len(ordered)
            and ordered[end][1] == ordered[index][1]
        ):
            end += 1

        average_rank = ((index + 1) + end) / 2

        for position in range(index, end):
            original_index = ordered[position][0]
            ranks[original_index] = average_rank

        index = end

    return ranks


def _spearman_correlation(
    first_ranks: list[float],
    second_ranks: list[float],
) -> float | None:
    """Calculate Spearman correlation, including tied ranks."""
    if len(first_ranks) < 2:
        return None

    first_mean = sum(first_ranks) / len(first_ranks)
    second_mean = sum(second_ranks) / len(second_ranks)

    first_centered = [rank - first_mean for rank in first_ranks]
    second_centered = [rank - second_mean for rank in second_ranks]

    numerator = sum(
        first * second
        for first, second in zip(first_centered, second_centered)
    )

    first_variance = sum(value**2 for value in first_centered)
    second_variance = sum(value**2 for value in second_centered)

    denominator = sqrt(first_variance * second_variance)

    if denominator == 0:
        return None

    return numerator / denominator


def compare_priority_methods(
    defect_records: list[dict],
) -> dict:
    """
    Compare defect-type frequency with total absolute financial impact.

    Each record must contain:
        defect_type: category of data-quality defect
        impact: signed estimated financial impact

    Impact is aggregated by absolute value. This measures total impact
    magnitude, not the net effect of positive and negative impacts.
    """
    if not defect_records:
        raise ValueError("At least one defect record is required.")

    totals = defaultdict(
        lambda: {"count": 0, "total_absolute_impact": 0.0}
    )

    for record in defect_records:
        if "defect_type" not in record or "impact" not in record:
            raise ValueError(
                "Each record must contain defect_type and impact."
            )

        defect_type = record["defect_type"]

        if not isinstance(defect_type, str) or not defect_type.strip():
            raise ValueError("defect_type must be a non-empty string.")

        impact = record["impact"]

        if isinstance(impact, bool) or not isinstance(
            impact, (int, float)
        ):
            raise ValueError("impact must be a finite number.")

        impact = float(impact)

        if not (float("-inf") < impact < float("inf")):
            raise ValueError("impact must be a finite number.")

        totals[defect_type]["count"] += 1
        totals[defect_type]["total_absolute_impact"] += abs(impact)

    defect_types = list(totals)

    counts = [totals[name]["count"] for name in defect_types]
    impacts = [
        totals[name]["total_absolute_impact"]
        for name in defect_types
    ]

    count_ranks = _average_ranks(
        [-float(count) for count in counts]
    )
    impact_ranks = _average_ranks(
        [-impact for impact in impacts]
    )

    comparison = []

    for index, defect_type in enumerate(defect_types):
        comparison.append(
            {
                "defect_type": defect_type,
                "occurrence_count": totals[defect_type]["count"],
                "total_absolute_impact": round(impacts[index], 2),
                "count_rank": int(count_ranks[index])
                if count_ranks[index].is_integer()
                else count_ranks[index],
                "impact_rank": int(impact_ranks[index])
                if impact_ranks[index].is_integer()
                else impact_ranks[index],
            }
        )

    comparison.sort(key=lambda item: (item["impact_rank"], item["defect_type"]))

    return {
        "defect_type_count": len(defect_types),
        "spearman_rank_correlation": _spearman_correlation(
            count_ranks, impact_ranks
        ),
        "ranking_differs": any(
            item["count_rank"] != item["impact_rank"]
            for item in comparison
        ),
        "ranking_basis": {
            "count": "Number of records in each defect category",
            "impact": "Sum of absolute estimated impacts by category",
        },
        "results": comparison,
        "interpretation": (
            "This comparison ranks defect categories by frequency and "
            "total absolute estimated impact. It does not establish that "
            "one approach is universally better. Results depend on the "
            "defect population and the valuation model."
        ),
    }
