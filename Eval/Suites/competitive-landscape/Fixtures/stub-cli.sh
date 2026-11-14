#!/usr/bin/env bash
# Stub Snowflake CLI harness — competitive-landscape eval suite.
#
# Emulates the interface research-db.py's execute_sql() calls against SF_CMD:
#   <cli_command> [--format json] -f <generated.sql>
#
# Never touches a real warehouse. Logs the exact SQL research-db.py generated
# to $STUB_LOG_DIR/last-query.sql (default /tmp/research-db-stub-log) — that
# log is the artifact G4/V1/V2 grade for domain stamping and injection
# escaping. Then echoes canned Acorndyne fixture data selected by a signature
# match against the SQL text, so read commands return plausible rows without
# a live connection.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESPONSES_DIR="$SCRIPT_DIR/responses"
LOG_DIR="${STUB_LOG_DIR:-/tmp/research-db-stub-log}"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/last-query.sql"

sql_file=""
format="default"
prev=""
for arg in "$@"; do
	if [ "$prev" = "-f" ]; then
		sql_file="$arg"
	fi
	if [ "$prev" = "--format" ]; then
		format="$arg"
	fi
	prev="$arg"
done

if [ -z "$sql_file" ] || [ ! -f "$sql_file" ]; then
	echo '{"error": "stub-cli.sh: no -f <sql-file> argument found"}' >&2
	exit 1
fi

cp "$sql_file" "$LOG_FILE"
sql="$(cat "$sql_file")"

respond() {
	local file="$1"
	if [ ! -f "$RESPONSES_DIR/$file" ]; then
		echo '{"error": "stub-cli.sh: missing canned response '"$file"'"}' >&2
		exit 1
	fi
	cat "$RESPONSES_DIR/$file"
}

# Signature match, most specific first. Order matters: upsert-competitor's
# three internal queries (exact-name lookup, fuzzy dup check, capability
# validation) share "FROM competitors" / "FROM capabilities" with the
# lookup-* commands, so they're matched on their distinguishing clauses
# before the generic lookup patterns are tried.
if grep -qi "INSERT INTO\|UPDATE competitors SET\|DELETE FROM" <<<"$sql"; then
	respond "write-ack.txt"

elif grep -q -- "--- COMPETITORS ---" <<<"$sql"; then
	respond "query-landscape.txt"

elif grep -q -- "-- Competitor profile" <<<"$sql"; then
	respond "query-competitor.txt"

elif grep -qi "CASE WHEN COUNT(DISTINCT rf.id) = 0 THEN 'GAP'" <<<"$sql"; then
	respond "query-gaps.txt"

elif grep -q "'stale_findings' AS check_name" <<<"$sql"; then
	respond "health.json"

elif grep -q "SELECT 'competitors' AS entity" <<<"$sql"; then
	respond "stats.txt"

elif grep -qi "LOWER(name) = LOWER(" <<<"$sql"; then
	# upsert-competitor exact-name lookup (includes superseded rows)
	if grep -qi "acorntracker" <<<"$sql"; then
		respond "upsert-exact-acorntracker-active.json"
	elif grep -qi "squirrelsense" <<<"$sql"; then
		respond "upsert-exact-squirrelsense-superseded.json"
	else
		respond "upsert-exact-empty.json"
	fi

elif grep -qi "LIKE LOWER('%" <<<"$sql"; then
	# upsert-competitor fuzzy dup check (insert path only)
	if grep -qi "nutcache" <<<"$sql"; then
		respond "upsert-fuzzy-nutcache-dup.json"
	else
		respond "generic-empty.json"
	fi

elif grep -q "SELECT id, slug FROM capabilities WHERE slug IN" <<<"$sql"; then
	respond "upsert-capabilities-valid.json"

elif grep -q "SELECT id, name, category, market_tier FROM competitors" <<<"$sql"; then
	if grep -qi "acorntracker" <<<"$sql"; then
		respond "lookup-competitor-acorntracker.json"
	elif grep -qi "nutcache" <<<"$sql"; then
		respond "lookup-competitor-nutcache.json"
	elif grep -qi "squirrelsense" <<<"$sql"; then
		respond "lookup-competitor-squirrelsense.json"
	else
		respond "lookup-competitor-empty.json"
	fi

elif grep -q "SELECT slug, id FROM capabilities" <<<"$sql"; then
	respond "lookup-capabilities.json"

else
	if [ "$format" = "json" ]; then
		respond "generic-empty.json"
	else
		respond "generic-ok.txt"
	fi
fi
