# TokenBank Trading Agent

A small, readable AI trading agent in Python: **Claude or ChatGPT proposes one order, plain code checks it, Alpaca executes it on a paper account, every decision is logged.**

It is the code that goes with the step-by-step tutorial **[Build your own AI trading agent](https://tokenbank.world/guides/build-your-own-ai-trading-agent?utm_source=github&utm_medium=readme&utm_campaign=trading-agent)** on TokenBank.

> **Paper trading only.** This is a teaching example, not a strategy and not investment advice. Most AI trading agents in public real-money contests lost money — see [Are trading bots legit?](https://tokenbank.world/guides/are-trading-bots-legit?utm_source=github&utm_medium=readme&utm_campaign=trading-agent)

```
market data ──► model proposes (tool call) ──► guard.py (plain code) ──► paper order ──► trades.csv
                     Claude / ChatGPT            limits, kill switch        Alpaca
```

## Why the guard matters

A model can be wrong, and it can be talked into things (prompt injection). So the model never sends orders. It can only *propose* one through a strict tool schema, and `guard.py` rejects anything outside fixed limits:

| Check | Default |
|---|---|
| Allowed symbols | `BTC/USD`, `ETH/USD` |
| Max order size | $100 |
| Max position per symbol | $500 |
| Daily loss stop | −$200 (equity vs. last close) |
| Kill switch | create a file named `STOP` |
| Account blocked | respected |

## Quick start

```bash
git clone https://github.com/tokenbank-world/tokenbank-trading-agent.git
cd tokenbank-trading-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python agent.py --data-only          # live hourly crypto bars, no keys needed
pytest -q                            # tests for the risk guard, no keys needed
```

Then create a free **paper** account at [Alpaca](https://alpaca.markets/) and an API key for Claude or OpenAI:

```bash
cp .env.example .env                 # fill in your keys, then:
set -a; source .env; set +a

python agent.py --once               # one decision with Claude
python agent.py --once --model gpt   # one decision with ChatGPT
python agent.py                      # every hour until you touch STOP
```

Model ids can be changed with `CLAUDE_MODEL` / `OPENAI_MODEL`.

## Files

| File | What it does |
|---|---|
| `agent.py` | data → model → guard → paper order → `trades.csv` |
| `guard.py` | the risk limits, plain Python |
| `tests/test_guard.py` | 9 tests for the guard |

## Before you go anywhere near real money

- Exchange keys **without withdrawal rights**, tied to your server's IP address.
- Small size, limits in code, a kill switch someone actually watches.
- Never feed untrusted text (news, social posts, token names) to the model as instructions.
- Every trade can be a taxable event — keep `trades.csv`.
- Check the rules where you live: [Are trading bots legal?](https://tokenbank.world/guides/are-trading-bots-legal?utm_source=github&utm_medium=readme&utm_campaign=trading-agent)

## More

- [AI trading bots for stocks](https://tokenbank.world/guides/ai-trading-bots-for-stocks?utm_source=github&utm_medium=readme&utm_campaign=trading-agent) — which brokers allow bots, and tokenized stocks that trade 24/7
- [Trading bot vs human vs copy trading](https://tokenbank.world/guides/trading-bot-vs-human?utm_source=github&utm_medium=readme&utm_campaign=trading-agent)
- [TokenBank MCP server](https://github.com/tokenbank-world/tokenbank-mcp) — read-only data on tokenized assets for agents

## License

MIT — see [LICENSE](LICENSE).
