"""
Internal data models for Selenium script generation.

Defines dataclasses for script generation, validation, and HTML parsing.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class ScriptStatus(str, Enum):
    """Selenium script validation status."""
    VALID = "valid"
    VALID_WITH_WARNINGS = "valid_with_warnings"
    INVALID = "invalid"


# ==================== HTML Selector Models ====================

@dataclass
class HTMLSelector:
    """Represents an HTML element selector."""
    selector_type: str  # id, name, css, xpath
    selector_value: str
    element_tag: str
    element_text: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class HTMLElementInfo:
    """Information about HTML elements extracted from page."""
    ids: List[Dict[str, Any]] = field(default_factory=list)
    names: List[Dict[str, Any]] = field(default_factory=list)
    buttons: List[Dict[str, Any]] = field(default_factory=list)
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    select: List[Dict[str, Any]] = field(default_factory=list)
    radio: List[Dict[str, Any]] = field(default_factory=list)
    checkbox: List[Dict[str, Any]] = field(default_factory=list)


# ==================== Script Validation Models ====================

@dataclass
class ScriptValidation:
    """Validation results for a generated script."""
    status: ScriptStatus
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    selectors_found: List[str] = field(default_factory=list)
    syntax_valid: bool = True

    def is_valid(self) -> bool:
        """Check if script is valid (no errors)."""
        return self.status in [ScriptStatus.VALID, ScriptStatus.VALID_WITH_WARNINGS]

    def add_error(self, error: str):
        """Add an error to validation results."""
        self.errors.append(error)
        self.status = ScriptStatus.INVALID
        self.syntax_valid = False

    def add_warning(self, warning: str):
        """Add a warning to validation results."""
        self.warnings.append(warning)
        if self.status == ScriptStatus.VALID:
            self.status = ScriptStatus.VALID_WITH_WARNINGS


# ==================== Script Models ====================

@dataclass
class SeleniumScript:
    """A generated Selenium WebDriver script."""
    code: str
    test_case_id: str
    selectors_used: List[str]
    validation_status: ScriptStatus
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    file_name: Optional[str] = None
    script_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "code": self.code,
            "test_case_id": self.test_case_id,
            "selectors_used": self.selectors_used,
            "validation_status": self.validation_status.value if isinstance(self.validation_status, ScriptStatus) else self.validation_status,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings,
            "created_at": self.created_at.isoformat(),
            "file_name": self.file_name,
            "script_id": self.script_id
        }


@dataclass
class ScriptGenerationContext:
    """Context information for script generation."""
    test_case_id: str
    test_scenario: str
    test_steps: List[str]
    expected_result: str
    html_selectors: HTMLElementInfo
    documentation_context: str
    include_assertions: bool = True
    include_logging: bool = True
