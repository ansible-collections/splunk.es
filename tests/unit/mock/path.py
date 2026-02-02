from ansible.utils.path import unfrackpath

from ansible_collections.splunk.es.tests.unit.compat.mock import MagicMock


mock_unfrackpath_noop = MagicMock(
    spec_set=unfrackpath,
    side_effect=lambda x, *args, **kwargs: x,
)
