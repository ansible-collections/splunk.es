# -*- coding: utf-8 -*-
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Dictionary utility functions for Ansible Splunk ES collection.

These functions were originally provided by ansible.netcommon's
``network.common.utils`` module and are inlined here to remove
that collection dependency.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from itertools import chain


def sort_list(val):
    """Sort a value if it is a list, otherwise return as-is.

    Args:
        val: Any value. If it is a list of dicts, each dict is
            converted to a sorted-tuple representation for comparison.

    Returns:
        A sorted copy of the list, or the original value unchanged.
    """
    if isinstance(val, list):
        if all(isinstance(x, dict) for x in val):
            return sorted(val, key=lambda x: sorted(x.items()))
        return sorted(val)
    return val


def remove_empties(cfg_dict: dict) -> dict:
    """Recursively remove keys with empty/None values from a dictionary.

    Args:
        cfg_dict: A dictionary to clean.

    Returns:
        A new dictionary with all None, empty-list, empty-dict,
        empty-tuple, and empty-string values removed.
    """
    final_cfg: dict = {}
    if not cfg_dict:
        return final_cfg

    for key, val in cfg_dict.items():
        dct = None
        if isinstance(val, dict):
            child_val = remove_empties(val)
            if child_val:
                dct = {key: child_val}
        elif isinstance(val, list) and val and all(isinstance(x, dict) for x in val):
            child_val = [remove_empties(x) for x in val]
            if child_val:
                dct = {key: child_val}
        elif val not in [None, [], {}, (), ""]:
            dct = {key: val}
        if dct:
            final_cfg.update(dct)
    return final_cfg


def dict_diff(base: dict, comparable: dict) -> dict:
    """Compute the difference between two dictionaries.

    For scalar values the key reflects the updated value from *comparable*.
    Keys absent from *comparable* are ignored.  Lists are replaced wholly.
    Nested dicts are compared recursively.

    Args:
        base: The reference dictionary.
        comparable: The dictionary to compare against *base*.

    Returns:
        A new dictionary containing only the differences.

    Raises:
        AssertionError: If *base* or *comparable* is not a dict
            (None is accepted for *comparable*).
    """
    if not isinstance(base, dict):
        raise AssertionError("`base` must be of type <dict>")
    if not isinstance(comparable, dict):
        if comparable is None:
            comparable = {}
        else:
            raise AssertionError("`comparable` must be of type <dict>")

    updates: dict = {}

    for key, value in base.items():
        if isinstance(value, dict):
            item = comparable.get(key)
            if item is not None:
                sub_diff = dict_diff(value, comparable[key])
                if sub_diff:
                    updates[key] = sub_diff
        else:
            comparable_value = comparable.get(key)
            if comparable_value is not None:
                if sort_list(base[key]) != sort_list(comparable_value):
                    updates[key] = comparable_value

    for key in set(comparable.keys()).difference(base.keys()):
        updates[key] = comparable.get(key)

    return updates


def dict_merge(base: dict, other: dict) -> dict:
    """Deep-merge two dictionaries, preferring values from *other*.

    When both keys exist the value is taken from *other*.  Lists are
    combined with duplicates removed.  Nested dicts are merged recursively.

    Args:
        base: The base dictionary.
        other: The dictionary to merge into *base*.

    Returns:
        A new combined dictionary.

    Raises:
        AssertionError: If either argument is not a dict.
    """
    if not isinstance(base, dict):
        raise AssertionError("`base` must be of type <dict>")
    if not isinstance(other, dict):
        raise AssertionError("`other` must be of type <dict>")

    combined: dict = {}

    for key, value in deepcopy(base).items():
        if isinstance(value, dict):
            if key in other:
                item = other.get(key)
                if item is not None:
                    if isinstance(other[key], Mapping):
                        combined[key] = dict_merge(value, other[key])
                    else:
                        combined[key] = other[key]
                else:
                    combined[key] = item
            else:
                combined[key] = value
        elif isinstance(value, list):
            if key in other:
                item = other.get(key)
                if item is not None:
                    try:
                        combined[key] = list(set(chain(value, item)))
                    except TypeError:
                        value.extend([i for i in item if i not in value])
                        combined[key] = value
                else:
                    combined[key] = item
            else:
                combined[key] = value
        else:
            if key in other:
                other_value = other.get(key)
                if other_value is not None:
                    if sort_list(base[key]) != sort_list(other_value):
                        combined[key] = other_value
                    else:
                        combined[key] = value
                else:
                    combined[key] = other_value
            else:
                combined[key] = value

    for key in set(other.keys()).difference(base.keys()):
        combined[key] = other.get(key)

    return combined
