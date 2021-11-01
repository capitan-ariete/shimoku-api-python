""""""

from typing import List, Dict, Optional


class ExplorerApi(object):
    """Get Businesses, Apps, Paths and Reports in any possible combination
    """

    def __init__(self, api_client):
        self.api_client = api_client

    # TODO this will be used by all, then post it in aux.py or something alike
    def set_http_info(self, **kwargs):  # noqa: E501
        """
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.remove_with_http_info(campaign_id, async_req=True)
        >>> result = thread.get()
        :param async_req bool
        :param str campaign_id: The unique id for the campaign. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        for key, val in params['kwargs']:
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method remove" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json', 'application/problem+json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['basicAuth']  # noqa: E501

        return (
            query_params, header_params,
            body_params, form_params, local_var_files,
            auth_settings, params, collection_formats,
        )

    def _get_element(self, element_name: str, element_id: str, **kwargs) -> Dict:
        """Retrieve an element if the endpoint exists"""
        (
            query_params, header_params,
            body_params, form_params, local_var_files,
            auth_settings, params, collection_formats,
        ) = self.set_http_info(**kwargs)

        path_params = {}
        if element_name in params:
            path_params[element_name] = params[element_name]  # noqa: E501

        element_data: Dict = (
            self.api_client.call_api(
                f'{element_name}/{element_id}', 'GET',  # TODO el GET lo puedo hacer variable tambien!!
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=None,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
        )
        return element_data

    def get_business(self, business_id: str, **kwargs) -> Dict:
        """Retrieve an specific user_id

        :param business_id: user UUID
        """
        business_data: Dict = (
            self._get_element(
                element_name='business',
                element_id=business_id,
                **kwargs
            )
        )
        return business_data

    def get_app(self, app_id: str, **kwargs) -> Dict:
        """Retrieve an specific app_id metadata

        :param app_id: app UUID
        """
        app_data: Dict = (
            self._get_element(
                element_name='app',
                element_id=app_id,
                **kwargs
            )
        )
        return app_data

# TODO Guillermo esto nunca tendra el chartData
    def get_report(
            self, report_id: Optional[str] = None,
            external_id: Optional[str] = None,
            app_id: Optional[str] = None,
            **kwargs,
    ) -> Dict:
        """Retrieve an specific report data

        :param report_id: Shimoku report UUID
        :param external_id: external report UUID
        :param app_id: Shinmoku app UUID (only required if the external_id is provided)
        """
# TODO Guillermo I better gonna need this end-point
        if report_id:
            report_data: Dict = (
                self._get_element(
                    element_name='report',
                    element_id=report_id,
                    **kwargs
                )
            )
        elif external_id:
            if not app_id:
                raise ValueError(
                    'If you retrieve by external_id '
                    'you must provide an app_id'
                )

            report_ids_in_app: List[str] = (
                self.get_app_all_reports(app_id)
            )

            for report_id in report_ids_in_app:
                report_data_: Dict = self.get_report(report_id=report_id)
                if report_data_['etl_code_id'] == external_id:
                    report_data: Dict = (
                        self._get_element(
                            element_name='report',
                            element_id=report_id,
                            **kwargs
                        )
                    )
                    return report_data
            else:
                return {}
        else:
            raise ValueError('Either report_id or external_id must be provided')

        return report_data


    #############
    ##### Cascade
    #############

    # TODO Guillermo esta no esta implementada en la API
    def get_account_businesses(self):
        raise NotImplementedError

    # TODO Guillermo esta no esta implementada en la API
    def get_business_apps(self, business_id: str) -> List[str]:
        """Given a business retrieve all app ids

        :param business_id: business UUID
        """
        raise NotImplementedError

    # TODO Guillermo esta no esta implementada en la API
    def get_app_all_paths(self, app_id: str) -> List[str]:
        """Given an app retrieve all report_id

        :param app_id: app UUID
        """
        raise NotImplementedError

    # TODO Guillermo esta no esta implementada en la API
    def get_path_all_reports(self, app_id: str, path_name: str) -> List[str]:
        """Given a Path that belongs to an AppId retrieve all reportId

        :param app_id: app UUID
        """
        raise NotImplementedError


    #############
    ##### Multi-level Cascade
    #############

    def get_business_paths(self, business_id: str) -> List[str]:
        """Given a business retrieve all path names

        :param business_id: business UUID
        """
        app_ids: List[str] = self.get_business_apps(business_id=business_id)
        paths: List[str] = []
        for app_id in app_ids:
            app_paths: List[str] = self.get_app_all_paths(app_id=app_id)
            paths = paths + app_paths
        return paths

    def get_business_reports(self, business_id: str) -> List[str]:
        """Given a business retrieve all report ids

        :param business_id: business UUID
        """
        app_ids: List[str] = self.get_business_apps(business_id=business_id)
        report_ids: List[str] = []
        for app_id in app_ids:
            app_report_ids: List[str] = self.get_app_all_reports(app_id=app_id)
            report_ids = report_ids + app_report_ids
        return report_ids

    def get_app_all_reports(self, app_id: str) -> List[str]:
        """Given an app retrieve all report_id

        :param app_id: app UUID
        """
        paths: List[str] = self.get_app_all_paths(app_id=app_id)
        report_ids: List[str] = []
        for path_name in paths:
            path_reports: List[str] = self.get_path_all_reports(path_name=path_name)
            report_ids = report_ids + path_reports
        return report_ids

    #############
    ##### Cascade with filters
    #############

    def get_business_all_apps_with_filter(
            self, business_id: str, app_filter: Dict
    ) -> List[Dict]:
        """
        # TODO filter example!!
        """
        app_ids: List[str] = (
            self.get_business_apps(
                business_id=business_id,
            )
        )

        apps: List[Dict] = []
        for app_id in app_ids:
            app: Dict = self.get_app(app_id)
            for filter_key, filter_value in app_filter.items():
                if app[filter_key] == filter_value:
                    apps.append(app)
        return apps

    def get_app_all_reports_by_filter(
            self, app_id: str,
            report_filter: Dict
    ) -> List[Dict]:
        """Having an AppId first retrieve all reportId that belongs
        to the target AppId. Second filter and take the reportId

        # TODO filter example!!
        """
        report_ids: List[str] = (
            self.get_app_all_reports(
                app_id=app_id,
            )
        )

        reports: List[Dict] = []
        for report_id in report_ids:
            report: Dict = self.get_report(report_id=report_id)
            for filter_key, filter_value in report_filter.items():
                if report[filter_key] == filter_value:
                    reports.append(report)
        return reports


    #############
    ##### Get reports in same
    #############

    def get_all_reports_in_same_app(self, report_id: str) -> List[str]:
        """Return all reports that are in the same app that the target report"""
        report_data: Dict = self.get_report(report_id=report_id)
        app_id: str = report_data['appId']
        return self.get_app_all_reports(app_id)

    def get_all_reports_in_same_path(self, report_id: str) -> List[str]:
        """Return all reports that are in the same path that the target report"""
        report_data: Dict = self.get_report(report_id=report_id)
        path_name: str = report_data['path']
        return self.get_path_all_reports(path_name)

    #############
    ##### Get Metadata
    #############

    def get_app_all_reports_metadata(self, app_id: str) -> List[Dict]:
        """Given an App Id retrieve all reports data from all reports
        that belongs to such App Id.
        """
        report_ids = self.get_app_all_reports(app_id=app_id)
        return [
            self.get_report(report_id=report_id)
            for report_id in report_ids
        ]

    def get_path_all_reports_metadata(self, app_id: str, path: str) -> List[Dict]:
        """Given an App return all Reports data that belong to a target path"""
        results: List[str] = list()
        report_ids: List[str] = self.get_app_all_reports(app_id)
        for report_id in report_ids:
            report: Dict = self.get_report(report_id)
            if report.get('path') == path:
                results.append(report)

        return results


    #############
    ##### Bottom-Up
    #############

    def get_business_id_by_app(self, app_id: str, **kwargs) -> str:
        """Retrieve an specific app_id metadata

        :param app_id: app UUID
        """
        app_data: Dict = self.get_app(app_id=app_id, **kwargs)
        return app_data['businessId']

    def get_app_id_by_report(self, report_id: str, **kwargs) -> str:
        """Bottom-up method
        Having a report_id return the app it belongs to
        """
        report_data: Dict = self.get_report(
            report_id=report_id, **kwargs,
        )
        return report_data['appId']

    def get_business_id_by_report(self, report_id: str, **kwargs) -> str:
        """Bottom-up method
        Having a report_id return the app it belongs to
        """
        app_id: str = self.get_app_id_by_report(report_id=report_id, **kwargs)
        business_id: str = self.get_business_id_by_app(app_id=app_id, **kwargs)
        return business_id

# TODO Guillermo I gonna need an enpoint for this
    def get_path_app(self, path_name: str, **kwargs) -> str:
        """Bottom-up method
        Having a report_id return the app it belongs to
        """
        raise NotImplemented
