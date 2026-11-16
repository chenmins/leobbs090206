#!/usr/bin/python3
# Deployment-owned bridge; keep management on the legacy Cookie path.
import runpy
import sys
sys.path.insert(0, '/opt/leobbs-agent')
runpy.run_path('/opt/leobbs-agent/manage.cgi', run_name='__main__')
