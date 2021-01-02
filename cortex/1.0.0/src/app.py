#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import urllib3
import cortex4py 
from cortex4py.api import Api

from walkoff_app_sdk.app_base import AppBase

class Cortex(AppBase):
    __version__ = "1.0.0"
    app_name = "cortex"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        super().__init__(redis, logger, console_logger)

    async def get_available_analyzers(self, apikey, url, datatype):
        self.api = Api(url, apikey, cert=False)
        try:
            analyzers = self.api.analyzers.find_all({}, range='all')
        except cortex4py.exceptions.ServiceUnavailableError as e:
            return [e]
        except cortex4py.exceptions.AuthorizationError as e:
            return [e]
        except cortex4py.exceptions.NotFoundError as e:
            return [e]

        if len(analyzers) == 0:
            return []

        all_results = []
        for analyzer in analyzers:
            if not datatype in analyzer.dataTypeList:
                continue

            all_results.append(analyzer.name)

        return all_results

    async def run_available_analyzers(self, apikey, url, data, datatype, message="", tlp=1):
        self.api = Api(url, apikey, cert=False)
        analyzers = await self.get_available_analyzers(apikey, url, datatype)

        alljobs = []
        for analyzer in analyzers:
            try:
                job = self.api.analyzers.run_by_name(analyzer, {
                    'data': data,
                    'dataType': datatype,
                    'tlp': tlp,
                    'message': message,
                }, force=1)

                alljobs.append(job.id)
            except cortex4py.exceptions.ServiceUnavailableError as e:
                return [e]
            except cortex4py.exceptions.AuthorizationError as e:
                return [e]
            except cortex4py.exceptions.NotFoundError as e:
                return [e]

        return alljobs

    async def run_analyzer(self, apikey, url, analyzer_name, data, datatype, message="", tlp=1):
        self.api = Api(url, apikey, cert=False)
        try:
            job = self.api.analyzers.run_by_name(analyzer_name, {
                'data': data,
                'dataType': datatype,
                'tlp': tlp,
                'message': message,
            }, force=1)
        except cortex4py.exceptions.ServiceUnavailableError as e:
            return e
        except cortex4py.exceptions.AuthorizationError as e:
            return e
        except cortex4py.exceptions.NotFoundError as e:
            return e

        return job.id

    async def get_analyzer_result(self, url, apikey, result_id):
        self.api = Api(url, apikey, cert=False)
        try:
            report = self.api.jobs.get_report(result_id).report
        except cortex4py.exceptions.ServiceUnavailableError as e:
            return e
        except cortex4py.exceptions.AuthorizationError as e:
            return e
        except cortex4py.exceptions.NotFoundError as e:
            return e

        return report 

if __name__ == "__main__":
    asyncio.run(Cortex.run(), debug=True)
