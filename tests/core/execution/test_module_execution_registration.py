"""
Module execution-registration tests.
"""

import pytest
from flask import Flask

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    CommandDispatcher,
    ExecutionContext,
    ExecutionDefinition,
    ExecutionResult,
    command_registry,
)
from app.core.modules import BaseModule
from app.core.modules.metadata import ModuleMetadata


class TestCommand(
    BaseCommand
):

    command_name = "test.module.execution"

    def execute_name(self) -> str:

        return self.command_name


class TestHandler(
    BaseCommandHandler
):

    command_type = TestCommand

    called = False

    def handle(
        self,
        command,
        context,
    ):

        self.called = True

        return ExecutionResult.success_result(
            data={
                "executed": True,
            }
        )


class TestModule(
    BaseModule
):

    def get_metadata(self) -> ModuleMetadata:

        return ModuleMetadata(
            code="TEST",
            name="Test",
            version="1.0.0",
            description="Test module.",
            author="CDCS",
            category="Test",
            active=True,
        )

    def get_execution_definitions(self):

        return [
            ExecutionDefinition(
                command=TestCommand,
                handler=TestHandler(),
            )
        ]


@pytest.fixture
def app():

    application = Flask(
        __name__
    )

    application.extensions[
        "command_dispatcher"
    ] = CommandDispatcher()

    return application


@pytest.fixture(autouse=True)
def clear_command_registry():

    command_registry.clear()

    yield

    command_registry.clear()


def test_module_exposes_execution_definitions():

    module = TestModule()

    definitions = (
        module.get_execution_definitions()
    )

    assert len(
        definitions
    ) == 1

    assert (
        definitions[0].command
        is TestCommand
    )

    assert isinstance(
        definitions[0].handler,
        TestHandler,
    )


def test_module_registers_command_with_command_registry(
    app,
):

    module = TestModule()

    module.register_execution(
        app
    )

    assert (
    command_registry.exists(
        TestCommand.command_name
    )
    is True
)


def test_module_registers_handler_with_application_dispatcher(
    app,
):

    module = TestModule()

    module.register_execution(
        app
    )

    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    assert (
        dispatcher.has_handler(
            TestCommand
        )
        is True
    )


def test_module_execution_registration_does_not_execute_handler(
    app,
):

    module = TestModule()

    handler = module.get_execution_definitions()[
        0
    ].handler

    module.register_execution(
        app
    )

    assert (
        handler.called
        is False
    )


def test_module_with_no_execution_definitions_is_unchanged(
    app,
):

    class EmptyModule(
        BaseModule
    ):

        def get_metadata(self) -> ModuleMetadata:

            return ModuleMetadata(
                code="EMPTY",
                name="Empty",
                version="1.0.0",
                description="Empty module.",
                author="CDCS",
                category="Test",
                active=True,
            )

    module = EmptyModule()

    assert (
        module.has_execution_definitions()
        is False
    )

    assert (
        module.register_execution(
            app
        )
        is None
    )


def test_execution_registration_requires_application_dispatcher():

    application = Flask(
        __name__
    )

    module = TestModule()

    with pytest.raises(
        RuntimeError,
        match="Application command dispatcher is not initialized.",
    ):

        module.register_execution(
            application
        )


def test_execution_definition_rejects_mismatched_handler():

    class OtherCommand(
        BaseCommand
    ):

        command_name = "test.module.other"

        def execute_name(self) -> str:

            return self.command_name

    class OtherHandler(
        BaseCommandHandler
    ):

        command_type = OtherCommand

        def handle(
            self,
            command,
            context,
        ):

            return ExecutionResult.success_result()

    definition = ExecutionDefinition(
        command=TestCommand,
        handler=OtherHandler(),
    )

    module = TestModule()

    module.execution_definitions = [
        definition
    ]

    with pytest.raises(
        TypeError,
        match="handler command_type must match the command",
    ):

        application = Flask(
            __name__
        )

        application.extensions[
            "command_dispatcher"
        ] = CommandDispatcher()

        module.register_execution(
            application
        )
