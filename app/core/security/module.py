"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Module permission definitions.
"""


from app.core.security.permissions import Permission



class ModulePermission(Permission):
    """
    Permission definition helper for
    enterprise modules.
    """



    def __init__(
        self,
        module: str,
        resource: str,
        action: str,
        name: str = "",
        description: str = "",
    ):
        """
        Create module permission.
        """

        code = (
            f"{module}."
            f"{resource}."
            f"{action}"
        )


        super().__init__(
            code=code,
            name=(
                name
                or code.replace(
                    ".",
                    " ",
                ).title()
            ),
            description=description,
            module=module,
            resource=resource,
            action=action,
        )
