from app.modules.catering.commands import (
    RecognizeCateringRevenueCommand,
)


def test_recognize_revenue_command_validates_positive_id():
    command = RecognizeCateringRevenueCommand(
        revenue_id=1
    )

    command.validate()


def test_recognize_revenue_command_rejects_zero():
    command = RecognizeCateringRevenueCommand(
        revenue_id=0
    )

    try:
        command.validate()
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for zero revenue_id."
    )


def test_recognize_revenue_command_rejects_negative_id():
    command = RecognizeCateringRevenueCommand(
        revenue_id=-1
    )

    try:
        command.validate()
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for negative revenue_id."
    )


def test_recognize_revenue_command_name():
    command = RecognizeCateringRevenueCommand(
        revenue_id=1
    )

    assert (
        command.execute_name()
        == "catering.revenue.recognize"
    )
