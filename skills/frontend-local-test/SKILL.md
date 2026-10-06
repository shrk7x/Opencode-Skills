---
name: frontend-local-test
description: Start and test the EpubMaster frontend in its local workspace for a current PR. Use when asked to test the frontend locally, run the local frontend, validate a frontend PR in the workspace, or sign in with a local test account.
---

# EpubMaster local frontend testing

Use this fixed workspace:

`/Users/qiuchen/Desktop/Workplace/EpubMaster/frontend-epub-translator/frontend`

## Workflow

1. Enter the workspace. Inspect the current branch and confirm it contains the target PR's changes. Do not discard, overwrite, or commit unrelated user changes.
2. Start the frontend with `npm run dev` from that directory. Reuse an existing correct local server when safe; otherwise stop only the obsolete server that conflicts with the required port.
3. Open and test `http://localhost:3000`, never `127.0.0.1:3000`. Google OAuth configuration depends on the `localhost` host.
4. Use the in-app browser when the user asks to see or test the page. Use Chrome when the user asks to reuse its existing signed-in session. Keep the requested browser visible when requested. Inspect a fresh DOM snapshot before interaction, and verify a locator is unique before clicking or filling.
5. Reload the local page after frontend code changes, then perform the focused test and report the observed result.

## Test account

All browser acceptance tests run against the **Dev stage**. Default to the Dev-stage account already auto-signed-in in the user's Chrome on `http://localhost:3000`, including paid translation and completed-result download tests. All Dev-stage accounts are user-created testing accounts. Do not inspect or export browser cookies.

Do not use a Beta account or Beta API configuration for local-browser acceptance. Beta deployment is verified separately through deployment/configuration checks; it is not the account-testing environment.

Local credential pairs in `serverless-translator/integration-tests/env.test` are fallback-only because their password-auth flow is not currently usable through this frontend client. Never print, log, commit, or expose their values. Try one only when the user explicitly requests it.

## Test EPUB files

For an end-to-end upload → translate → download test, use the real sample books in:

`/Users/qiuchen/Desktop/Workplace/EpubMaster/epub-translator-desktop/tests/samples/`

Prefer the smallest valid book:

`pg1064-images-3.epub` (about 88 KB)

Use `pg11136-images-3.epub` only when a larger fixture is needed. Do not use `frontend/tests/fixtures/sample.epub`; it is a 19-byte placeholder, not a valid EPUB. Upload only after the user has authorized an end-to-end translation, then verify the completed-file download.

## Boundaries

- This workflow tests the frontend only. Do not deploy beta as part of local testing.
- Do not upload a user file or begin a paid translation unless the user specifically asks for that test.
- If the target PR is absent from the workspace branch, stop and fetch/switch only after preserving unrelated local changes.
