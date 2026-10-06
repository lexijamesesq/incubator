#!/usr/bin/env python3
"""
Strategy Research Database Access Layer

Shared utility for Incubator skills to read/write the strategy research database
(Snowflake). Handles SQL generation, execution, and structured output.

Usage:
    python3 scripts/research-db.py <command> [--json '<args>']

Commands:
    query-landscape     Query competitive landscape by capability slugs
    query-competitor    Deep-dive on a specific competitor
    query-gaps          Detect finding gaps for competitors on given capabilities
    write-finding       Write a research finding + capability links
    write-findings      Batch write multiple findings
    upsert-competitor   Insert or update a competitor row + capability links
    lookup-competitor   Get competitor ID by name
    lookup-capabilities Get capability IDs by slugs
    stats               Database row counts + stale-finding count
    health              Stewardship sweep: stale, orphans, thin records, self-superseded, dupes

Connection details live in scripts/research-db-config.json (gitignored). Copy
research-db-config.sample.json as a starting point.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import uuid

# ---------------------------------------------------------------------------
# Configuration — loaded from research-db-config.json (gitignored)
# ---------------------------------------------------------------------------


def _load_config():
    """Load connection config from the gitignored config file, or
    RESEARCH_DB_CONFIG if set. The env override lets callers (e.g. the eval
    suite) point at a fixture config without swapping the real file."""
    config_path = os.environ.get("RESEARCH_DB_CONFIG") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "research-db-config.json"
    )
    if not os.path.exists(config_path):
        print(
            json.dumps(
                {
                    "error": f"Config file not found: {config_path}. Copy research-db-config.sample.json to research-db-config.json and fill in your connection details."
                }
            )
        )
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def _validate_config(sf):
    """Guard against config states this script must never operate under: an
    unconfigured domain (would silently fall back to another consumer's live
    domain) or an unfilled-in TODO: placeholder in any field (would write
    placeholder text into real SQL). Runs once at module load — before any
    command dispatches — so no call site can be added later that bypasses it.
    """
    errors = []
    if "domain" not in sf or sf.get("domain") is None:
        errors.append(
            "snowflake.domain is not set — copy research-db-config.sample.json and fill in your domain"
        )
    for field in ("role", "database", "schema", "domain"):
        value = sf.get(field)
        if isinstance(value, str) and value.startswith("TODO:"):
            errors.append(
                f"snowflake.{field} is still a placeholder ({value!r}) — fill in your real value"
            )
    if errors:
        print(json.dumps({"error": "config_invalid", "errors": errors}))
        sys.exit(1)


_CONFIG = _load_config()
_sf = _CONFIG.get("snowflake", {})
_validate_config(_sf)
SF_CMD = _sf.get("cli_command", "snow sql --enable-templating NONE")
DOMAIN = _sf["domain"]

# ---------------------------------------------------------------------------
# SQL helpers (Snowflake dialect)
# ---------------------------------------------------------------------------


def sql_preamble():
    role = _sf.get("role", "YOUR_ROLE")
    db = _sf.get("database", "YOUR_DB")
    schema = _sf.get("schema", "YOUR_SCHEMA")
    preamble = f"USE ROLE {role};\nUSE DATABASE {db};\nUSE SCHEMA {schema};\n"
    warehouse = _sf.get("warehouse")
    if warehouse:
        preamble += f"USE WAREHOUSE {warehouse};\n"
    return preamble


def sql_dateadd_months(n, date_col):
    return f"DATEADD('month', {n}, {date_col})"


def sql_count_if(condition):
    return f"COUNT_IF({condition})"


def sql_gen_uuid():
    return str(uuid.uuid4())


def esc(s):
    """Escape backslashes and single quotes for a Snowflake SQL string literal.
    Backslash replacement MUST run first — Snowflake honors backslash as the
    default string-literal escape character, so a value ending in a lone
    backslash can escape a closing quote that only-quote-doubling wouldn't
    catch; escaping backslashes after quotes would double-escape the ones
    quote-doubling just inserted.
    """
    if s is None:
        return None
    return str(s).replace("\\", "\\\\").replace("'", "''")


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

# Substrings that show up in `snow sql` stderr for auth/session failures —
# checked against a FAILED command's stderr only, never a success path, so
# false-positive risk is limited to misclassifying the failure's category.
_AUTH_ERROR_PATTERNS = (
    "authentication failed",
    "incorrect username or password",
    "token has expired",
    "token is invalid",
    "browser response timed out",
    "reauthentication required",
    "oauth",
)


def execute_sql(sql, output_format="default"):
    """Execute SQL against Snowflake. Returns stdout.

    output_format:
        "default" — raw CLI output (table-formatted, for LLM consumption)
        "json"    — JSON-parseable output (for programmatic parsing)

    On failure, exits non-zero with a JSON error on stderr whose "error"
    field distinguishes cli_not_installed / not_authenticated / sql_failure
    — the caller (agent) translates each differently rather than treating
    every failure as an opaque database error.
    """
    fd, tmp = tempfile.mkstemp(prefix="research-db-query-", suffix=".sql")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(sql)

        if output_format == "json":
            cmd = f"{SF_CMD} --format json -f {tmp}"
        else:
            cmd = f"{SF_CMD} -f {tmp}"

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=120
            )
        except OSError as e:
            # shell=True normally surfaces a missing command as a nonzero
            # exit from the shell (see the returncode==127 branch below),
            # not a Python exception — this catches the rarer case where
            # subprocess itself can't launch the shell (e.g. E2BIG).
            print(
                json.dumps(
                    {
                        "error": "cli_not_installed",
                        "message": f"Could not launch the Snowflake CLI: {e}. Check cli_command in research-db-config.json.",
                    }
                ),
                file=sys.stderr,
            )
            sys.exit(1)

        if result.returncode != 0:
            stderr = result.stderr.strip()
            stderr_lower = stderr.lower()
            if (
                result.returncode == 127
                or "command not found" in stderr_lower
                or "no such file or directory" in stderr_lower
            ):
                print(
                    json.dumps(
                        {
                            "error": "cli_not_installed",
                            "message": stderr
                            or "Snowflake CLI not found on PATH. Check cli_command in research-db-config.json.",
                        }
                    ),
                    file=sys.stderr,
                )
            elif any(p in stderr_lower for p in _AUTH_ERROR_PATTERNS):
                print(
                    json.dumps({"error": "not_authenticated", "message": stderr}),
                    file=sys.stderr,
                )
            else:
                print(
                    json.dumps({"error": "sql_failure", "message": stderr}),
                    file=sys.stderr,
                )
            sys.exit(1)

        return result.stdout.strip()
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def parse_json_result(output):
    """Parse JSON output from `snow sql --format json`.

    The CLI emits a list of result sets (one per statement). Preamble USE
    statements produce empty or status-only result sets; the data result is the
    last non-empty one.
    """
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    for result_set in reversed(data):
        if (
            isinstance(result_set, list)
            and result_set
            and isinstance(result_set[0], dict)
        ):
            # Filter out USE statement status rows (single 'status' key)
            if not (len(result_set[0]) == 1 and "status" in result_set[0]):
                return result_set
    return []


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_query_landscape(args):
    """Query competitive landscape by capability slugs.

    Returns competitors tagged to the given capabilities, with their findings
    and gap indicators. Sorted by tier then category.
    """
    caps = args.get("capabilities", [])
    if not caps:
        print(json.dumps({"error": "capabilities list required"}))
        sys.exit(1)

    cap_list = ",".join(f"'{esc(c)}'" for c in caps)
    ttl_filter = sql_dateadd_months("rf.ttl_months", "rf.created_at")

    sql = f"""{sql_preamble()}
SELECT '--- COMPETITORS ---' AS section;

SELECT c.name, c.category, c.market_tier, c.pricing_model,
  array_agg(DISTINCT cap.slug) AS matched_caps
FROM competitors c
JOIN competitor_capabilities cc ON c.id = cc.competitor_id
JOIN capabilities cap ON cc.capability_id = cap.id
WHERE cap.slug IN ({cap_list})
  AND c.superseded_by IS NULL
GROUP BY c.id, c.name, c.category, c.market_tier, c.pricing_model
ORDER BY
  CASE c.market_tier WHEN 'tier-1' THEN 1 WHEN 'tier-2' THEN 2 WHEN 'tier-3' THEN 3 END,
  CASE c.category WHEN 'core' THEN 1 WHEN 'adjacent' THEN 2 WHEN 'emerging' THEN 3 WHEN 'substitute' THEN 4 END;

SELECT '--- FINDINGS ---' AS section;

SELECT rf.category AS finding_type, rf.confidence, LEFT(rf.claim, 200) AS claim,
  LEFT(rf.evidence, 100) AS evidence, c.name AS competitor_name
FROM research_findings rf
JOIN finding_capabilities fc ON rf.id = fc.finding_id
JOIN capabilities cap ON fc.capability_id = cap.id
LEFT JOIN competitors c ON rf.competitor_id = c.id
WHERE cap.slug IN ({cap_list})
  AND rf.superseded_by IS NULL
  AND {ttl_filter} > CURRENT_DATE
GROUP BY rf.id, rf.category, rf.confidence, rf.claim, rf.evidence, c.name
ORDER BY
  CASE rf.confidence WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END,
  rf.category
LIMIT 40;
"""

    print(execute_sql(sql))


def cmd_query_competitor(args):
    """Deep-dive on a specific competitor."""
    name = args.get("name")
    if not name:
        print(json.dumps({"error": "name required"}))
        sys.exit(1)

    sql = f"""{sql_preamble()}
-- Competitor profile
SELECT c.id, ANY_VALUE(c.domain) AS domain, ANY_VALUE(c.name) AS name,
  ANY_VALUE(c.category) AS category, ANY_VALUE(c.segments) AS segments,
  ANY_VALUE(c.pricing_model) AS pricing_model,
  ANY_VALUE(c.integration_posture) AS integration_posture,
  ANY_VALUE(c.market_tier) AS market_tier,
  ANY_VALUE(c.intelligence) AS intelligence,
  ANY_VALUE(c.last_researched) AS last_researched,
  ANY_VALUE(c.superseded_by) AS superseded_by,
  ANY_VALUE(c.created_at) AS created_at,
  ANY_VALUE(c.created_by) AS created_by,
  array_agg(DISTINCT cap.slug) AS capabilities
FROM competitors c
LEFT JOIN competitor_capabilities cc ON c.id = cc.competitor_id
LEFT JOIN capabilities cap ON cc.capability_id = cap.id
WHERE c.name = '{esc(name)}' AND c.superseded_by IS NULL
GROUP BY c.id;

-- Linked findings
SELECT rf.id, rf.topic, rf.category, rf.claim, rf.evidence,
  rf.confidence, rf.source_url, rf.ttl_months, rf.created_at
FROM research_findings rf
WHERE rf.competitor_id = (SELECT id FROM competitors WHERE name = '{esc(name)}' AND superseded_by IS NULL)
  AND rf.superseded_by IS NULL
ORDER BY rf.created_at DESC;
"""
    print(execute_sql(sql))


def cmd_query_gaps(args):
    """Detect finding gaps: competitors tagged to capabilities but with no matching findings."""
    caps = args.get("capabilities", [])
    if not caps:
        print(json.dumps({"error": "capabilities list required"}))
        sys.exit(1)

    cap_list = ",".join(f"'{esc(c)}'" for c in caps)

    sql = f"""{sql_preamble()}
SELECT c.name, c.category, c.market_tier, cap.slug AS capability,
  CASE WHEN COUNT(DISTINCT rf.id) = 0 THEN 'GAP' ELSE 'COVERED' END AS status,
  COUNT(DISTINCT rf.id) AS finding_count
FROM competitors c
JOIN competitor_capabilities cc ON c.id = cc.competitor_id
JOIN capabilities cap ON cc.capability_id = cap.id
LEFT JOIN research_findings rf ON c.id = rf.competitor_id AND rf.superseded_by IS NULL
LEFT JOIN finding_capabilities fc ON rf.id = fc.finding_id AND fc.capability_id = cap.id
WHERE cap.slug IN ({cap_list}) AND c.superseded_by IS NULL
GROUP BY c.name, c.category, c.market_tier, cap.slug
ORDER BY
  CASE WHEN COUNT(DISTINCT rf.id) = 0 THEN 0 ELSE 1 END,
  c.market_tier, c.category, c.name;
"""
    print(execute_sql(sql))


CLAIM_MIN_CHARS = 30
QUERY_STRING_PATTERN = __import__("re").compile(
    r'^[\s\-*]*(?:Query\s+\d+:\s*)?"[^"]+"\s*$'
)


def _validate_finding(f, idx=None):
    """Defense-in-depth validation for a single finding dict.
    Returns list of error strings (empty list = valid).
    Catches: missing fields, empty capabilities, query-string claims, stub claims,
    and missing source URL+description (four anti-patterns observed in the educator-sme research).
    """
    errors = []
    prefix = f"finding[{idx}]: " if idx is not None else ""
    required = [
        "claim",
        "evidence",
        "confidence",
        "ttl_months",
        "category",
        "topic",
        "capabilities",
    ]
    for field in required:
        if field not in f or f[field] is None:
            errors.append(f"{prefix}missing required field: {field}")
    if "capabilities" in f and not f["capabilities"]:
        errors.append(
            f"{prefix}capabilities must be a non-empty list (junction rows silently drop otherwise)"
        )
    claim = (f.get("claim") or "").strip()
    if claim and len(claim) < CLAIM_MIN_CHARS:
        errors.append(
            f"{prefix}claim too short ({len(claim)} chars; min {CLAIM_MIN_CHARS}) — write a substantive assertion, not a stub"
        )
    if claim and QUERY_STRING_PATTERN.match(claim):
        errors.append(
            f"{prefix}claim looks like a search query string — claims must be assertions, not research metadata"
        )
    if not f.get("source_url") and not f.get("source_description"):
        errors.append(
            f"{prefix}source_url OR source_description required (capture heuristic: Sourced is a gate)"
        )
    if "ttl_months" in f and f["ttl_months"] is not None:
        try:
            # Normalize in place so every downstream SQL interpolation site
            # uses a real int — never a string an attacker could shape into
            # a raw-SQL breakout (ttl_months is interpolated unquoted).
            f["ttl_months"] = int(f["ttl_months"])
        except (ValueError, TypeError):
            errors.append(f"{prefix}ttl_months must be a numeric value")
    return errors


def cmd_write_finding(args):
    """Write a single research finding + capability junction rows."""
    errors = _validate_finding(args)
    if errors:
        print(json.dumps({"error": "validation_failed", "errors": errors}))
        sys.exit(1)

    finding_id = sql_gen_uuid()
    competitor_id = args.get("competitor_id")
    source_url = args.get("source_url")
    source_desc = args.get("source_description")
    cap_slugs = args["capabilities"]

    lines = [sql_preamble()]

    url_val = f"'{esc(source_url)}'" if source_url else "NULL"
    desc_val = f"'{esc(source_desc)}'" if source_desc else "NULL"
    comp_val = f"'{esc(competitor_id)}'" if competitor_id else "NULL"

    lines.append(f"""
INSERT INTO research_findings (id, domain, topic, category, agent_type, claim, evidence,
  source_url, source_description, confidence, ttl_months, competitor_id)
VALUES ('{finding_id}', '{DOMAIN}', '{esc(args["topic"])}', '{esc(args["category"])}', NULL,
  '{esc(args["claim"])}', '{esc(args["evidence"])}',
  {url_val}, {desc_val}, '{esc(args["confidence"])}', {args["ttl_months"]}, {comp_val});
""")

    for slug in cap_slugs:
        lines.append(f"""
INSERT INTO finding_capabilities (finding_id, capability_id)
SELECT '{finding_id}', id FROM capabilities WHERE slug = '{esc(slug)}';
""")

    sql = "\n".join(lines)
    execute_sql(sql)
    print(json.dumps({"finding_id": finding_id, "capabilities": cap_slugs}))


def cmd_write_findings(args):
    """Batch write multiple findings using INSERT...SELECT...UNION ALL."""
    findings = args.get("findings", [])
    if not findings:
        print(json.dumps({"error": "findings list required"}))
        sys.exit(1)

    all_errors = []
    for i, f in enumerate(findings):
        all_errors.extend(_validate_finding(f, idx=i))
    if all_errors:
        print(json.dumps({"error": "validation_failed", "errors": all_errors}))
        sys.exit(1)

    lines = [sql_preamble()]
    result_ids = []

    for f in findings:
        f["_id"] = sql_gen_uuid()
        result_ids.append({"finding_id": f["_id"], "claim_preview": f["claim"][:80]})

    lines.append(
        "INSERT INTO research_findings (id, domain, topic, category, agent_type, claim, evidence, source_url, source_description, confidence, ttl_months, competitor_id)"
    )
    lines.append("SELECT * FROM (")
    for i, f in enumerate(findings):
        prefix = "    SELECT " if i == 0 else "    UNION ALL SELECT "
        url = f"'{esc(f.get('source_url'))}'" if f.get("source_url") else "NULL"
        desc = (
            f"'{esc(f.get('source_description'))}'"
            if f.get("source_description")
            else "NULL"
        )
        comp = f"'{esc(f['competitor_id'])}'" if f.get("competitor_id") else "NULL"
        lines.append(
            f"{prefix}'{f['_id']}', '{DOMAIN}', '{esc(f['topic'])}', '{esc(f['category'])}', NULL, '{esc(f['claim'])}', '{esc(f['evidence'])}', {url}, {desc}, '{esc(f['confidence'])}', {f['ttl_months']}, {comp}"
        )
    lines.append(");")

    junction_rows = []
    for f in findings:
        for slug in f.get("capabilities", []):
            junction_rows.append((f["_id"], slug))

    if junction_rows:
        lines.append("\nINSERT INTO finding_capabilities (finding_id, capability_id)")
        lines.append("SELECT fc.fid, c.id FROM (")
        for i, (fid, slug) in enumerate(junction_rows):
            prefix = "    SELECT " if i == 0 else "    UNION ALL SELECT "
            lines.append(f"{prefix}'{fid}' AS fid, '{esc(slug)}' AS slug")
        lines.append(") fc JOIN capabilities c ON fc.slug = c.slug;")

    sql = "\n".join(lines)
    execute_sql(sql)
    print(
        json.dumps(
            {
                "findings_written": len(findings),
                "junction_rows": len(junction_rows),
                "ids": result_ids,
            }
        )
    )


def cmd_lookup_competitor(args):
    """Get competitor ID and basic info by name."""
    name = args.get("name")
    if not name:
        print(json.dumps({"error": "name required"}))
        sys.exit(1)

    sql = f"""{sql_preamble()}
SELECT id, name, category, market_tier FROM competitors
WHERE name ILIKE '%{esc(name)}%' AND superseded_by IS NULL
ORDER BY name;
"""
    output = execute_sql(sql, output_format="json")
    rows = parse_json_result(output)
    print(json.dumps(rows))


def cmd_lookup_capabilities(args):
    """Get capability IDs by slugs."""
    slugs = args.get("slugs", [])
    if not slugs:
        sql = f"{sql_preamble()}\nSELECT slug, id FROM capabilities ORDER BY slug;"
    else:
        slug_list = ",".join(f"'{esc(s)}'" for s in slugs)
        sql = f"{sql_preamble()}\nSELECT slug, id FROM capabilities WHERE slug IN ({slug_list}) ORDER BY slug;"

    output = execute_sql(sql, output_format="json")
    rows = parse_json_result(output)
    print(json.dumps(rows))


CATEGORY_ENUM = {"core", "adjacent", "emerging", "substitute"}
SEGMENT_ENUM = {"k-12", "higher-ed", "certification", "workforce"}
MARKET_TIER_ENUM = {"tier-1", "tier-2", "tier-3"}
INTELLIGENCE_BODY_MIN = 50


def cmd_upsert_competitor(args):
    """Insert or update a competitor row + capability junction rows.

    Required fields (insert): name, category, segments, market_tier, capabilities[],
    intelligence_body, plus source_url OR source_description.
    Required fields (update): name (lookup key). Other fields applied if provided.

    Gates:
      - category must be in CATEGORY_ENUM
      - each segment must be in SEGMENT_ENUM
      - market_tier must be in MARKET_TIER_ENUM
      - all capability slugs must exist
      - intelligence_body min 50 chars at insert
      - fuzzy name dup check on insert (rejected unless force_create=True)
      - category change on update returns warning unless force_category_change=True
        (intended for human use only — skills should never pass this flag)

    Returns JSON with action: created | updated | rejected_dup | rejected_validation
                              | needs_category_confirmation
    """
    name = args.get("name", "").strip()
    if not name:
        print(json.dumps({"error": "name required"}))
        sys.exit(1)

    force_create = args.get("force_create", False)
    force_category_change = args.get("force_category_change", False)

    # 1. Look up by exact name (case-insensitive) across ALL rows including superseded.
    # The dup-detection pass must see superseded rows so we don't quietly duplicate
    # a soft-deleted/self-superseded competitor.
    sql_lookup = f"""{sql_preamble()}
SELECT id, name, category, segments, pricing_model, integration_posture,
  market_tier, intelligence, last_researched, superseded_by
FROM competitors
WHERE LOWER(name) = LOWER('{esc(name)}')
ORDER BY (superseded_by IS NULL) DESC, created_at DESC
LIMIT 1;
"""
    existing = parse_json_result(execute_sql(sql_lookup, output_format="json"))

    # If the matched row is superseded (including self-supersession), surface to human.
    # Skills must NOT auto-revive — that's a deliberate decision.
    if existing and existing[0].get("SUPERSEDED_BY"):
        sup_id = existing[0]["SUPERSEDED_BY"]
        is_self_super = sup_id == existing[0]["ID"]
        print(
            json.dumps(
                {
                    "action": "found_superseded",
                    "id": existing[0]["ID"],
                    "name": existing[0]["NAME"],
                    "superseded_by": sup_id,
                    "self_superseded": is_self_super,
                    "message": (
                        f"Competitor '{name}' exists but is superseded "
                        f"({'self-superseded — soft-deleted state' if is_self_super else f'replaced by {sup_id}'}). "
                        "Surface to human. To revive, run: UPDATE competitors SET superseded_by = NULL WHERE id = '"
                        + existing[0]["ID"]
                        + "'; "
                        "then re-run upsert-competitor to refresh the row."
                    ),
                }
            )
        )
        sys.exit(0)

    is_update = bool(existing)

    # 2. Validate required fields based on action
    errors = []
    category = args.get("category")
    if category and category not in CATEGORY_ENUM:
        errors.append(
            f"category must be one of {sorted(CATEGORY_ENUM)}, got '{category}'"
        )
    segments = args.get("segments", [])
    for s in segments:
        if s not in SEGMENT_ENUM:
            errors.append(f"segment '{s}' must be one of {sorted(SEGMENT_ENUM)}")
    market_tier = args.get("market_tier")
    if market_tier and market_tier not in MARKET_TIER_ENUM:
        errors.append(
            f"market_tier must be one of {sorted(MARKET_TIER_ENUM)}, got '{market_tier}'"
        )
    intelligence_body = args.get("intelligence_body", "")
    capabilities = args.get("capabilities", [])

    if not is_update:
        # Insert: stronger requirements
        if not category:
            errors.append("category required for insert")
        if not segments:
            errors.append("segments required for insert (at least one)")
        if not market_tier:
            errors.append("market_tier required for insert")
        if not capabilities:
            errors.append("capabilities required for insert (at least one)")
        if not intelligence_body or len(intelligence_body) < INTELLIGENCE_BODY_MIN:
            errors.append(
                f"intelligence_body required for insert, min {INTELLIGENCE_BODY_MIN} chars"
            )
        if not args.get("source_url") and not args.get("source_description"):
            errors.append(
                "source_url OR source_description required for insert (evidence requirement)"
            )

    if errors:
        print(json.dumps({"action": "rejected_validation", "errors": errors}))
        sys.exit(1)

    # 3. Validate capability slugs exist
    if capabilities:
        cap_list = ",".join(f"'{esc(s)}'" for s in capabilities)
        sql_caps = f"{sql_preamble()}\nSELECT id, slug FROM capabilities WHERE slug IN ({cap_list});"
        cap_rows = parse_json_result(execute_sql(sql_caps, output_format="json"))
        found_slugs = {r["SLUG"] for r in cap_rows}
        missing = [s for s in capabilities if s not in found_slugs]
        if missing:
            print(
                json.dumps(
                    {
                        "action": "rejected_validation",
                        "errors": [f"unknown capability slugs: {missing}"],
                    }
                )
            )
            sys.exit(1)
        cap_id_by_slug = {r["SLUG"]: r["ID"] for r in cap_rows}

    # 4. INSERT path
    if not is_update:
        # Fuzzy name dup check
        sql_fuzzy = f"""{sql_preamble()}
SELECT id, name, category FROM competitors
WHERE superseded_by IS NULL AND LOWER(name) LIKE LOWER('%{esc(name)}%')
LIMIT 5;
"""
        fuzzy = parse_json_result(execute_sql(sql_fuzzy, output_format="json"))
        if fuzzy and not force_create:
            print(
                json.dumps(
                    {
                        "action": "rejected_dup",
                        "message": f"Possible duplicates of '{name}' found. Re-run with force_create=true to insert anyway.",
                        "candidates": fuzzy,
                    }
                )
            )
            sys.exit(1)

        new_id = sql_gen_uuid()
        seg_array = "ARRAY_CONSTRUCT(" + ",".join(f"'{esc(s)}'" for s in segments) + ")"
        ip_array = "NULL"
        if args.get("integration_posture"):
            ip_array = (
                "ARRAY_CONSTRUCT("
                + ",".join(f"'{esc(p)}'" for p in args["integration_posture"])
                + ")"
            )
        intel_json = json.dumps(
            {
                "body": intelligence_body,
                "source_url": args.get("source_url"),
                "source_description": args.get("source_description"),
            }
        )
        pricing = args.get("pricing_model")
        pricing_val = f"'{esc(pricing)}'" if pricing else "NULL"

        lines = [sql_preamble()]
        lines.append(f"""
INSERT INTO competitors (id, domain, name, category, segments, pricing_model,
  integration_posture, market_tier, intelligence, last_researched)
SELECT '{new_id}', '{DOMAIN}', '{esc(name)}', '{category}', {seg_array}, {pricing_val},
  {ip_array}, '{market_tier}', PARSE_JSON('{esc(intel_json)}'), CURRENT_DATE;
""")
        # Junction rows
        for slug in capabilities:
            cap_id = cap_id_by_slug[slug]
            lines.append(
                f"INSERT INTO competitor_capabilities (competitor_id, capability_id) VALUES ('{new_id}', '{cap_id}');"
            )
        execute_sql("\n".join(lines))
        print(json.dumps({"action": "created", "id": new_id, "name": name}))
        return

    # 5. UPDATE path
    row = existing[0]
    existing_id = row["ID"]
    warnings = []

    # Category change gate
    if category and category != row["CATEGORY"]:
        if not force_category_change:
            print(
                json.dumps(
                    {
                        "action": "needs_category_confirmation",
                        "id": existing_id,
                        "name": name,
                        "current_category": row["CATEGORY"],
                        "proposed_category": category,
                        "message": "Category changes are gated. Surface to human; rerun with force_category_change=true (human-only) to apply.",
                    }
                )
            )
            sys.exit(0)
        warnings.append(f"category changed: {row['CATEGORY']} → {category}")

    set_clauses = []
    if category and category != row["CATEGORY"] and force_category_change:
        set_clauses.append(f"category = '{category}'")
    if segments:
        seg_array = "ARRAY_CONSTRUCT(" + ",".join(f"'{esc(s)}'" for s in segments) + ")"
        set_clauses.append(f"segments = {seg_array}")
    if market_tier and market_tier != row["MARKET_TIER"]:
        set_clauses.append(f"market_tier = '{market_tier}'")
    if "pricing_model" in args:
        pricing = args.get("pricing_model")
        pv = f"'{esc(pricing)}'" if pricing else "NULL"
        set_clauses.append(f"pricing_model = {pv}")
    if "integration_posture" in args:
        ip = args["integration_posture"]
        if ip:
            iv = "ARRAY_CONSTRUCT(" + ",".join(f"'{esc(p)}'" for p in ip) + ")"
        else:
            iv = "NULL"
        set_clauses.append(f"integration_posture = {iv}")
    if intelligence_body:
        if len(intelligence_body) < INTELLIGENCE_BODY_MIN:
            print(
                json.dumps(
                    {
                        "action": "rejected_validation",
                        "errors": [
                            f"intelligence_body min {INTELLIGENCE_BODY_MIN} chars"
                        ],
                    }
                )
            )
            sys.exit(1)
        intel_json = json.dumps(
            {
                "body": intelligence_body,
                "source_url": args.get("source_url"),
                "source_description": args.get("source_description"),
            }
        )
        set_clauses.append(f"intelligence = PARSE_JSON('{esc(intel_json)}')")
    # Always stamp last_researched on update
    set_clauses.append("last_researched = CURRENT_DATE")

    sql_update = f"{sql_preamble()}\nUPDATE competitors SET {', '.join(set_clauses)} WHERE id = '{existing_id}';"
    execute_sql(sql_update)

    # Capabilities: replace junction rows if capabilities provided
    if capabilities:
        lines = [sql_preamble()]
        lines.append(
            f"DELETE FROM competitor_capabilities WHERE competitor_id = '{existing_id}';"
        )
        for slug in capabilities:
            cap_id = cap_id_by_slug[slug]
            lines.append(
                f"INSERT INTO competitor_capabilities (competitor_id, capability_id) VALUES ('{existing_id}', '{cap_id}');"
            )
        execute_sql("\n".join(lines))

    print(
        json.dumps(
            {"action": "updated", "id": existing_id, "name": name, "warnings": warnings}
        )
    )


def cmd_health(args):
    """Stewardship sweep: stale findings, orphans, thin records, self-superseded
    rows, suspected duplicates, capability coverage. Returns a structured JSON
    report. Read-only — does not mutate.
    """
    sql = f"""{sql_preamble()}
-- 1. Stale findings (past TTL, still active)
SELECT 'stale_findings' AS check_name, id, LEFT(claim, 80) AS claim_preview,
  ttl_months, created_at::DATE AS created
FROM research_findings
WHERE superseded_by IS NULL
  AND DATEADD('month', ttl_months, created_at) < CURRENT_DATE
ORDER BY created_at;

-- 2. Orphan competitors (active, zero linked findings)
SELECT 'orphan_competitors' AS check_name, c.id, c.name, c.category, c.market_tier
FROM competitors c
LEFT JOIN research_findings rf ON rf.competitor_id = c.id AND rf.superseded_by IS NULL
WHERE c.superseded_by IS NULL
GROUP BY c.id, c.name, c.category, c.market_tier
HAVING COUNT(rf.id) = 0
ORDER BY c.name;

-- 3. Orphan capabilities (zero competitors tagged AND zero findings tagged)
SELECT 'orphan_capabilities' AS check_name, cap.slug,
  COUNT(DISTINCT cc.competitor_id) AS competitor_count,
  COUNT(DISTINCT fc.finding_id) AS finding_count
FROM capabilities cap
LEFT JOIN competitor_capabilities cc ON cc.capability_id = cap.id
LEFT JOIN finding_capabilities fc ON fc.capability_id = cap.id
GROUP BY cap.slug
HAVING COUNT(DISTINCT cc.competitor_id) = 0 AND COUNT(DISTINCT fc.finding_id) = 0
ORDER BY cap.slug;

-- 4. Thin competitor intelligence (active, no body AND no structured intel)
-- A row is "thin" only if intelligence is null OR has no useful keys.
-- Body-shape rows: intelligence:body must be >= 50 chars.
-- Structured-shape rows: intelligence has at least 1 non-body key.
SELECT 'thin_competitors' AS check_name, id, name,
  COALESCE(LENGTH(intelligence:body::VARCHAR), 0) AS body_len,
  CASE WHEN intelligence IS NULL THEN 0 ELSE ARRAY_SIZE(OBJECT_KEYS(intelligence)) END AS key_count
FROM competitors
WHERE superseded_by IS NULL
  AND (
    intelligence IS NULL
    OR ARRAY_SIZE(OBJECT_KEYS(intelligence)) = 0
    OR (
      -- has body key but body is too short, AND has no other content keys
      intelligence:body IS NOT NULL
      AND LENGTH(intelligence:body::VARCHAR) < 50
      AND ARRAY_SIZE(ARRAY_EXCEPT(OBJECT_KEYS(intelligence), ARRAY_CONSTRUCT('body', 'source_url', 'source_description'))) = 0
    )
    OR (
      -- no body key AND no structured content keys
      intelligence:body IS NULL
      AND ARRAY_SIZE(ARRAY_EXCEPT(OBJECT_KEYS(intelligence), ARRAY_CONSTRUCT('source_url', 'source_description'))) = 0
    )
  )
ORDER BY body_len, name;

-- 5. Findings missing both source_url and source_description
SELECT 'unsourced_findings' AS check_name, id, LEFT(claim, 80) AS claim_preview, created_at::DATE AS created
FROM research_findings
WHERE superseded_by IS NULL
  AND source_url IS NULL
  AND (source_description IS NULL OR TRIM(source_description) = '')
ORDER BY created_at;

-- 6. Self-superseded competitors (soft-deleted state — invisible to most queries)
SELECT 'self_superseded_competitors' AS check_name, id, name, created_at::DATE AS created
FROM competitors
WHERE superseded_by = id
ORDER BY name;

-- 7. Suspected duplicates (active competitors where one name is a substring of another)
SELECT 'suspected_duplicate_competitors' AS check_name,
  a.name AS name_a, b.name AS name_b, a.category AS category_a, b.category AS category_b
FROM competitors a
JOIN competitors b
  ON a.id < b.id
  AND (LOWER(a.name) LIKE '%' || LOWER(b.name) || '%'
       OR LOWER(b.name) LIKE '%' || LOWER(a.name) || '%')
WHERE a.superseded_by IS NULL AND b.superseded_by IS NULL
ORDER BY a.name, b.name;

-- 8. Capability coverage summary (any capability with under 2 competitors flagged thin)
SELECT 'thin_capability_coverage' AS check_name, cap.slug,
  COUNT(DISTINCT cc.competitor_id) AS competitor_count
FROM capabilities cap
LEFT JOIN competitor_capabilities cc ON cc.capability_id = cap.id
GROUP BY cap.slug
HAVING COUNT(DISTINCT cc.competitor_id) BETWEEN 1 AND 2
ORDER BY competitor_count, cap.slug;
"""
    output = execute_sql(sql, output_format="json")
    try:
        all_results = json.loads(output)
    except json.JSONDecodeError:
        print(
            json.dumps({"error": "could not parse health output", "raw": output[:500]})
        )
        sys.exit(1)

    # Group results by check_name
    report = {
        "stale_findings": [],
        "orphan_competitors": [],
        "orphan_capabilities": [],
        "thin_competitors": [],
        "unsourced_findings": [],
        "self_superseded_competitors": [],
        "suspected_duplicate_competitors": [],
        "thin_capability_coverage": [],
    }
    for result_set in all_results:
        if not isinstance(result_set, list) or not result_set:
            continue
        first = result_set[0]
        if not isinstance(first, dict):
            continue
        if len(first) == 1 and "status" in first:
            continue
        check_name = first.get("CHECK_NAME")
        if check_name and check_name in report:
            report[check_name] = [
                {k: v for k, v in row.items() if k != "CHECK_NAME"}
                for row in result_set
            ]

    summary = {
        check: {"count": len(rows), "rows": rows} for check, rows in report.items()
    }
    print(json.dumps(summary, indent=2, default=str))


def cmd_stats(args):
    """Database health summary."""
    active_comp = sql_count_if("superseded_by IS NULL")
    active_find = sql_count_if("superseded_by IS NULL")
    sql = f"""{sql_preamble()}
SELECT 'competitors' AS entity, COUNT(*) AS total,
  {active_comp} AS active FROM competitors
UNION ALL SELECT 'findings', COUNT(*), {active_find} FROM research_findings
UNION ALL SELECT 'capabilities', COUNT(*), COUNT(*) FROM capabilities
UNION ALL SELECT 'comp_caps', COUNT(*), COUNT(*) FROM competitor_capabilities
UNION ALL SELECT 'find_caps', COUNT(*), COUNT(*) FROM finding_capabilities;

SELECT COUNT(*) AS stale_findings FROM research_findings
WHERE superseded_by IS NULL
  AND {sql_dateadd_months("ttl_months", "created_at")} < CURRENT_DATE;
"""
    print(execute_sql(sql))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

COMMANDS = {
    "query-landscape": cmd_query_landscape,
    "query-competitor": cmd_query_competitor,
    "query-gaps": cmd_query_gaps,
    "write-finding": cmd_write_finding,
    "write-findings": cmd_write_findings,
    "upsert-competitor": cmd_upsert_competitor,
    "lookup-competitor": cmd_lookup_competitor,
    "lookup-capabilities": cmd_lookup_capabilities,
    "stats": cmd_stats,
    "health": cmd_health,
}


def main():
    parser = argparse.ArgumentParser(
        description="Strategy Research Database Access Layer"
    )
    parser.add_argument("command", choices=COMMANDS.keys())
    parser.add_argument("--json", type=str, default="{}", help="JSON arguments")
    parsed = parser.parse_args()

    try:
        args = json.loads(parsed.json)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    COMMANDS[parsed.command](args)


if __name__ == "__main__":
    main()
