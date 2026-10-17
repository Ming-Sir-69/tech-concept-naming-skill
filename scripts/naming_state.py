#!/usr/bin/env python3
"""Small deterministic state helper for an AI-led naming Skill (Python 3.9+).

This program never invents names, infers etymologies, ranks quality, or contacts a service.
It only preserves explicit user decisions and edits candidate parts precisely.
"""
import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import unicodedata

SCHEMA = "tech-concept-naming/v1"
STATUSES = {"draft", "shortlisted", "rejected", "chosen"}


class StateError(Exception):
    pass


def fail_if_symlink(path):
    if path.is_symlink():
        raise StateError("Refusing symlink state path")


def clean_text(value, field="text", *, max_length=240):
    if not isinstance(value, str):
        raise StateError("%s must be a string" % field)
    value = unicodedata.normalize("NFC", value)
    if not value.strip() or "\x00" in value or len(value) > max_length:
        raise StateError("%s must be nonempty, <= %d codepoints, no NUL" % (field, max_length))
    return value


def clean_parts(parts):
    if not isinstance(parts, list) or not 1 <= len(parts) <= 32:
        raise StateError("parts must be a JSON list containing 1..32 nonempty strings")
    return [clean_text(p, "part", max_length=80) for p in parts]


def assembled(parts):
    return "".join(parts)


def exclusions(state, name):
    lower = name.casefold()
    return [s for s in state["preferences"]["ban_fragments"] if s.casefold() in lower]


def check_candidate(state, parts):
    name = assembled(parts)
    if len(name) > 240:
        raise StateError("Assembled name exceeds 240 codepoints")
    bans = exclusions(state, name)
    if bans:
        raise StateError("Candidate contains explicitly banned fragment(s): %s" % ", ".join(bans))
    return name


def load(path):
    fail_if_symlink(path)
    if not path.is_file():
        raise StateError("State file does not exist; run init first")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise StateError("Could not read valid JSON state: %s" % exc)
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise StateError("Unknown state schema; refusing modification")
    if not isinstance(data.get("revision"), int) or not isinstance(data.get("candidates"), dict):
        raise StateError("Invalid state structure")
    if not isinstance(data.get("preferences"), dict):
        raise StateError("Invalid preferences")
    for key in ("like", "avoid", "ban_fragments"):
        if not isinstance(data["preferences"].get(key), list):
            raise StateError("Invalid preference list: %s" % key)
    return data


def write_atomic(path, state):
    """Durable single-writer replace; --expect prevents stale sequential edits.

    Callers must serialize parallel writers. This is not multi-process locking.
    """
    fail_if_symlink(path)
    fd, tmp = tempfile.mkstemp(prefix=".naming-state-", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(state, out, ensure_ascii=False, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def snapshot(state, only_id=None):
    result = copy.deepcopy(state)
    if only_id is not None:
        if only_id not in state["candidates"]:
            raise StateError("Unknown candidate: %s" % only_id)
        result["candidates"] = {only_id: result["candidates"][only_id]}
    for candidate in result["candidates"].values():
        parts = candidate["parts"]
        candidate["assembled"] = assembled(parts)
        candidate["codepoints"] = len(candidate["assembled"])
        candidate["part_codepoints"] = [len(s) for s in parts]
        candidate["excluded_fragments"] = exclusions(state, candidate["assembled"])
    return result


def event(state, action, details):
    state["revision"] += 1
    state["events"].append({
        "revision": state["revision"], "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "action": action, "details": details,
    })


def edit_state(state, args):
    command = args.command
    if command == "add":
        ident = clean_text(args.id, "id", max_length=64)
        if ident in state["candidates"]:
            raise StateError("Candidate ID already exists; use edit on its parts")
        try:
            parts = clean_parts(json.loads(args.parts_json))
        except ValueError as exc:
            raise StateError("Invalid --parts-json: %s" % exc)
        name = check_candidate(state, parts)
        c = {"parts": parts, "status": "draft", "rationale": args.rationale or "",
             "localized": {}}
        if args.zh:
            c["localized"]["zh-CN"] = {"name": clean_text(args.zh, "Chinese name"), "reason": args.zh_reason or ""}
        state["candidates"][ident] = c
        event(state, command, {"id": ident, "name": name})
    elif command in ("edit", "insert", "remove"):
        c = state["candidates"].get(args.id)
        if c is None:
            raise StateError("Unknown candidate: %s" % args.id)
        before = copy.deepcopy(c["parts"])
        parts = c["parts"][:]
        i = args.index
        if command == "insert":
            if not 0 <= i <= len(parts):
                raise StateError("Insert index out of range")
            parts.insert(i, clean_text(args.text, "part", max_length=80))
        else:
            if not 0 <= i < len(parts):
                raise StateError("Part index out of range")
            if command == "edit":
                parts[i] = clean_text(args.text, "part", max_length=80)
            else:
                parts.pop(i)
        parts = clean_parts(parts)
        check_candidate(state, parts)
        c["parts"] = parts
        event(state, command, {"id": args.id, "index": i, "before": before, "after": parts})
    elif command == "localize":
        c = state["candidates"].get(args.id)
        if c is None:
            raise StateError("Unknown candidate: %s" % args.id)
        lang = clean_text(args.lang, "language", max_length=24)
        old = copy.deepcopy(c["localized"].get(lang))
        c["localized"][lang] = {"name": clean_text(args.name, "localized name"), "reason": args.reason or ""}
        event(state, command, {"id": args.id, "lang": lang, "before": old, "after": c["localized"][lang]})
    elif command == "rationale":
        c = state["candidates"].get(args.id)
        if c is None:
            raise StateError("Unknown candidate: %s" % args.id)
        old = c["rationale"]
        c["rationale"] = clean_text(args.text, "rationale", max_length=4000)
        event(state, command, {"id": args.id, "before": old, "after": c["rationale"]})
    elif command == "preference":
        value = clean_text(args.value, "preference")
        key = {"like": "like", "avoid": "avoid", "ban": "ban_fragments"}[args.kind]
        existing = state["preferences"][key]
        if args.remove:
            matches = [v for v in existing if v.casefold() == value.casefold()]
            if not matches:
                raise StateError("Preference not found in %s" % args.kind)
            existing[:] = [v for v in existing if v.casefold() != value.casefold()]
        elif not any(v.casefold() == value.casefold() for v in existing):
            existing.append(value)
        event(state, command, {"kind": args.kind, "value": value,
                               "operation": "remove" if args.remove else "add"})
    elif command == "status":
        c = state["candidates"].get(args.id)
        if c is None:
            raise StateError("Unknown candidate: %s" % args.id)
        if args.value == "chosen" and any(v["status"] == "chosen" and k != args.id
                                          for k, v in state["candidates"].items()):
            raise StateError("Another candidate is chosen; change that status explicitly first")
        old = c["status"]
        c["status"] = args.value
        event(state, command, {"id": args.id, "from": old, "to": args.value})
    else:
        raise StateError("Unsupported mutation: %s" % command)


def parser():
    p = argparse.ArgumentParser(description="Deterministic candidate parts and preferences for AI-led naming")
    commands = p.add_subparsers(dest="command", required=True)
    q = commands.add_parser("init", help="Create a state file without overwriting an existing file")
    q.add_argument("path")
    q.add_argument("--brief", required=True)
    q.add_argument("--audience", default="AI tool developers")
    q = commands.add_parser("show", help="Show machine-readable candidate state and part-length previews")
    q.add_argument("path")
    q.add_argument("--id")
    def mutating(command, help_text):
        s = commands.add_parser(command, help=help_text)
        s.add_argument("path")
        s.add_argument("--expect", type=int, required=True, help="Current revision from show")
        return s
    q = mutating("add", "Add a new candidate, preserving segment boundaries")
    q.add_argument("--id", required=True)
    q.add_argument("--parts-json", required=True)
    q.add_argument("--rationale", default="")
    q.add_argument("--zh", default="")
    q.add_argument("--zh-reason", default="")
    for action in ("edit", "insert", "remove"):
        q = mutating(action, "Change one candidate part without rewriting the rest")
        q.add_argument("--id", required=True)
        q.add_argument("--index", type=int, required=True, help="0-based part index")
        if action != "remove":
            q.add_argument("--text", required=True)
    q = mutating("localize", "Set an independent localized name, not a word-for-word translation")
    q.add_argument("--id", required=True)
    q.add_argument("--lang", default="zh-CN")
    q.add_argument("--name", required=True)
    q.add_argument("--reason", default="")
    q = mutating("rationale", "Store an Agent-provided explanation; does not verify etymology or change names")
    q.add_argument("--id", required=True)
    q.add_argument("--text", required=True)
    q = mutating("preference", "Record a positive, negative, or literal banned fragment")
    q.add_argument("--kind", choices=["like", "avoid", "ban"], required=True)
    q.add_argument("--value", required=True)
    q.add_argument("--remove", action="store_true", help="Withdraw only this preference; retain history and other choices")
    q = mutating("status", "Mark one candidate draft, shortlisted, rejected or chosen")
    q.add_argument("--id", required=True)
    q.add_argument("--value", choices=sorted(STATUSES), required=True)
    return p


def run(argv=None):
    args = parser().parse_args(argv)
    path = Path(args.path).expanduser()
    if args.command == "init":
        if not path.parent.is_dir():
            raise StateError("State parent directory does not exist")
        fail_if_symlink(path)
        value = {"schema": SCHEMA, "revision": 0, "brief": {"intent": clean_text(args.brief, "brief", max_length=4000),
                 "audience": args.audience}, "preferences": {"like": [], "avoid": [], "ban_fragments": []},
                 "candidates": {}, "events": []}
        try:
            fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(value, f, ensure_ascii=False, indent=2)
                f.write("\n")
        except FileExistsError:
            raise StateError("State file already exists; never overwriting via init")
        state = value
    else:
        state = load(path)
        if args.command == "show":
            print(json.dumps(snapshot(state, args.id), ensure_ascii=False, indent=2))
            return 0
        if args.expect != state["revision"]:
            raise StateError("Stale revision: expected %d, current %d" % (args.expect, state["revision"]))
        edit_state(state, args)
        write_atomic(path, state)
    print(json.dumps(snapshot(state), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except (StateError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(2)
