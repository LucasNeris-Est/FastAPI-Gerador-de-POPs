from typing import Any, Dict
from guardrails.validators import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/valid_tex", data_type=["string"])
class ValidTex(Validator):
    """Validates that a value is a valid TeX document.


    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/valid_tex`            |
    | Supported data types          | `string`                          |
    | Programmatic fix              | None                              |
    """

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Validates that a value is a valid TeX document."""
        if not isinstance(value, str):
            return FailResult(
                error_message="Value is not a string, and thus cannot be valid TeX."
            )

        # Required basic TeX commands
        required_commands = [r"\documentclass", r"\begin{document}", r"\end{document}"]
        missing_commands = [
            command for command in required_commands if command not in value
        ]

        if missing_commands:
            return FailResult(
                error_message=(
                    f"Value is not a valid TeX document! Missing required commands: "
                    f"{', '.join(missing_commands)}"
                )
            )

        return PassResult()
