# Tech Concept Naming

An Agent Skill for naming **AI tools, agents, Skills, CLI utilities and open-source projects**. Understand the product, explore concepts and meaningful roots, then refine a few names with the creator. Chinese names can be conceived independently of English ones.

[中文](README.md) · [Refinement example](examples/local-refinement.md) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/Ming-Sir-69/tech-concept-naming-skill/issues)

Keep accepted fragments while changing another part, retain or withdraw preferences, and distinguish attested roots from new coinages. An optional Python helper preserves exact fragments and revisioned decisions; the AI handles creative work.

## Install in your project

```sh
DISABLE_TELEMETRY=1 npx --yes skills@1.7.2 add Ming-Sir-69/tech-concept-naming-skill --skill tech-concept-naming --agent codex --copy --yes
```

For Claude Code, use `--agent claude-code`. This optional [Vercel Skills](https://github.com/vercel-labs/skills) installer needs Node.js 22.20.0+ and network access. The environment variable disables its telemetry and associated audit requests. Installation remains project-scoped.

Without Node, download the Skill ZIP and `SHA256SUMS.txt` from [Releases](https://github.com/Ming-Sir-69/tech-concept-naming-skill/releases). Verify the checksum and place its `tech-concept-naming` folder in `.agents/skills/` for Codex or `.claude/skills/` for Claude Code. Reopen the project session.

## Use

In Codex, invoke `$tech-concept-naming`; in Claude Code, use `/tech-concept-naming`. For example:

> Use $tech-concept-naming to name an AI CLI that explains code changes for open-source maintainers. Summarize the product first. Explore three distinct directions, with at most two names each. Coin Chinese names independently and label unverified etymology. Do not modify my code.

Then refine:

> Keep Patch and change only the ending. Avoid bot and -ify. Keep the Chinese name for now. Withdraw the preference for very short names while preserving other decisions.

No script execution or repository access is required for a short naming task. If exact multi-round state is useful, the agent may run `scripts/naming_state.py` with Python 3.9+ (standard library only). Store state in your task workspace and serialize writes. [Helper reference](docs/state-helper.md)

## Update or remove

Run from the project where you installed it:

```sh
DISABLE_TELEMETRY=1 npx --yes skills@1.7.2 update tech-concept-naming --project --yes
DISABLE_TELEMETRY=1 npx --yes skills@1.7.2 remove tech-concept-naming --agent codex --yes
```

Use `--agent claude-code` to remove that installation. For manual installs, replace or remove only the Skill folder. Your separately saved state is yours to retain or delete.

## Requirements and boundaries

Use an Agent Skills-compatible AI host. Host/model access and fees are separate from this MIT-licensed repository. The helper makes no network calls and requires no API key; the host may send task context to its model provider. This project supplies no domain, trademark or dictionary database. Checks must report actual sources and unknowns, and do not guarantee legal clearance or registrability.

[Compatibility](docs/compatibility.md) · [Privacy](docs/privacy.md) · [Contributing](CONTRIBUTING.md)

Development checks: `python3 -m unittest discover -s tests -v`. See [release notes](docs/releasing.md) for maintenance. No hosted service or GitHub workflow is required.
