from __future__ import annotations

from ..export import get_user_sites
from ..exporthelpers.export_helper import Json


class FakeApi:
    def fetch(self, endpoint: str) -> Json:
        if endpoint == 'me/associated':
            return {
                'items': [
                    {
                        'site_name': 'Meta Stack Exchange',
                        'site_url': 'https://meta.stackexchange.com',
                    },
                    {
                        'site_name': 'Stack Overflow',
                        'site_url': 'https://stackoverflow.com',
                    },
                ],
            }

        assert endpoint == 'sites', endpoint
        return {
            'items': [
                {
                    'name': 'Meta Stack Exchange',
                    'api_site_parameter': 'meta',
                    'site_url': 'https://meta.stackexchange.com',
                },
                {
                    'name': 'Stack Overflow',
                    'api_site_parameter': 'stackoverflow',
                    'site_url': 'https://stackoverflow.com',
                },
            ],
        }


def test_get_user_sites_matches_by_url() -> None:
    assert get_user_sites(FakeApi()) == {
        'meta': 'Meta Stack Exchange',
        'stackoverflow': 'Stack Overflow',
    }
