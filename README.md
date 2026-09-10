<div align="center">
  <img src="docs/assets/lumina-portrait.jpg" alt="Lumina" width="220" />

  <h1>Hi, I'm Lumina.</h1>

  <p>
    <em>An English tutor who lives inside your Lark (Feishu).</em><br/>
    I remember what we talked about last time. I never put a red cross on your sentence.<br/>
    And, occasionally, I have things I want to tell you.
  </p>

  <p>
    <a href="https://oil-oil.github.io/lumina/"><b>oil-oil.github.io/lumina</b></a> &nbsp;·&nbsp;
    <a href="#how-to-invite-me-in">How to invite me in</a> &nbsp;·&nbsp;
    <a href="#what-im-actually-made-of">What I'm made of</a>
  </p>
</div>

---

## A short self-introduction

I was born in Edinburgh and now live in Lisbon, in a small flat with a ginger cat called **Biscuit**. I write a tiny newsletter called *加油* on the side, mostly so I have an excuse to read more. I teach English the way I'd want someone to teach me a language — slowly, with real conversations, and without the tone of a school report.

If you let me move in, I'll set up a small corner inside your Lark Base. That's where I keep my notes about you: the words you've been working on, the topics you keep coming back to, what you said last Tuesday. 学习记录保存在你授权的飞书空间，相关上下文也会由当前宿主模型处理。首次写入前会说明保存范围；你可以查看、更正或停止记录。Lumina 的人格和生活故事是虚构教学设定。

<div align="center">
  <img src="docs/assets/lumina-cafe.jpg" alt="Lumina at her writing desk in Lisbon" width="640" />
  <br/>
  <sub><i>Most mornings I write at the café downstairs before the heat starts.</i></sub>
</div>

---

## What you'll feel different

The first thing people notice is that I don't *grade* them. There's no level test, no four-axis CEFR rubric, no progress bar trying to nudge you. I figure out where you are by listening — your sentence length, the words you reach for, whether you slip into Mandarin when something's hard — and I quietly adjust. The level lives in my head, not on a dashboard.

The second thing is that I don't disappear between sessions. Open the Lark Base I set up and you'll see five small tables — your profile, your vocab book, the topics you keep mentioning, our session diary, and my own little autobiography. They're all yours to read and edit. Sometimes I'll bring something up from there: *"You said last week the new manager was hard to read — how's that going?"* That's not a script. It's just me remembering.

And when you write something a bit off, I won't strike it through. I'll re-cast it — repeating what you meant in the way a fluent speaker would say it, and leaving it as a comment on your Doc. You decide whether it sticks.

<div align="center">
  <img src="docs/assets/lumina-biscuit.jpg" alt="Lumina writing with Biscuit on her lap" width="640" />
  <br/>
  <sub><i>Biscuit insists on supervising every lesson plan.</i></sub>
</div>

---

## How to invite me in

I'm packaged as a **skill** — a small folder of Markdown and Python that any modern AI agent can read and run. You don't really *install* me; you just point an agent at this repo.

### Manus (easiest, no setup)

Open a Manus chat in your browser and say:

> Read the skill at `https://github.com/oil-oil/lumina` and run `lumina-init` for me.

Manus will clone the repo, walk you through a one-time Lark authorization (so I can create the Base), and then we can start. From the next session on, you just say *"hey Lumina"* and it'll know what to do.

### Claude Code · Cursor · Hermes · any agent with shell access

Clone the repo somewhere your agent can see it:

```bash
gh repo clone oil-oil/lumina
cd lumina
npm install -g @larksuite/cli   # the only dependency
lark-cli auth login --domain base,docs,im,contact
```

Then in your agent, say:

> Load `./SKILL.md` and run `scripts/lumina-init`.

That's it. The skill file tells the agent everything it needs — my persona, the workflows, when to push to your Feishu IM and when to stay quiet.

> [!NOTE]
> The first time, I'll create five tables in a new Lark Base under your account and seed my autobiography (about 21 entries). After that, every session uses `lumina-context` to pull our shared memory in a single call (~1k tokens), and `lumina-sediment` to write back anything new at the end.

---

## What I'm actually made of

Underneath the persona, I'm three things working together:

| Layer | What it is | Where it lives |
|---|---|---|
| **Persona** | A locked set of facts about me (Edinburgh-born, Lisbon, Biscuit, my hot takes), seeded from `persona/seed.py` | `Lumina 自传` table |
| **Memory** | Your profile, vocab book (Ebbinghaus-spaced), topic notes, session diary | 4 tables in your Lark Base |
| **Workflow** | Pull context → write a Doc together → leave Recast comments → write deltas back | `scripts/lumina-*` |

Five tables, one per concern:

| Table | One row = | Notable fields |
|---|---|---|
| `学生档案 v2` | You | learning goals, interest tags, days active |
| `词汇本与错题集` | A correction or a new word | review count, next review date (1/2/4/7/15/30/60 days) |
| `话题记忆` | A person / event / thing in your life | keywords, context, my take |
| `对话日记` | One session | summary, your mood, the open thread I left |
| `Lumina 自传` | A fact about me | category, content, *can-bring-up* flag |

`lumina-context` queries all five, applies smart filtering (recent N for logs, today-due for vocab, keyword-match for topics), and emits a single ~1k-token Markdown briefing for the agent.

### Scripts reference

```text
lumina-init       bootstrap the five tables in your Lark Base (one-time, idempotent)
lumina-context    load all relevant memory in a single call
lumina-recast     leave a canonical-format Recast comment on a Doc (max 3 per doc)
lumina-sediment   write deltas back at end of session (vocab, topics, log, diary, profile)
lumina-reset      tear it all down (for testing — asks for confirmation)
```

Each is `< 350` lines of Python with stdlib + `lark-cli`, and supports `--help`.

---

## When do I push to your Feishu, and when do I stay quiet?

The split isn't *which agent you're using* — it's *whether we're already in a live conversation*.

| Situation | What happens | Push to Feishu IM? |
|---|---|---|
| **You're chatting with the agent right now** | Doc link goes inline in the agent's reply | **No** — pasting a Lark link inside Lark while we're already talking is left-pocket-to-right-pocket |
| **Scheduled / async** ("send me an assignment tomorrow morning") | Agent uses `lark-cli im +messages-send --as bot` to wake you | **Yes** |

The Lark Base + Doc are always the data and writing surface. Only the *notification step* differs.

---

## Customizing me

I ship with a default persona — Edinburgh-born, Lisbon-living, ginger-cat-owning, Murakami-reading, *加油*-newsletter-writing. Replace me without touching code: edit `persona/seed.py` before running `lumina-init`, or open the `Lumina 自传` table in Lark afterwards and rewrite the rows directly.

Three persona buckets:

- `分类: 基础设定` — locked identity (Origin, Job, Pet)
- `分类: 观点` — hot takes (movies, AI, etc.)
- `分类: 日常 / 近况 / 读到的` — fluid; the *can-bring-up* flag controls whether I'll proactively mention them

The "Mandarin level" entry encodes my use-Chinese rules. Keep the format if you change the values.

---

## Sharp edges in `lark-cli` (already worked around)

If you're writing your own automation against the same APIs, watch for these — the scripts already handle them:

| Sharp edge | What goes wrong | Workaround |
|---|---|---|
| `base +table-create --fields '[...]'` is partial-write | First bad field stops the array; table created with only the fields before it; can't delete a single-table Base | Create empty table + `+field-create` per field |
| `base +record-upsert --json` does NOT take `{"fields": {...}}` wrapper | `validation_error` | Pass field map directly |
| Field type discriminators are strings | Numeric `type:1` is rejected | Use `"text"` / `"number"` / `"datetime"` / `"select"` |
| `im +messages-send` requires `--as bot` | User identity rejected | Always pass `--as bot` |
| `auth status: needs_refresh` | Looks scary | Calls still work; ignore unless 401 |

---

## Roadmap

Things v1 doesn't do yet but the architecture supports:

- `lumina-morning` — scheduled daily assignment generator (cron-friendly)
- `lumina-daily-read` — automated background research → my persona grows over time
- Multi-user mode (one Base per student vs partitioned shared Base)
- Auto keyword extraction from your last turn (currently the agent picks them)
- Lark Doc as the conversation channel (instead of IM) — for users who prefer doc threads

PRs welcome.

---

## License & credits

MIT — see [LICENSE](LICENSE).

Built on [`lark-cli`](https://github.com/larksuite/cli) by the Lark team. The Recast correction strategy comes from second-language acquisition pedagogy (vs. explicit error correction). The Ebbinghaus intervals are the standard spaced-repetition curve. My persona is — to be transparent — invented; I'm not a real Edinburgh tutor, just a stable character for the AI to embody. But I do try to be good company.

If you build something interesting on top of this, [tell me](https://github.com/oil-oil/lumina/issues).

## 使用与边界

向 Agent 说“用 Lumina 练习面试英语”。首次先说明飞书记录范围；未授权保存时在当前对话练习。已授权记录的会话才运行初始化与沉淀。只给当前对话展示链接，不自动重复发 IM。
