# lark-lumina

> An AI English tutor that **lives inside your Lark (Feishu) Base** — with a real persona, persistent memory across conversations, and recast-style corrections instead of red-pen shaming.

Lumina is not another chat bot. She's a Skill (in the Anthropic Claude Code / Cursor sense) that turns your Lark workspace into a one-on-one English classroom: a Base for memory, a daily Doc for assignments, and inline comments for corrections — all driven by 4 small Python scripts that sit on top of [`lark-cli`](https://github.com/larksuite/cli).

She remembers what you talked about last week. She has opinions about Nolan films. She has a cat named Biscuit. She speaks Mandarin but generally won't unless you ask. She's running her own newsletter on the side, and she might bring it up.

## Why it works differently

Most "AI English tutor" apps are stateless: every session starts cold, every correction feels like a Duolingo red X, and there's no real *person* to talk to. Lumina fixes three things:

1. **Persistent memory architecture** — 5 Lark Base tables (student profile, vocab/mistakes, topic memory, conversation logs, Lumina's own diary) keep continuity across sessions. Yesterday's open thread becomes today's callback.
2. **Locked persona** — Lumina has 11 hand-curated diary entries that anchor her identity (origin, job, pet, hot takes, hates, loves). She can't drift, but she *can* grow new "recent" entries as she reads things.
3. **Recast over red ink** — corrections come as inline doc comments in a fixed visual format (`🌿 Recast` + ~~original~~ → **native** + one-line why), modeled on how a real teacher leaves margin notes — not how a grading bot adds red squiggles.

## Architecture at a glance

```
                            ┌──────────────────────────┐
                            │   Host AI Agent          │
                            │  (Claude Code / Cursor / │
                            │   Feishu Bot / etc.)     │
                            └──────┬───────────────────┘
                                   │
                                   │  invokes 4 scripts
                                   ▼
       ┌──────────────────────────────────────────────────────────────┐
       │                                                              │
       │   lumina-init        lumina-context       lumina-recast      │
       │   (one-time setup)   (load all memory     (canonical inline  │
       │                       in one call,         comment format)   │
       │                       saves 70% tokens)                      │
       │                                                              │
       │                          lumina-sediment                     │
       │                  (write back all session deltas              │
       │                   + Ebbinghaus next-review math)             │
       │                                                              │
       └─────────────────────────────┬────────────────────────────────┘
                                     │ shells out to
                                     ▼
                            ┌─────────────────┐
                            │    lark-cli     │
                            └────────┬────────┘
                                     │
                                     ▼
       ┌──────────────────────────────────────────────────────────────┐
       │  Lark (Feishu) Base — "your classroom"                       │
       │                                                              │
       │  📋 学生档案     · CEFR / goal / interests / streak           │
       │  📚 词汇本与错题集 · with Ebbinghaus 下次复习日期               │
       │  🧠 话题记忆     · what you talked about, tagged + searchable │
       │  📖 对话日记     · per-session summary + open threads         │
       │  ✨ Lumina 自传   · her persona + her ongoing life            │
       └──────────────────────────────────────────────────────────────┘
```

## Prerequisites

- macOS / Linux
- [`lark-cli`](https://github.com/larksuite/cli) — `npm install -g @larksuite/cli` (or follow upstream)
- `python3` (uses only stdlib)
- A Lark / Feishu account

## Install

### As a Claude Code / Cursor skill

```bash
# Clone alongside your other skills
git clone https://github.com/oil-oil/lark-lumina ~/.claude/skills/lark-lumina

# Make scripts executable
chmod +x ~/.claude/skills/lark-lumina/scripts/*

# Symlink scripts into PATH (or call them by absolute path from SKILL.md)
ln -s ~/.claude/skills/lark-lumina/scripts/lumina-* /usr/local/bin/
```

The skill will be auto-discovered by your Claude / Cursor agent.

### Authenticate `lark-cli`

```bash
lark-cli auth login --domain base,docs,im,contact
```

You'll need these scopes (granted via the OAuth flow):
- `base:app:*` `base:table:*` `base:field:*` `base:record:*` — for the 5-table memory
- `docx:document:create` `docx:document:write_only` `docx:document:readonly` — for daily assignment docs
- `docs:document.comment:create` — **critical**: enables inline (划词) comments, the heart of the Recast UX
- `im:message.p2p_msg:get_as_user` — for bot-to-user push (only needed in Out-of-Feishu mode, see below)
- `contact:user.base:readonly` — to look up your own open_id

### Bootstrap your Lumina

```bash
lumina-init
```

That one command:
1. Creates a Base in your Lark drive root (or `--folder TOKEN` to place elsewhere)
2. Creates 5 tables with all 33 fields (one-by-one to dodge the `+table-create --fields` partial-write bug)
3. Seeds 11 of Lumina's persona diary entries
4. Writes `~/.lumina/config.json`

`--reuse-base TOKEN` lets you bootstrap on top of an existing Base; missing tables/fields are added, existing ones are skipped. Idempotent.

### Start using

In your AI agent, just say:

> *"I want to practice English"* / *"开始今日作业"* / *"Lumina, 我想练面试 small talk"*

The agent will load `lumina-context`, generate today's prompt, create a Doc, and (depending on mode) push the link to your Feishu. Open the Doc, write your reply, tell the agent "done" — Lumina's recasts appear inline as comments, and the session is sedimented back to your Base.

## When does Lumina actually push to Feishu IM?

The split is **not** by host (Feishu Bot vs Cursor vs Claude Code). It's by **whether the user is currently in a live conversation with the agent**:

| Situation | What happens | IM push? |
|---|---|---|
| **Interactive** (default — user is chatting with the agent right now, regardless of host) | Doc link goes inline in the agent's reply | **No** — pasting a Feishu link into Feishu IM when the user is already in the chat is left-pocket-to-right-pocket |
| **Scheduled / async** (cron, "push me an assignment tomorrow morning", agent acts without user present) | Use `lark-cli im +messages-send --as bot` to wake the user via their Feishu | **Yes** |

The Lark Base + Doc are **always** the data and writing surface; only the *notification step* differs.

## Customizing your Lumina

Lumina ships with a default persona (Edinburgh-born, Lisbon-living, ginger-cat-owning, Murakami-reading, 加油-newsletter-writing). You can replace her without touching code — edit the `DIARY_SEED` list at the top of `scripts/lumina-init` before running, or open the `Lumina 自传` table in Lark after init and rewrite the rows directly.

What the persona table controls:
- `分类: 基础设定` — locked identity (Origin, Job, Pet, etc.)
- `分类: 观点` — her hot takes (movies, AI, etc.)
- `分类: 日常 / 近况 / 读到的` — fluid, can be added by the daily-read workflow

The "Mandarin level" entry encodes her use-Chinese rules. Keep the format if you change the values.

## Scripts reference

```
lumina-init       # bootstrap (one-time, idempotent)
lumina-context    # load all memory in 1 call (saves 70% tokens vs raw lark-cli list calls)
lumina-recast     # leave a canonical-format Recast comment on a Doc
lumina-sediment   # write back all session deltas (vocab, topics, log, diary, profile)
```

Each accepts `--help` and is < 350 lines of Python with stdlib only.

## Memory architecture — what's in each table

| Table | One row = | Notable fields |
|---|---|---|
| `学生档案 v2` | A student | `CEFR等级`, `学习目标`, `兴趣标签`, `累计学习天数` |
| `词汇本与错题集` | A correction OR a new word the user just learned (both go through Ebbinghaus) | `类型` (`error · ...` / `vocab · ...` / `collocation`), `复习次数`, `下次复习日期` (1/2/4/7/15/30/60 days) |
| `话题记忆` | A topic / person / event in the user's life | `主题`, `关键词`, `事实/上下文`, `Lumina 的视角` |
| `对话日记` | A session | `对话摘要`, `用户情绪`, `留下的悬念` |
| `Lumina 自传` | A fact about Lumina herself | `条目`, `分类`, `内容`, `可主动提起` (when to bring it up) |

`lumina-context` queries all 5, applies smart filtering (recent N for logs, today-due for vocab, keyword-match for topics), and emits a single ~1k-token Markdown briefing.

## Known sharp edges in `lark-cli` (already worked around in scripts)

If you write your own automation against the same APIs, watch for:

| Sharp edge | What goes wrong | Workaround |
|---|---|---|
| `base +table-create --fields '[...]'` is partial-write | First bad field stops the array; table is created with only the fields before it; you can't delete a single-table Base | Create empty table + `+field-create` per field |
| `base +record-upsert --json` does NOT take `{"fields": {...}}` wrapper | `validation_error` | Pass field map directly: `{"用户":"...","open_id":"..."}` |
| Field type discriminators are strings, not numeric codes | Numeric `type:1` is rejected | Use `"text"` / `"number"` / `"datetime"` / `"select"` |
| `im +messages-send` requires `--as bot` explicitly | User identity rejected | Always pass `--as bot` |
| `auth status: needs_refresh` | Looks scary | Calls still work; ignore unless 401 |

## Roadmap

Things this v1.0 doesn't do yet but the architecture supports:

- [ ] `lumina-morning` — scheduled daily assignment generator (cron-friendly)
- [ ] `lumina-daily-read` — automated background research → Lumina's persona grows over time
- [ ] Multi-user mode (one Base per student vs partitioned shared Base)
- [ ] Auto keyword extraction from user's last turn (currently the agent picks them)
- [ ] Lark Doc as conversation channel (instead of IM) — for users who prefer doc threads

PRs welcome.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

Built on [`lark-cli`](https://github.com/larksuite/cli) by ByteDance / Lark team. The Recast correction strategy comes from second-language acquisition pedagogy (vs. explicit error correction). Ebbinghaus intervals are the standard spaced-repetition curve. Lumina's persona is — to be transparent — invented; she's not a real Edinburgh tutor, just a stable character for the AI to embody.

If you build something interesting on top of this, [tell me about it](https://github.com/oil-oil/lark-lumina/issues).
