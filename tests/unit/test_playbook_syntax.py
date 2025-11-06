"""
Unit tests for Ansible playbook syntax validation.

Tests validate playbook YAML syntax and basic structure.
"""

import os

import pytest
import yaml


@pytest.mark.unit
def test_all_playbooks_exist(playbook_paths: dict) -> None:
    """
    Test that all expected playbooks exist.

    Args:
        playbook_paths: Dictionary of playbook names to paths from fixture.
    """
    for name, path in playbook_paths.items():
        assert os.path.exists(path), f"Playbook '{name}' not found at {path}"


@pytest.mark.unit
def test_playbooks_valid_yaml(playbook_paths: dict) -> None:
    """
    Test that all playbooks are valid YAML.

    Args:
        playbook_paths: Dictionary of playbook names to paths from fixture.
    """
    for name, path in playbook_paths.items():
        with open(path, "r") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in playbook '{name}': {e}")


@pytest.mark.unit
def test_playbooks_are_lists(playbook_paths: dict) -> None:
    """
    Test that playbooks are lists of plays.

    Args:
        playbook_paths: Dictionary of playbook names to paths from fixture.
    """
    for name, path in playbook_paths.items():
        with open(path, "r") as f:
            content = yaml.safe_load(f)
            assert isinstance(
                content, list
            ), f"Playbook '{name}' should be a list of plays"


@pytest.mark.unit
def test_deploy_playbook_structure(playbook_paths: dict) -> None:
    """
    Test that deploy playbook has expected structure.

    Args:
        playbook_paths: Dictionary of playbook names to paths from fixture.
    """
    with open(playbook_paths["deploy"], "r") as f:
        playbook = yaml.safe_load(f)

    assert len(playbook) > 0, "Deploy playbook should have at least one play"

    # Check first play
    first_play = playbook[0]
    assert "hosts" in first_play, "Play should define hosts"
    assert "tasks" in first_play or "roles" in first_play, "Play should have tasks or roles"


@pytest.mark.unit
def test_verify_playbook_structure(playbook_paths: dict) -> None:
    """
    Test that verify playbook has expected structure.

    Args:
        playbook_paths: Dictionary of playbook names to paths from fixture.
    """
    with open(playbook_paths["verify"], "r") as f:
        playbook = yaml.safe_load(f)

    assert len(playbook) > 0, "Verify playbook should have at least one play"

    first_play = playbook[0]
    assert "hosts" in first_play, "Play should define hosts"
    assert "tasks" in first_play or "roles" in first_play, "Play should have tasks or roles"
