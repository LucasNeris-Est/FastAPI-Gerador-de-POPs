# Import Guard and Validator
from guardrails import Guard
from Validador_tex import ValidTex  # Certifique-se de importar seu validador

# Setup Guard
guard = Guard().use(ValidTex, on_fail="exception")

# A TeX document example that should pass validation
valid_tex_document = r"""
\documentclass{article}
\begin{document}
Hello, this is a test document.
\end{document}
"""

# A TeX document example that should fail validation (missing \documentclass)
invalid_tex_document = r"""
\begin{document}
Hello, this document is missing the class declaration.
\end{document}
"""

# Validate the valid TeX document
try:
    guard.validate(valid_tex_document)  # Validator passes
    print("Valid TeX document passed validation.")
except Exception as e:
    print(f"Validation failed: {e}")

# Validate the invalid TeX document
try:
    guard.validate(invalid_tex_document)  # Validator fails
except Exception as e:
    print(f"Validation failed: {e}")
