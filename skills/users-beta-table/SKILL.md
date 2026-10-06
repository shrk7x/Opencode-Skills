---
name: users-beta-table
description: Use when the user asks to show or inspect the `Users-beta` table and wants the latest live values for user id, email, active paid jobs, and token balance.
---

# Users Beta Table

## Purpose

Show the current contents of the `Users-beta` DynamoDB table from the `read-only` AWS profile.

## When to Use

Use this skill whenever the user asks for:
- the `Users-beta` table
- a user balance table view
- user id, email, active jobs, or token balance from `Users-beta`

## Required Behavior

Each time this skill is used:
- Query the live `Users-beta` table again
- Do not reuse an older snapshot
- Do not infer or cache values between runs
- Show each row with:
  - `user_id`
  - `email`
  - `active_paid_jobs`
  - `token_balance`

## Data Source

- AWS profile: `read-only`
- Region: `us-east-1`
- Table name: `Users-beta`

## Output Format

Prefer a compact table sorted by email or creation time if available.

If a field is missing, show `null` rather than guessing.

## Notes

- The table is the source of truth for this request.
- If the user asks for related fields like `subscription_status` or `created_at`, include them only if requested.
