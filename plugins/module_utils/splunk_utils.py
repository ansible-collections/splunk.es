# -*- coding: utf-8 -*-
"""Pure Python utility functions for Splunk modules.

This module contains utility functions that have NO Ansible dependencies,
making them safe to import in unit tests without triggering Ansible imports.

"""

# (c) 2018, Adam Miller (admiller@redhat.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


def remove_get_keys_from_payload_dict(payload_dict, remove_key_list):
    """Remove specified keys from a payload dictionary.

    Args:
        payload_dict: Dictionary to remove keys from.
        remove_key_list: List of keys to remove.

    Returns:
        The modified payload_dict with specified keys removed.
    """
    for each_key in remove_key_list:
        if each_key in payload_dict:
            payload_dict.pop(each_key)
    return payload_dict


def map_params_to_obj(module_params, key_transform):
    """Convert API returned params to module params using key transformation.

    This function transforms dictionary keys from API format to module format.
    Keys are popped from the input dictionary (mutates input).

    Args:
        module_params: Dictionary with API parameter names.
        key_transform: Dict mapping API param names to module param names.
            Format: {api_key: module_key}

    Returns:
        Dictionary with transformed keys (module param names).
    """
    obj = {}
    for k, v in key_transform.items():
        if k in module_params and (
            module_params.get(k) or module_params.get(k) == 0 or module_params.get(k) is False
        ):
            obj[v] = module_params.pop(k)
    return obj


def map_obj_to_params(module_return_params, key_transform):
    """Convert module params to API params using key transformation.

    This function transforms dictionary keys from module format to API format.
    Keys are popped from the input dictionary (mutates input).

    Args:
        module_return_params: Dictionary with module parameter names.
        key_transform: Dict mapping API param names to module param names.
            Format: {api_key: module_key}

    Returns:
        Dictionary with transformed keys (API param names).
    """
    temp = {}
    for k, v in key_transform.items():
        if v in module_return_params and (
            module_return_params.get(v)
            or module_return_params.get(v) == 0
            or module_return_params.get(v) is False
        ):
            temp[k] = module_return_params.pop(v)
    return temp


def set_defaults(config, defaults):
    """Set default values in config dictionary if keys are not present.

    Args:
        config: Configuration dictionary to update.
        defaults: Dictionary of default key-value pairs.

    Returns:
        The modified config dictionary with defaults applied.
    """
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config
