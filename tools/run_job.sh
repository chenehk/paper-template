#!/usr/bin/env bash
# Run one exploration job and record its life in an events file, so the job
# reports for itself even when nobody is watching.
# Usage: run_job.sh EVENTS_FILE JOB_NAME -- command ...
set -u
events=$1; name=$2; shift 2
[ "${1:-}" = "--" ] && shift
emit() {  # emit EVENT [extra JSON fields, starting with a comma]
    (
        flock 9
        printf '{"t":"%s","job":"%s","event":"%s","slurm_id":"%s","host":"%s"%s}\n' \
            "$(date -Is)" "$name" "$1" "${SLURM_JOB_ID:-}" "$(hostname -s)" "${2:-}" >> "$events"
    ) 9>>"$events.lock"
}
child=
on_term() {
    emit terminated ',"signal":"TERM"'
    [ -n "$child" ] && kill -TERM "$child" 2>/dev/null && wait "$child"
    exit 143
}
trap on_term TERM INT
emit started
bash -c "$*" &
child=$!
wait "$child"
rc=$?
if [ "$rc" -eq 0 ]; then emit finished ',"exit":0'; else emit failed ",\"exit\":$rc"; fi
exit "$rc"
