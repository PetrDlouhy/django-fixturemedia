"""Utilities module."""

import re


file_patt = re.compile(r'"?(?:media://)?([^"]+?[\/\\]+[^"]+?\.[^."]+?)"?$',
                       re.MULTILINE)
file_patt_prefixed = re.compile(r'"?media://([^"]+?[\/\\]+[^"]+?\.[^."]+?)"?$',
                                re.MULTILINE)
