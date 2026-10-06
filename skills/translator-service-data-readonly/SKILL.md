---
name: translator-service-data-readonly
description: Use when querying live AWS data for the serverless translator service, including user data, DynamoDB tables, CloudWatch logs, Step Functions executions, S3 objects, Cognito users, billing-related records, beta data, dev data, or production diagnostics.
---

# Translator Service Data Readonly

## Core Rule

For any live AWS data query related to the serverless translator service, use the AWS profile `read-only` by default.

This applies when inspecting data, logs, executions, users, jobs, translations, entitlements, token balances, uploads, or operational state. Do not use admin SSO profiles for read-only investigation unless the user explicitly asks for a different profile.

## Required Defaults

- AWS profile: `read-only`
- Region: `us-east-1`
- Account verified for this profile: `641965853046`
- Identity pattern: `arn:aws:iam::641965853046:user/ReadOnly`

## Query Pattern

1. Use `--profile read-only --region us-east-1` on AWS CLI commands.
2. Prefer live reads over cached notes or older command output.
3. Do not mutate resources: no writes, deletes, imports, deploys, invalidations, or state-machine starts.
4. If a command fails with missing permissions, report the missing access and do not retry with an administrator profile unless the user explicitly authorizes that profile.
5. When showing user or customer data, include only fields needed for the user request.

## Common Commands

```bash
aws sts get-caller-identity --profile read-only --region us-east-1
aws dynamodb scan --table-name Users-beta --profile read-only --region us-east-1
aws logs filter-log-events --log-group-name <group> --profile read-only --region us-east-1
aws stepfunctions describe-execution --execution-arn <arn> --profile read-only --region us-east-1
aws s3 ls s3://<bucket>/<prefix> --profile read-only --region us-east-1
aws cognito-idp list-users --user-pool-id <pool> --profile read-only --region us-east-1
```

## Common Mistakes

| Mistake | Correct behavior |
| --- | --- |
| Using `AdministratorAccess-641965853046` for ordinary investigation | Use `read-only` unless the user explicitly requested admin access |
| Reusing old user table output | Query the live table again |
| Running a write command while "just checking" | Stop and ask for explicit permission with the intended write profile |
| Omitting the profile and relying on defaults | Add `--profile read-only` explicitly |

## Related Skill

For a compact view of `Users-beta` fields, use `users-beta-table` after applying this profile rule.
