"""
UnitAPI DSL Module

This module provides a Domain Specific Language (DSL) for configuring and controlling UnitAPI systems.
It supports multiple configuration formats, including YAML, HCL, Starlark, and a custom Simple DSL.
"""

from .base import DSLElement, Extension, Device, PipelineStep, Pipeline, IDSLParser
from .validators.schema import validate_config, validate_config_with_details
from .runtime.executor import DSLExecutor
from .runtime.context import DSLContext

__all__ = [
    # Base classes
    "DSLElement",
    "Extension",
    "Device",
    "PipelineStep",
    "Pipeline",
    "IDSLParser",
    # Validators
    "validate_config",
    "validate_config_with_details",
    # Runtime
    "DSLExecutor",
    "DSLContext",
]
