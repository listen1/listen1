#!/usr/bin/env python
"""Fabfile using only commands from buedafab (https://github.com/bueda/ops) to
deploy this app to remote servers.
"""

import os
from fabric.api import *

from buedafab.test import (test, tornado_test_runner as _tornado_test_runner,
        lint)
from buedafab.deploy.types import tornado_deploy as deploy
from buedafab.environments import development, staging, production, localhost
from buedafab.tasks import (setup, restart_webserver, rollback, enable,
        disable, maintenancemode, rechef)

# For a description of these attributes, see https://github.com/bueda/ops

env.unit = "boilerplate"
env.path = "/var/webapps/%(unit)s" % env
env.scm = "git@github.com:bueda/%(unit)s.git" % env
env.scm_http_url = "http://github.com/bueda/%(unit)s" % env
env.root_dir = os.path.abspath(os.path.dirname(__file__))
env.test_runner = _tornado_test_runner

env.pip_requirements = ["requirements/common.txt",
        "vendor/allo/pip-requirements.txt",]
env.pip_requirements_dev = ["requirements/dev.txt",]
env.pip_requirements_production = ["requirements/production.txt",]
