# Security Baseline

Non-negotiable security rules for all generated code.

## Secrets

1. **Never write a secret into source, config committed to VCS, logs, error messages, or test fixtures.** Secrets come from environment variables or a secret manager, always. Placeholder values in examples must be obviously fake (`sk-XXXX`, `changeme`).
2. **Never log request bodies, headers, or tokens wholesale.** Redact `Authorization`, cookies, passwords, and PII before logging. A debug log is an exfiltration channel with retention.
3. **If you encounter an exposed secret, flag it immediately** and treat it as compromised - rotating it is the fix; deleting the line is not.

## Injection - the one family that never dies

4. **SQL: parameterized queries only.** Never interpolate user input into query strings, even "just for the table name" - use allowlists for identifiers.
5. **Shell: never build command strings from user input.** Use argument arrays / exec APIs that bypass the shell. If a shell is unavoidable, allowlist-validate, don't escape-and-hope.
6. **HTML: encode output by default.** Use framework auto-escaping; treat `dangerouslySetInnerHTML` / `v-html` / `innerHTML` / `| safe` as requiring justification plus sanitization (e.g., DOMPurify).
7. **Paths: resolve and check containment.** User-supplied filenames get normalized, then verified to be inside the intended directory. Reject `..` traversal by checking the resolved path, not the raw string.
8. **Deserialization of untrusted data is code execution** in many stacks (pickle, Java serialization, YAML `load`). Use safe loaders and schema-validated formats (JSON + validation).

## Auth and access

9. **Authorize on the server, per request, per resource.** Hiding a button is not access control. Every endpoint checks both "is this user authenticated" and "may this user touch this specific resource" (IDOR is the standard failure).
10. **Never roll your own crypto or password storage.** Passwords: bcrypt/argon2 via a maintained library. Tokens: generated from a CSPRNG. Comparisons of secrets: constant-time functions.
11. **Fail closed.** If the auth check errors, deny. A try/catch that falls through to "allow" is a vulnerability, not resilience.

## Web specifics

12. **CSRF protection on state-changing endpoints** that use cookie auth (framework middleware or SameSite + token).
13. **Set the boring headers:** `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, HSTS on HTTPS sites. Cookies: `HttpOnly`, `Secure`, `SameSite`.
14. **CORS is an allowlist, not `*`** - especially never `*` with credentials.
15. **Validate on the server regardless of client validation.** Client checks are UX; server checks are security.

## Dependencies and data

16. **Pin dependencies via lockfiles; prefer well-maintained packages.** Before adding a package, glance at maintenance status and download base - typosquats and abandoned packages are real attack surface.
17. **Uploaded files are hostile.** Validate type by content (magic bytes) not extension, cap size, store outside the web root, never execute or include them.
18. **Error messages to users are generic; details go to logs.** Stack traces, SQL fragments, and internal paths in responses are reconnaissance gifts.
