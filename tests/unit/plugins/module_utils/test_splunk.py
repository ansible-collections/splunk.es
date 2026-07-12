# Copyright 2026 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

"""
Unit tests for plugins/module_utils/splunk.py.

Covers:
- check_argspec: happy path (ansible.utils available, valid args)
- check_argspec: failure path (ansible.utils available, invalid args)
- check_argspec: missing dependency path (ansible.utils NOT available)
- ImportError fallback: HAS_ANSIBLE_UTILS is False when import fails
"""

import importlib
import sys

from unittest.mock import MagicMock, patch

from ansible_collections.splunk.es.plugins.module_utils import splunk as splunk_mod
from ansible_collections.splunk.es.plugins.module_utils.splunk import check_argspec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_action_module(task_args=None, task_action="splunk.es.splunk_finding"):
    """Return a minimal mock action module."""
    action_module = MagicMock()
    action_module._task.args = task_args or {}
    action_module._task.action = task_action
    return action_module


# ---------------------------------------------------------------------------
# Tests for the HAS_ANSIBLE_UTILS = False branch (ImportError fallback)
# ---------------------------------------------------------------------------


class TestAnsibleUtilsImportFallback:
    """Verify that the module degrades gracefully when ansible.utils is absent."""

    def test_has_ansible_utils_false_when_import_fails(self):
        """Re-importing splunk.py with ansible.utils blocked sets HAS_ANSIBLE_UTILS=False."""
        module_name = "ansible_collections.splunk.es.plugins.module_utils.splunk"

        # Build a fake sys.modules that raises ImportError for ansible.utils
        blocked_key = (
            "ansible_collections.ansible.utils" + ".plugins.module_utils.common.argspec_validate"
        )
        patched_modules = {k: v for k, v in sys.modules.items() if k != module_name}
        patched_modules[blocked_key] = None  # None causes ImportError on import

        with patch.dict(sys.modules, patched_modules, clear=False):
            # Remove cached module so it gets reimported
            sys.modules.pop(module_name, None)
            try:
                reloaded = importlib.import_module(module_name)
                assert reloaded.HAS_ANSIBLE_UTILS is False
                assert reloaded.AnsibleArgSpecValidator is None
            finally:
                # Restore original cached module
                sys.modules.pop(module_name, None)
                importlib.import_module(module_name)

    def test_ansible_arg_spec_validator_is_none_when_import_fails(self):
        """AnsibleArgSpecValidator is set to None when the import fails."""
        module_name = "ansible_collections.splunk.es.plugins.module_utils.splunk"
        blocked_key = (
            "ansible_collections.ansible.utils" + ".plugins.module_utils.common.argspec_validate"
        )
        patched_modules = {k: v for k, v in sys.modules.items() if k != module_name}
        patched_modules[blocked_key] = None

        with patch.dict(sys.modules, patched_modules, clear=False):
            sys.modules.pop(module_name, None)
            try:
                reloaded = importlib.import_module(module_name)
                assert reloaded.AnsibleArgSpecValidator is None
            finally:
                sys.modules.pop(module_name, None)
                importlib.import_module(module_name)


# ---------------------------------------------------------------------------
# Tests for check_argspec when ansible.utils is NOT available
# ---------------------------------------------------------------------------


class TestCheckArgspecMissingDependency:
    """check_argspec returns False and sets result['failed'] when ansible.utils is absent."""

    def test_returns_false_when_ansible_utils_missing(self):
        result = {}
        action_module = _make_action_module()

        with patch.object(splunk_mod, "HAS_ANSIBLE_UTILS", False):
            ret = check_argspec(action_module, result, documentation="")

        assert ret is False

    def test_sets_failed_true_when_ansible_utils_missing(self):
        result = {}
        action_module = _make_action_module()

        with patch.object(splunk_mod, "HAS_ANSIBLE_UTILS", False):
            check_argspec(action_module, result, documentation="")

        assert result.get("failed") is True

    def test_error_message_mentions_ansible_utils(self):
        result = {}
        action_module = _make_action_module()

        with patch.object(splunk_mod, "HAS_ANSIBLE_UTILS", False):
            check_argspec(action_module, result, documentation="")

        assert "ansible.utils" in result.get("msg", "")

    def test_error_message_mentions_install_command(self):
        result = {}
        action_module = _make_action_module()

        with patch.object(splunk_mod, "HAS_ANSIBLE_UTILS", False):
            check_argspec(action_module, result, documentation="")

        assert "ansible-galaxy collection install" in result.get("msg", "")


# ---------------------------------------------------------------------------
# Tests for check_argspec when ansible.utils IS available
# ---------------------------------------------------------------------------


class TestCheckArgspecWithAnsibleUtils:
    """check_argspec delegates to AnsibleArgSpecValidator when the dep is present."""

    def _mock_validator(self, valid=True, errors=None, args=None):
        """Return a mock AnsibleArgSpecValidator instance."""
        validator = MagicMock()
        validator.validate.return_value = (valid, errors or [], args or {})
        validator_cls = MagicMock(return_value=validator)
        return validator_cls, validator

    def test_returns_true_on_valid_args(self):
        action_module = _make_action_module(task_args={"name": "test"})
        result = {}
        validator_cls, unused_validator = self._mock_validator(valid=True, args={"name": "test"})

        with patch.object(splunk_mod, "HAS_ANSIBLE_UTILS", True):
            with patch.object(splunk_mod, "AnsibleArgSpecValidator", validator_cls):
                ret = check_argspec(action_module, result, documentation="DOCS")

        assert ret is True
        assert "failed" not in result

    def test_returns_false_on_invalid_args(self):
        action_module = _make_action_module(task_args={"bad": "arg"})
        result = {}
        validator_cls, unused_validator = self._mock_validator(
            valid=False,
            errors=["missing required param"],
            args={},
        )

        with patch.object(splunk_mod, "HAS_ANSIBLE_UTILS", True):
            with patch.object(splunk_mod, "AnsibleArgSpecValidator", validator_cls):
                ret = check_argspec(action_module, result, documentation="DOCS")

        assert ret is False
        assert result.get("failed") is True
        assert "missing required param" in result.get("msg", [])

    def test_validator_receives_correct_schema_format(self):
        action_module = _make_action_module(task_args={"key": "val"})
        result = {}
        validator_cls, unused_validator = self._mock_validator(valid=True, args={"key": "val"})

        with patch.object(splunk_mod, "HAS_ANSIBLE_UTILS", True):
            with patch.object(splunk_mod, "AnsibleArgSpecValidator", validator_cls):
                with patch.object(splunk_mod.utils, "remove_empties", return_value={"key": "val"}):
                    check_argspec(action_module, result, documentation="MY_DOCS")

        unused_args, kwargs = validator_cls.call_args
        assert kwargs.get("schema_format") == "doc"
        assert kwargs.get("schema") == "MY_DOCS"
