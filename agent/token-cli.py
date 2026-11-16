#!/usr/bin/python3
"""Run locally as www-data: issue/list/revoke account-bound Agent tokens."""
import argparse
import json
import sys
from service import AgentService, ApiError

parser = argparse.ArgumentParser(description=__doc__)
commands = parser.add_subparsers(dest='command', required=True)
issue = commands.add_parser('issue')
issue.add_argument('--user', required=True)
issue.add_argument('--boards', required=True, help='comma-separated IDs')
issue.add_argument('--scopes', required=True, help='topics:write,replies:write')
issue.add_argument('--days', type=int, default=30)
commands.add_parser('list')
commands.add_parser('revoke').add_argument('id')
args = parser.parse_args()
try:
    service = AgentService()
    if args.command == 'issue': result = service.issue(args.user, args.scopes.split(','), [int(x) for x in args.boards.split(',')], args.days * 86400)
    elif args.command == 'list': result = service.list_tokens()
    else:
        service.revoke(args.id)
        result = {'revoked': args.id}
    print(json.dumps(result, ensure_ascii=False))
except (ApiError, ValueError) as error:
    print(str(error), file=sys.stderr)
    sys.exit(1)
