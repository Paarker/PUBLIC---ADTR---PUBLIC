# ADTR — AI Decision Transparency Record

A standard format for documenting decisions made with AI coding assistants.

## Why this exists

When a developer uses Copilot, Cursor, Claude, or any other AI assistant to make technical decisions, there's usually no structured record of what happened. What did the AI suggest? What did the developer actually do? Why?

That's a problem for anyone who needs to audit, review, or understand AI-assisted work — whether that's an engineering manager doing a post-incident review, a regulated industry proving due diligence, or a team trying to onboard someone into a codebase full of AI-generated code.

ADTR is a simple JSON-based record format. One record per AI interaction. It captures what was asked, what the AI said, what the human decided, and why. Nothing more.

## Schema overview

Each record has three layers:

1. **Record Envelope** — identity, timing, tool info, integrity hash. Required on every record.
2. **Activity Payload** — the actual interaction: what kind of activity it was, what the AI suggested, what the developer decided and why. This is the important part.
3. **Context Tags** — optional. Routing metadata, confidence scores, file attachments. Extensible.

See `schema/adtr-v0.1.schema.json` for the full spec.

## Getting started

```bash
pip install adtr-validate  # coming soon — not on PyPI yet
adtr-validate my-records/*.json
```

Or pipe from stdin:
```bash
cat record.json | adtr-validate --stdin
```

## Status

**v0.1** — still in design. Schema will change. Don't build production systems on this yet.

- [x] JSON Schema v0.1 (draft)
- [x] Example records
- [ ] CLI validator on PyPI
- [ ] Reference docs
- [ ] VS Code extension / GitHub Action examples

## Funding

Applying for a grant from [NLnet](https://nlnet.nl/) via the [NGI Zero Commons Fund](https://nlnet.nl/commonsfund/) (EU Next Generation Internet programme).

## License

Code and spec: [Apache 2.0](LICENSE). Docs: [CC-BY-SA 4.0](docs/LICENSE).

## Contributing

Not accepting PRs yet — schema needs to stabilise first. Issues welcome.

---

Made by [Paarker SRL](https://paarker.com), Milan.
