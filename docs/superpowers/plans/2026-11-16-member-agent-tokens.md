# Member Agent authorization implementation plan

Approved design: mobile entry under personal status, classic control-panel entry; retro blue list/create/one-time-secret screens, name/scopes/boards/expiry/password, revoke confirmation and MCP instructions.

1. Implement cookie-authenticated management at /cgi-bin/agenttokens.cgi (preserves legacy /cgi-bin cookie paths), owner-only list/create/revoke, account-bound expiring CSRF challenges, password confirmation/rate limits and one-use create challenges. No user-controlled owner. Keep existing CLI tokens compatible.
2. Add names and last-used timestamps, retain hash-only Token storage and update last use under existing account lock. List only writable boards using legacy settings/member/moderator resolution, recheck issuance and actual writes.
3. Build shared Vue AgentTokens component with mobile cards and classic table/sidebar; routes /m/agent and /cgi-bin/agentpanel.cgi; inject menu link and CGI entrypoints idempotently into persisted installations. Reuse existing GIFs.
4. Test ownership, bad/missing cookie, CSRF, wrong password, permission filtering, duplicate create, secret non-retrieval, revoke and last use. Run real browser creation/list/revoke at narrow and desktop widths in isolated initialized data; no real tokens in screenshots.
5. Update docs/changelog, run existing API/MCP tests, build and update local Docker after checks.
