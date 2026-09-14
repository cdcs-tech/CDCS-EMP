"""
CDCS Enterprise Management Platform (CDCS-EMP)

Purchase Request workflow tests.
"""

from app.core.workflow import (
    WorkflowDefinition,
    workflow_registry,
)

from app.modules.procurement.module import (
    ProcurementModule,
)

from app.modules.procurement.workflows import (
    PurchaseRequestWorkflow,
)


def test_purchase_request_workflow_defines_exact_states():
    workflow = PurchaseRequestWorkflow()

    assert [state.name for state in workflow.states()] == [
        "DRAFT",
        "SUBMITTED",
        "APPROVED",
        "REJECTED",
    ]


def test_purchase_request_workflow_defines_exact_transitions():
    workflow = PurchaseRequestWorkflow()

    transitions = workflow.transitions()

    assert len(transitions) == 4

    assert [
        (
            transition.source,
            transition.action,
            transition.target,
        )
        for transition in transitions
    ] == [
        ("DRAFT", "SUBMIT", "SUBMITTED"),
        ("SUBMITTED", "APPROVE", "APPROVED"),
        ("SUBMITTED", "REJECT", "REJECTED"),
        ("SUBMITTED", "RETURN", "DRAFT"),
    ]


def test_purchase_request_workflow_transition_metadata():
    workflow = PurchaseRequestWorkflow()

    transitions = workflow.transitions()

    assert [
        (
            transition.metadata["operation"],
            transition.metadata["terminal"],
        )
        for transition in transitions
    ] == [
        ("purchase_request.submit", False),
        ("purchase_request.approve", False),
        ("purchase_request.reject", True),
        ("purchase_request.return", False),
    ]


def test_purchase_request_workflow_has_only_approved_transition_paths():
    workflow = PurchaseRequestWorkflow()

    assert workflow.can_transition(
        "DRAFT",
        "SUBMITTED",
    )

    assert workflow.can_transition(
        "SUBMITTED",
        "APPROVED",
    )

    assert workflow.can_transition(
        "SUBMITTED",
        "REJECTED",
    )

    assert workflow.can_transition(
        "SUBMITTED",
        "DRAFT",
    )

    assert not workflow.can_transition(
        "DRAFT",
        "APPROVED",
    )

    assert not workflow.can_transition(
        "DRAFT",
        "REJECTED",
    )

    assert not workflow.can_transition(
        "APPROVED",
        "DRAFT",
    )

    assert not workflow.can_transition(
        "REJECTED",
        "DRAFT",
    )


def test_purchase_request_workflow_rejected_transition_is_terminal():
    workflow = PurchaseRequestWorkflow()

    terminal_transitions = [
        transition
        for transition in workflow.transitions()
        if transition.metadata.get("terminal") is True
    ]

    assert len(terminal_transitions) == 1

    transition = terminal_transitions[0]

    assert transition.source == "SUBMITTED"
    assert transition.action == "REJECT"
    assert transition.target == "REJECTED"


def test_purchase_request_workflow_return_is_controlled_correction():
    workflow = PurchaseRequestWorkflow()

    return_transitions = [
        transition
        for transition in workflow.transitions()
        if transition.action == "RETURN"
    ]

    assert len(return_transitions) == 1

    transition = return_transitions[0]

    assert transition.source == "SUBMITTED"
    assert transition.target == "DRAFT"
    assert transition.metadata["operation"] == (
        "purchase_request.return"
    )
    assert transition.metadata["terminal"] is False


def test_procurement_module_exposes_purchase_request_workflow():
    module = ProcurementModule()

    workflows = module.get_workflows()

    assert len(workflows) == 1

    definition = workflows[0]

    assert isinstance(
        definition,
        WorkflowDefinition,
    )

    assert definition.module_name == "PROCUREMENT"
    assert definition.workflow_name == "purchase_request"
    assert isinstance(
        definition.workflow,
        PurchaseRequestWorkflow,
    )


def test_procurement_workflow_registration_uses_enterprise_registry(
    app,
):
    module = ProcurementModule()

    with app.app_context():
        module.register_workflows(app)

        assert workflow_registry.has(
            "PROCUREMENT",
            "purchase_request",
        )

        definition = workflow_registry.get(
            "PROCUREMENT",
            "purchase_request",
        )

        assert isinstance(
            definition,
            WorkflowDefinition,
        )

        assert isinstance(
            definition.workflow,
            PurchaseRequestWorkflow,
        )
