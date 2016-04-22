# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

def resource_path(relative):
    """ Gets the resource's absolute path.

    :param relative: the relative path to the resource file.
    :return: the absolute path to the resource file.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)

    abspath = os.path.abspath(os.path.join(__file__, ".."))
    abspath = os.path.dirname(abspath)
    return os.path.join(abspath, relative)

