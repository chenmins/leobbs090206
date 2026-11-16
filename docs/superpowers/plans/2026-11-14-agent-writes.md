# Agent write API implementation plan

Continue the approved MCP roadmap with UTF-8 JSON topic/reply creation, account-bound scoped tokens, durable idempotency and real legacy permission checks. Keep stdio transport; remote HTTP MCP and browser token-management UI are outside this increment.

## Design

Use an Apache CGI Python adapter plus a private Perl worker which invokes the existing post.cgi. Reusing the legacy writer avoids reproducing moderation, flood control and GBK storage rules. Tokens are issued/revoked by a local operator command, contain 256 bits of randomness, and are stored only as SHA-256 digests with account password fingerprints, expiration, scopes and board IDs. No password is exposed to MCP. Cookie-based authentication is internal to the worker only.

The adapter stores token, audit and idempotency data in a persistent directory denied by Apache. Per-account locking in the container /run directory serializes retries (bind-mount flock proved unreliable on Docker Desktop); a shared post lock also serializes classic and API posting. Persist an in-progress record before invoking the writer. Completed identical requests replay their result; conflicts and unresolved writes return 409 without invoking the writer again. Do not claim transactionality for the legacy multi-file store.

## Tasks

- [x] Add failing tests for token scope/revocation, JSON validation and idempotency.
- [x] Implement token CLI, write adapter and legacy structured-result worker.
- [x] Deploy outside persisted source mounts; idempotently install the shared posting lock in existing post.cgi.
- [x] Add MCP create_topic/reply_topic only when a token is configured; explicit idempotency key, no automatic retries, write annotations.
- [x] Run isolated Docker tests: Chinese/UBB posts and replies, concurrent identical requests, scope and account restrictions, flood control, revocation and restart. Unit tests cover token expiry/password changes and uncertain outcomes.
- [x] Run existing read-only MCP/mobile tests and update API/usage/changelog documentation.
