from os import getenv
import shimoku_api_python as shimoku
from tenacity import RetryError
import unittest
import asyncio

api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')
verbose: str = getenv('VERBOSITY')
async_execution: bool = getenv('ASYNC_EXECUTION') == 'TRUE'


s = shimoku.Client(
    access_token=api_key,
    universe_id=universe_id,
    environment=environment,
    verbosity=verbose,
    async_execution=async_execution,
    business_id=business_id,
)


class TestDashboardMetadataApi(unittest.TestCase):

    def test_dashboard_CRUD(self):
        dashboard_name = 'Testing dashboard'
        s.dashboard.delete_dashboard(dashboard_name=dashboard_name)
        s.dashboard.delete_dashboard(dashboard_name=dashboard_name + ' updated')

        dashboard = s.dashboard.create_dashboard(dashboard_name=dashboard_name)

        assert dashboard['name'] == dashboard_name

        dashboard = s.dashboard.get_dashboard(dashboard_id=dashboard['id'])
        assert dashboard['name'] == dashboard_name

        s.dashboard.update_dashboard(dashboard_id=dashboard['id'], name=dashboard_name+' updated')

        dashboard = s.dashboard.get_dashboard(dashboard_id=dashboard['id'])
        assert dashboard['name'] == dashboard_name+' updated'

        assert s.dashboard.create_dashboard(dashboard_name=dashboard_name)
        assert not s.dashboard.create_dashboard(dashboard_name=dashboard_name)
        assert not s.dashboard.create_dashboard(dashboard_name=dashboard_name + ' updated')

        s.dashboard.delete_dashboard(dashboard_name=dashboard_name)
        s.dashboard.delete_dashboard(dashboard_name=dashboard_name+' updated')

        assert not s.dashboard.get_dashboard(dashboard_name=dashboard_name)
        assert not s.dashboard.get_dashboard(dashboard_name=dashboard_name+' updated')

    def test_create_and_delete_app_dashboard_link(self):
        dashboard_name = 'Testing dashboard for appdashboards'

        app_name = 'Testing app'

        if s.app.get_app_by_name(business_id=business_id, name=app_name):
            s.app.delete_app(business_id=business_id,
                             app_id=s.app.get_app_by_name(business_id=business_id, name=app_name)['id'])

        s.dashboard.delete_dashboard(dashboard_name=dashboard_name)
        s.dashboard.delete_dashboard(dashboard_name=dashboard_name + ' updated')

        s.dashboard.create_dashboard(dashboard_name=dashboard_name)
        app_id = s.app.create_app(business_id=business_id, name=app_name)['id']

        s.dashboard.add_app_in_dashboard(dashboard_name=dashboard_name, app_id=app_id)

        app_ids = s.dashboard.get_dashboard_app_ids(dashboard_name=dashboard_name)
        assert app_id == app_ids[0]

        with self.assertRaises(RetryError):
            s.dashboard.delete_dashboard(dashboard_name=dashboard_name)

        s.dashboard.remove_app_from_dashboard(dashboard_name=dashboard_name, app_id=app_id)
        s.dashboard.delete_dashboard(dashboard_name=dashboard_name)
        s.app.delete_app(business_id=business_id,
                         app_id=s.app.get_app_by_name(business_id=business_id, name=app_name)['id'])
