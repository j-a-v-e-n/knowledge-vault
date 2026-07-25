# Local GitHub CLI capability receipt

- observed_at_utc: `2026-07-25T16:34:08Z`
- command_1: `gh --version`
- command_1_output:

```text
gh version 2.95.0 (2026-06-17)
https://github.com/cli/cli/releases/tag/v2.95.0
```

- command_2: `gh attestation verify --help`
- selected_exact_output_from_command_2:

```text
In order to verify an attestation, you must provide an artifact and validate:
* the identity of the actor that produced the attestation
* the expected attestation predicate type (the nature of the claim)

The "actor identity" consists of:
* the repository or the repository owner the artifact is linked with
* the Actions workflow that produced the attestation (a.k.a the
  signer workflow)

IMPORTANT: please note that only the `signature.certificate` and the
`verifiedTimestamps` properties contain values that cannot be
manipulated by the workflow that originated the attestation.

When designing policy enforcement using this output, special care must be taken
when examining the contents of the `statement.predicate` property:
should an attacker gain access to your workflow's execution context, they
could then falsify the contents of the `statement.predicate`.

      --cert-identity string         Enforce that the certificate's SubjectAlternativeName matches the provided value exactly
      --cert-oidc-issuer string      Enforce that the issuer of the OIDC token matches the provided value (default "https://token.actions.githubusercontent.com")
      --deny-self-hosted-runners     Fail verification for attestations generated on self-hosted runners
      --predicate-type string        Enforce that verified attestations' predicate type matches the provided value (default "https://slsa.dev/provenance/v1")
  -R, --repo string                  Repository name in the format <owner>/<repo>
      --signer-digest string         Enforce that the digest associated with the signer workflow matches the provided value
      --signer-repo string           Enforce that the workflow that signed the attestation's repository matches the provided value (<owner>/<repo>)
      --signer-workflow string       Enforce that the workflow that signed the attestation matches the provided value ([host/]<owner>/<repo>/<path>/<to>/<workflow>)
      --source-digest string         Enforce that the digest associated with the source repository matches the provided value
      --source-ref string            Enforce that the git ref associated with the source repository matches the provided value
```

- execution_boundary: No `gh attestation verify` command was run because no artifact/bundle receipt exists for this RS-05 research task. No workflow was triggered or modified.

