"""The MariaDB kernel"""
# Copyright (c) MariaDB Foundation.
# Distributed under the terms of the Modified BSD License.

from ipykernel.kernelbase import Kernel

from mariadb_kernel._version import __version__
from mariadb_kernel.client_config import ClientConfig
from mariadb_kernel.mariadb_client import MariaDBClient
from mariadb_kernel.code_parser import CodeParser

import logging
import pexpect
import re


class MariaDBKernel(Kernel):
    implementation = "MariaDB"
    implementation_version = __version__
    language_info = {
        "name": "SQL",
        "mimetype": "text/plain",
        "file_extension": ".sql",
    }
    banner = "MariaDB kernel"

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self.log.setLevel(logging.INFO)
        self.client_config = ClientConfig(self.log)
        self.mariadb_client = MariaDBClient(self.log, self.client_config)

        self.mariadb_client.start()

    def _execute_magics(self, magics):
        # TODO: implement execution of magics
        self.log.error(f"########## parsed magics: {magics}")

    def do_execute(
        self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        parser = CodeParser(code)

        self._execute_magics(parser.get_magics())

        result = self.mariadb_client.run_statement(parser.get_sql())

        if not silent:
            display_content = {"data": {"text/html": str(result)}, "metadata": {}}
            self.send_response(self.iopub_socket, "display_data", display_content)

        return {
            "status": "ok",
            # The base class increments the execution count
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }

    def do_shutdown(self, restart):
        self.mariadb_client.stop()

    def do_complete(self, code, cursor_pos):
        return {"status": "ok", "matches": ["test"]}