"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Contract tests for QueryOptions.
"""

from __future__ import annotations

import pytest

from app.core.data.query import QueryOptions


class TestQueryOptions:
    """
    Contract tests for the QueryOptions value object.
    """

    def test_default_values(self):
        """
        QueryOptions provides stable enterprise defaults.
        """

        options = QueryOptions()

        assert options.page == 1
        assert options.page_size == 25
        assert options.sort_by == "id"
        assert options.sort_direction == "asc"
        assert options.filters == {}
        assert options.search is None
        assert options.fields == []
        assert options.include_inactive is False

    def test_custom_values_are_preserved(self):
        """
        Explicit query values are preserved.
        """

        options = QueryOptions(
            page=2,
            page_size=50,
            sort_by="name",
            sort_direction="desc",
            filters={
                "code": "TEST",
            },
            search="tenant",
            fields=[
                "id",
                "code",
                "name",
            ],
            include_inactive=True,
        )

        assert options.page == 2
        assert options.page_size == 50
        assert options.sort_by == "name"
        assert options.sort_direction == "desc"
        assert options.filters == {
            "code": "TEST",
        }
        assert options.search == "tenant"
        assert options.fields == [
            "id",
            "code",
            "name",
        ]
        assert options.include_inactive is True

    def test_to_dict_returns_serializable_representation(self):
        """
        QueryOptions can be converted into a dictionary.
        """

        options = QueryOptions(
            page=3,
            page_size=10,
            sort_by="name",
            sort_direction="desc",
            filters={
                "is_active": True,
            },
            search="active",
            fields=[
                "id",
                "name",
            ],
            include_inactive=True,
        )

        result = options.to_dict()

        assert result == {
            "page": 3,
            "page_size": 10,
            "sort_by": "name",
            "sort_direction": "desc",
            "filters": {
                "is_active": True,
            },
            "search": "active",
            "fields": [
                "id",
                "name",
            ],
            "include_inactive": True,
        }

    def test_to_dict_returns_copy_of_filters(self):
        """
        Serialized filters are independent of the source mapping.
        """

        filters = {
            "code": "TEST",
        }

        options = QueryOptions(
            filters=filters,
        )

        result = options.to_dict()

        result["filters"]["code"] = "CHANGED"

        assert options.filters["code"] == "TEST"

    def test_to_dict_returns_copy_of_fields(self):
        """
        Serialized fields are independent of the source list.
        """

        fields = [
            "id",
            "name",
        ]

        options = QueryOptions(
            fields=fields,
        )

        result = options.to_dict()

        result["fields"].append(
            "description"
        )

        assert options.fields == [
            "id",
            "name",
        ]

    def test_each_instance_gets_independent_filters(self):
        """
        Default filters must not be shared between instances.
        """

        first = QueryOptions()
        second = QueryOptions()

        first.filters["code"] = "FIRST"

        assert second.filters == {}

    def test_each_instance_gets_independent_fields(self):
        """
        Default fields must not be shared between instances.
        """

        first = QueryOptions()
        second = QueryOptions()

        first.fields.append("name")

        assert second.fields == []

    @pytest.mark.parametrize(
        "page",
        [
            0,
            -1,
            -10,
        ],
    )
    def test_invalid_page_values_are_rejected(
        self,
        page,
    ):
        """
        Page numbers below one are invalid.
        """

        with pytest.raises(
            ValueError,
            match="page",
        ):
            QueryOptions(
                page=page,
            )

    @pytest.mark.parametrize(
        "page_size",
        [
            0,
            -1,
            -25,
        ],
    )
    def test_invalid_page_size_values_are_rejected(
        self,
        page_size,
    ):
        """
        Page sizes below one are invalid.
        """

        with pytest.raises(
            ValueError,
            match="page_size",
        ):
            QueryOptions(
                page_size=page_size,
            )

    @pytest.mark.parametrize(
        "sort_direction",
        [
            "invalid",
            "ascending",
            "descending",
            "",
        ],
    )
    def test_invalid_sort_direction_is_rejected(
        self,
        sort_direction,
    ):
        """
        Unsupported sort directions are invalid.
        """

        with pytest.raises(
            ValueError,
            match="sort_direction",
        ):
            QueryOptions(
                sort_direction=sort_direction,
            )

    def test_sort_direction_is_case_insensitive(self):
        """
        Sort direction normalization accepts common casing.
        """

        ascending = QueryOptions(
            sort_direction="ASC",
        )

        descending = QueryOptions(
            sort_direction="DESC",
        )

        assert ascending.sort_direction == "asc"
        assert descending.sort_direction == "desc"

    def test_sort_by_must_not_be_empty(self):
        """
        A sort field is required when sorting is requested.
        """

        with pytest.raises(
            ValueError,
            match="sort_by",
        ):
            QueryOptions(
                sort_by="",
            )

    def test_search_is_normalized(self):
        """
        Search values are normalized by trimming whitespace.
        """

        options = QueryOptions(
            search="  tenant search  ",
        )

        assert options.search == "tenant search"

    def test_blank_search_is_normalized_to_none(self):
        """
        Blank search values are treated as no search criteria.
        """

        options = QueryOptions(
            search="   ",
        )

        assert options.search is None

    def test_fields_are_normalized(self):
        """
        Field names are trimmed during normalization.
        """

        options = QueryOptions(
            fields=[
                " id ",
                " name",
                "description ",
            ],
        )

        assert options.fields == [
            "id",
            "name",
            "description",
        ]

    def test_blank_fields_are_rejected(self):
        """
        Empty field names are not valid query fields.
        """

        with pytest.raises(
            ValueError,
            match="fields",
        ):
            QueryOptions(
                fields=[
                    "id",
                    "",
                ],
            )

    def test_include_inactive_is_boolean(self):
        """
        include_inactive must remain an explicit boolean.
        """

        options = QueryOptions(
            include_inactive=True,
        )

        assert options.include_inactive is True

    def test_query_options_does_not_share_mutable_state(self):
        """
        Mutable query collections are isolated between instances.
        """

        first = QueryOptions()
        second = QueryOptions()

        first.filters["status"] = "active"
        first.fields.append("name")

        assert second.filters == {}
        assert second.fields == []

