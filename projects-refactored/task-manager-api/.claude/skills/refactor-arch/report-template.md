# Audit Report Template

Use this exact format for the Phase 2 audit report.
Save the report to `reports/audit-project-<N>.md`.

---

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project:   <project-folder-name>
Stack:     <Language> + <Framework>
Files:     <N> analyzed | ~<LOC> lines of code
================================

## Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>
Total findings: <N>

## Findings

### [CRITICAL] <Finding Title>
File:           <relative/path/to/file.py>:<start_line>-<end_line>
Relevant code:
  <short snippet — 2–5 lines showing the issue>
Description:    <What is wrong and why it is dangerous. One to three sentences.>
Impact:         <The concrete harm an attacker or bug can cause.>
Recommendation: <The specific fix — name the function, pattern, or library to use.>

### [CRITICAL] <Finding Title>
…

### [HIGH] <Finding Title>
File:           …
Relevant code:
  …
Description:    …
Impact:         …
Recommendation: …

### [HIGH] …

### [MEDIUM] …

### [LOW] …

================================
Total: <N> findings
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>
================================
```

---

## Rules for Filling the Template

1. **Order findings by severity** — CRITICAL first, then HIGH, MEDIUM, LOW.
2. **Every finding must cite an exact file and line range.** Do not write "throughout the codebase" — pick the primary location.
3. **The relevant code snippet must be the actual problematic code**, not a comment or surrounding boilerplate. Keep it to 2–5 lines.
4. **Impact must be concrete.** Instead of "security risk", write "an attacker can log in as any user by supplying `' OR '1'='1` as the email".
5. **Recommendation must name the solution.** Instead of "fix the validation", write "use parameterized queries: `cursor.execute('SELECT … WHERE id = ?', (id,))`".
6. **Minimum finding counts per project:**
   - At least 1 CRITICAL or HIGH
   - At least 2 MEDIUM
   - At least 2 LOW
   - At least 5 total
7. **Deprecated API detection:** If the project uses deprecated framework APIs (e.g., Flask `before_first_request`, SQLAlchemy 1.x `Query.get()`, Express 4.x `app.del()`), add a finding tagged `[MEDIUM]` or `[LOW]` noting the deprecation and the replacement.

---

## Example Finding

```
### [CRITICAL] SQL Injection in product search
File:           models.py:285-297
Relevant code:
  query = "SELECT * FROM produtos WHERE 1=1"
  if termo:
      query += " AND (nome LIKE '%" + termo + "%')"
  cursor.execute(query)
Description:    User-supplied search term is concatenated directly into the SQL
                string. An attacker can supply `%' UNION SELECT senha FROM usuarios --`
                to exfiltrate all passwords from the users table.
Impact:         Full database read access to any authenticated or unauthenticated
                caller of GET /produtos/busca?q=<payload>.
Recommendation: Use parameterized queries with LIKE placeholders:
                cursor.execute(
                    "SELECT * FROM produtos WHERE nome LIKE ?",
                    (f"%{termo}%",)
                )
```

---

## Phase 2 Output Checklist

Before saving the report, verify:
- [ ] All CRITICAL findings listed first
- [ ] Each finding has file path + line numbers
- [ ] Each finding has a code snippet (not pseudocode)
- [ ] Impact describes concrete harm (not "may cause issues")
- [ ] Recommendation names a specific fix (not "improve security")
- [ ] Deprecated API findings included if applicable
- [ ] Summary counts match the actual finding list
- [ ] Report saved to `reports/audit-project-<N>.md`
