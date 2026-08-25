"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework Tests

Analytics metric and aggregation contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    AnalyticsAggregationType,
    AnalyticsMetric,
)


def test_analytics_aggregation_type_is_string_enum():

    assert issubclass(
        AnalyticsAggregationType,
        str,
    )


def test_analytics_aggregation_type_defines_count():

    assert (
        AnalyticsAggregationType.COUNT.value
        == "count"
    )


def test_analytics_aggregation_type_defines_sum():

    assert (
        AnalyticsAggregationType.SUM.value
        == "sum"
    )


def test_analytics_aggregation_type_defines_average():

    assert (
        AnalyticsAggregationType.AVERAGE.value
        == "average"
    )


def test_analytics_aggregation_type_defines_minimum():

    assert (
        AnalyticsAggregationType.MINIMUM.value
        == "minimum"
    )


def test_analytics_aggregation_type_defines_maximum():

    assert (
        AnalyticsAggregationType.MAXIMUM.value
        == "maximum"
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "count",
            AnalyticsAggregationType.COUNT,
        ),
        (
            "COUNT",
            AnalyticsAggregationType.COUNT,
        ),
        (
            " count ",
            AnalyticsAggregationType.COUNT,
        ),
        (
            "sum",
            AnalyticsAggregationType.SUM,
        ),
        (
            "SUM",
            AnalyticsAggregationType.SUM,
        ),
        (
            " sum ",
            AnalyticsAggregationType.SUM,
        ),
        (
            "average",
            AnalyticsAggregationType.AVERAGE,
        ),
        (
            "AVERAGE",
            AnalyticsAggregationType.AVERAGE,
        ),
        (
            " average ",
            AnalyticsAggregationType.AVERAGE,
        ),
        (
            "minimum",
            AnalyticsAggregationType.MINIMUM,
        ),
        (
            "MINIMUM",
            AnalyticsAggregationType.MINIMUM,
        ),
        (
            " minimum ",
            AnalyticsAggregationType.MINIMUM,
        ),
        (
            "maximum",
            AnalyticsAggregationType.MAXIMUM,
        ),
        (
            "MAXIMUM",
            AnalyticsAggregationType.MAXIMUM,
        ),
        (
            " maximum ",
            AnalyticsAggregationType.MAXIMUM,
        ),
    ],
)
def test_analytics_aggregation_type_normalizes_string(
    value,
    expected,
):

    assert (
        AnalyticsAggregationType.normalize(
            value
        )
        is expected
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "median",
        "weighted_average",
        "unsupported",
        None,
        123,
        object(),
    ],
)
def test_analytics_aggregation_type_rejects_unsupported_values(
    value,
):

    with pytest.raises(
        ValueError,
        match="Analytics aggregation type",
    ):
        AnalyticsAggregationType.normalize(
            value
        )


def test_analytics_aggregation_type_normalize_preserves_enum():

    aggregation = (
        AnalyticsAggregationType.COUNT
    )

    assert (
        AnalyticsAggregationType.normalize(
            aggregation
        )
        is aggregation
    )


def test_analytics_aggregation_type_codes():

    assert (
        AnalyticsAggregationType.COUNT.code
        == "count"
    )

    assert (
        AnalyticsAggregationType.SUM.code
        == "sum"
    )

    assert (
        AnalyticsAggregationType.AVERAGE.code
        == "average"
    )

    assert (
        AnalyticsAggregationType.MINIMUM.code
        == "minimum"
    )

    assert (
        AnalyticsAggregationType.MAXIMUM.code
        == "maximum"
    )


def test_analytics_aggregation_type_labels():

    assert (
        AnalyticsAggregationType.COUNT.label
        == "Count"
    )

    assert (
        AnalyticsAggregationType.SUM.label
        == "Sum"
    )

    assert (
        AnalyticsAggregationType.AVERAGE.label
        == "Average"
    )

    assert (
        AnalyticsAggregationType.MINIMUM.label
        == "Minimum"
    )

    assert (
        AnalyticsAggregationType.MAXIMUM.label
        == "Maximum"
    )


def test_analytics_aggregation_type_to_dict():

    assert (
        AnalyticsAggregationType.SUM.to_dict()
        == {
            "code": "sum",
            "label": "Sum",
        }
    )


def test_analytics_aggregation_types_are_unique():

    values = [
        aggregation.value
        for aggregation
        in AnalyticsAggregationType
    ]

    assert len(values) == len(
        set(values)
    )


def test_analytics_aggregation_type_iteration_order():

    assert list(
        AnalyticsAggregationType
    ) == [
        AnalyticsAggregationType.COUNT,
        AnalyticsAggregationType.SUM,
        AnalyticsAggregationType.AVERAGE,
        AnalyticsAggregationType.MINIMUM,
        AnalyticsAggregationType.MAXIMUM,
    ]


def test_analytics_metric_requires_code():

    with pytest.raises(
        ValueError,
        match="Analytics metric code",
    ):
        AnalyticsMetric(
            code=" ",
            name="Total Volunteers",
            aggregation=(
                AnalyticsAggregationType.COUNT
            ),
        )


def test_analytics_metric_requires_string_code():

    with pytest.raises(
        ValueError,
        match="Analytics metric code",
    ):
        AnalyticsMetric(
            code=123,
            name="Total Volunteers",
            aggregation=(
                AnalyticsAggregationType.COUNT
            ),
        )


def test_analytics_metric_requires_name():

    with pytest.raises(
        ValueError,
        match="Analytics metric name",
    ):
        AnalyticsMetric(
            code="total_volunteers",
            name=" ",
            aggregation=(
                AnalyticsAggregationType.COUNT
            ),
        )


def test_analytics_metric_requires_string_name():

    with pytest.raises(
        ValueError,
        match="Analytics metric name",
    ):
        AnalyticsMetric(
            code="total_volunteers",
            name=123,
            aggregation=(
                AnalyticsAggregationType.COUNT
            ),
        )


def test_analytics_metric_normalizes_code():

    metric = AnalyticsMetric(
        code="  total_volunteers  ",
        name="Total Volunteers",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
    )

    assert (
        metric.code
        == "total_volunteers"
    )


def test_analytics_metric_normalizes_name():

    metric = AnalyticsMetric(
        code="total_volunteers",
        name="  Total Volunteers  ",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
    )

    assert (
        metric.name
        == "Total Volunteers"
    )


@pytest.mark.parametrize(
    "aggregation, expected",
    [
        (
            "count",
            AnalyticsAggregationType.COUNT,
        ),
        (
            "COUNT",
            AnalyticsAggregationType.COUNT,
        ),
        (
            " sum ",
            AnalyticsAggregationType.SUM,
        ),
        (
            "average",
            AnalyticsAggregationType.AVERAGE,
        ),
        (
            "minimum",
            AnalyticsAggregationType.MINIMUM,
        ),
        (
            "maximum",
            AnalyticsAggregationType.MAXIMUM,
        ),
    ],
)
def test_analytics_metric_normalizes_aggregation(
    aggregation,
    expected,
):

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=aggregation,
        source="value",
    )

    assert (
        metric.aggregation
        is expected
    )


def test_analytics_metric_rejects_invalid_aggregation():

    with pytest.raises(
        ValueError,
        match="analytics aggregation type",
    ):
        AnalyticsMetric(
            code="metric",
            name="Metric",
            aggregation="unsupported",
            source="value",
        )


def test_analytics_metric_rejects_invalid_aggregation_type():

    with pytest.raises(
        ValueError,
        match="Analytics metric aggregation",
    ):
        AnalyticsMetric(
            code="metric",
            name="Metric",
            aggregation=123,
            source="value",
        )


def test_count_metric_does_not_require_source():

    metric = AnalyticsMetric(
        code="total_volunteers",
        name="Total Volunteers",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
    )

    assert metric.source is None


@pytest.mark.parametrize(
    "aggregation",
    [
        AnalyticsAggregationType.SUM,
        AnalyticsAggregationType.AVERAGE,
        AnalyticsAggregationType.MINIMUM,
        AnalyticsAggregationType.MAXIMUM,
    ],
)
def test_non_count_metric_requires_source(
    aggregation,
):

    with pytest.raises(
        ValueError,
        match="Analytics metric source",
    ):
        AnalyticsMetric(
            code="metric",
            name="Metric",
            aggregation=aggregation,
        )


def test_analytics_metric_normalizes_source():

    metric = AnalyticsMetric(
        code="total_amount",
        name="Total Amount",
        aggregation=(
            AnalyticsAggregationType.SUM
        ),
        source="  amount  ",
    )

    assert metric.source == "amount"


def test_analytics_metric_rejects_non_string_source():

    with pytest.raises(
        ValueError,
        match="Analytics metric source",
    ):
        AnalyticsMetric(
            code="metric",
            name="Metric",
            aggregation=(
                AnalyticsAggregationType.SUM
            ),
            source=123,
        )


def test_analytics_metric_normalizes_empty_optional_source_for_count():

    metric = AnalyticsMetric(
        code="record_count",
        name="Record Count",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        source=" ",
    )

    assert metric.source is None


def test_analytics_metric_normalizes_description():

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        description="  Description  ",
    )

    assert (
        metric.description
        == "Description"
    )


def test_analytics_metric_empty_description_becomes_none():

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        description=" ",
    )

    assert metric.description is None


def test_analytics_metric_rejects_invalid_description():

    with pytest.raises(
        ValueError,
        match="Analytics metric description",
    ):
        AnalyticsMetric(
            code="metric",
            name="Metric",
            aggregation=(
                AnalyticsAggregationType.COUNT
            ),
            description=123,
        )


def test_analytics_metric_normalizes_unit():

    metric = AnalyticsMetric(
        code="completion_rate",
        name="Completion Rate",
        aggregation=(
            AnalyticsAggregationType.AVERAGE
        ),
        source="completion",
        unit="  %  ",
    )

    assert metric.unit == "%"


def test_analytics_metric_empty_unit_becomes_none():

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        unit=" ",
    )

    assert metric.unit is None


def test_analytics_metric_rejects_invalid_unit():

    with pytest.raises(
        ValueError,
        match="Analytics metric unit",
    ):
        AnalyticsMetric(
            code="metric",
            name="Metric",
            aggregation=(
                AnalyticsAggregationType.COUNT
            ),
            unit=123,
        )


def test_analytics_metric_normalizes_category():

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        category="  Operations  ",
    )

    assert metric.category == "Operations"


def test_analytics_metric_empty_category_becomes_none():

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        category=" ",
    )

    assert metric.category is None


def test_analytics_metric_rejects_invalid_category():

    with pytest.raises(
        ValueError,
        match="Analytics metric category",
    ):
        AnalyticsMetric(
            code="metric",
            name="Metric",
            aggregation=(
                AnalyticsAggregationType.COUNT
            ),
            category=123,
        )


def test_analytics_metric_copies_metadata():

    metadata = {
        "domain": "operations",
        "owner": "reporting",
    }

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        metadata=metadata,
    )

    assert metric.metadata == metadata
    assert metric.metadata is not metadata


def test_analytics_metric_rejects_invalid_metadata():

    with pytest.raises(
        ValueError,
        match="Analytics metric metadata",
    ):
        AnalyticsMetric(
            code="metric",
            name="Metric",
            aggregation=(
                AnalyticsAggregationType.COUNT
            ),
            metadata=[],
        )


def test_analytics_metric_requires_boolean_active():

    with pytest.raises(
        ValueError,
        match="Analytics metric active",
    ):
        AnalyticsMetric(
            code="metric",
            name="Metric",
            aggregation=(
                AnalyticsAggregationType.COUNT
            ),
            active=1,
        )


def test_analytics_metric_defaults_to_active():

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
    )

    assert metric.active is True


def test_analytics_metric_can_be_inactive():

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        active=False,
    )

    assert metric.active is False


def test_analytics_metric_identifier():

    metric = AnalyticsMetric(
        code="total_volunteers",
        name="Total Volunteers",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
    )

    assert (
        metric.identifier
        == "TOTAL_VOLUNTEERS"
    )


def test_analytics_metric_to_dict():

    metric = AnalyticsMetric(
        code="total_volunteers",
        name="Total Volunteers",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        description="Total number of volunteers.",
        source=None,
        unit="persons",
        category="Operations",
        metadata={
            "domain": "volunteers",
        },
        active=True,
    )

    assert (
        metric.to_dict()
        == {
            "code": "total_volunteers",
            "name": "Total Volunteers",
            "aggregation": "count",
            "source": None,
            "description": "Total number of volunteers.",
            "unit": "persons",
            "category": "Operations",
            "metadata": {
                "domain": "volunteers",
            },
            "active": True,
        }
    )


def test_analytics_metric_to_dict_for_sum():

    metric = AnalyticsMetric(
        code="total_amount",
        name="Total Amount",
        aggregation=(
            AnalyticsAggregationType.SUM
        ),
        source="amount",
        unit="USD",
    )

    assert (
        metric.to_dict()
        == {
            "code": "total_amount",
            "name": "Total Amount",
            "aggregation": "sum",
            "source": "amount",
            "description": None,
            "unit": "USD",
            "category": None,
            "metadata": {},
            "active": True,
        }
    )


def test_analytics_metric_is_immutable():

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
    )

    with pytest.raises(
        AttributeError,
    ):
        metric.code = "changed"


def test_analytics_metric_preserves_metadata_values():

    metric = AnalyticsMetric(
        code="metric",
        name="Metric",
        aggregation=(
            AnalyticsAggregationType.COUNT
        ),
        metadata={
            "threshold": 10,
            "enabled": True,
        },
    )

    assert metric.metadata == {
        "threshold": 10,
        "enabled": True,
    }


def test_public_analytics_aggregation_type_is_available():

    from app.core.reporting import (
        AnalyticsAggregationType as PublicAggregationType,
    )

    assert (
        PublicAggregationType
        is AnalyticsAggregationType
    )


def test_public_analytics_metric_is_available():

    from app.core.reporting import (
        AnalyticsMetric as PublicAnalyticsMetric,
    )

    assert (
        PublicAnalyticsMetric
        is AnalyticsMetric
    )
