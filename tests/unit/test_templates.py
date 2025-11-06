"""
Unit tests for Ansible template validation.

Tests validate Jinja2 templates for syntax and proper variable usage.
"""

import os
from typing import List

import pytest


@pytest.mark.unit
def test_templates_directory_exists() -> None:
    """Test that templates directory exists."""
    templates_dir = "openwrt-mesh-ansible/templates"
    assert os.path.exists(templates_dir), f"Templates directory not found: {templates_dir}"


@pytest.mark.unit
def test_template_files_exist() -> None:
    """
    Test that expected template files exist.

    This is a placeholder test that can be expanded as templates are created.
    """
    templates_dir = "openwrt-mesh-ansible/templates"

    # For now, just verify the directory exists
    # Add specific template checks as templates are created
    assert os.path.isdir(templates_dir), "Templates directory should be a directory"


@pytest.mark.unit
def test_jinja2_templates_syntax() -> None:
    """
    Test that all Jinja2 templates have valid syntax.

    This test will attempt to parse all .j2 files in the templates directory.
    """
    templates_dir = "openwrt-mesh-ansible/templates"

    if not os.path.exists(templates_dir):
        pytest.skip("Templates directory does not exist yet")

    # Find all .j2 files
    template_files: List[str] = []
    for root, _dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith(".j2"):
                template_files.append(os.path.join(root, file))

    if not template_files:
        pytest.skip("No template files found")

    # Try to parse each template
    from jinja2 import Environment, TemplateSyntaxError

    env = Environment()

    for template_file in template_files:
        with open(template_file, "r") as f:
            template_content = f.read()
            try:
                env.parse(template_content)
            except TemplateSyntaxError as e:
                pytest.fail(f"Template syntax error in {template_file}: {e}")
