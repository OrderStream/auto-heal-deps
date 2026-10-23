# auto-heal-deps 🩹⚡

[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-v1.0.0-orange?logo=githubactions)](https://github.com/OrderStream/auto-heal-deps)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-Passing-brightgreen.svg)]()
[![OrderStream Polar](https://img.shields.io/badge/Polar-OrderStream-blue.svg)](https://polar.sh/orderstream)
[![Stellar XLM/USDC](https://img.shields.io/badge/Stellar-USDC%2FXLM-black.svg)](#direct-web3-wallet-monetization)
[![Base USDC](https://img.shields.io/badge/Base-USDC-0052FF.svg)](#direct-web3-wallet-monetization)

Automated dependency upgrade assistant that rewrites deprecated API calls to match new major versions and fixes lockfile peer conflicts.

---

## 💥 The Friction & Dollar Cost
Upgrading major libraries (Pydantic v1 ➔ v2, SQLAlchemy 1.4 ➔ 2.0, React 18 ➔ 19) is a multi-week engineering slog:
- Hundreds of deprecated methods (`.dict()` ➔ `.model_dump()`, `.parse_obj()` ➔ `.model_validate()`, `@validator` ➔ `@field_validator`) break tests across hundreds of files.
- Lockfile peer dependency collisions force teams to use `--force` or `--legacy-peer-deps`, leading to runtime `TypeError: undefined is not a function` in production.

**auto-heal-deps** provides zero-effort migration:
1. Codemods deprecated syntax to modern equivalents with unified diff preview.
2. Applies in-place rewrites across your entire repository with one command.
3. Diagnoses and resolves npm peer conflicts without hacky override flags.

---

## 🚀 Quick Start

### Installation
```bash
pip install auto-heal-deps
```

### CLI Usage
```bash
# Preview deprecated API usage across repository
auto-heal-deps scan --path ./src

# Dry-run migration diff
auto-heal-deps fix --path ./src --dry-run

# Automatically rewrite code in-place
auto-heal-deps fix --path ./src

# Check and resolve package.json peer conflicts
auto-heal-deps resolve-peers --file package.json

# Check license & zero-fee wallet payment details
auto-heal-deps license
```

---

## 🤖 GitHub Action Integration

```yaml
- name: Auto-Heal Dependencies
  uses: OrderStream/auto-heal-deps@v1
  with:
    path: "."
    apply: false
```

---

---

## 💳 Enterprise Pricing Matrix & Licensing

| Tier | Price | Repositories | Core Capabilities |
| :--- | :--- | :--- | :--- |
| **Community Free** | **** | Unlimited | Standalone CLI runner and single-repo GitHub Action |
| **Starter Suite** | ** / mo** | Up to 10 Repos | Automated CI PR gates, 500 CI runs/mo, standard email support |
| **Team Platform** | **,499 / mo** | Up to 50 Repos | Full 10-tool OrderStream suite, flaky test quarantine deterministic replay, zero-downtime shadow DB migration guard, 24/7 telemetry alarms |
| **Enterprise Platform** | **,999 / mo** | Unlimited | Multi-repo speculative merge engine, zero-downtime migration orchestrator, WASM sandbox gate, dedicated 24/7 cloud keeper, custom SLA |
| **M&A IP & Security Audit** | **,000 one-time** | Whole Organization | Comprehensive copyleft AST fuzzy fingerprint audit, snippet license sheriff certification, formal invariant verification, and executive forensic IP Cleanliness Certificate |

## 💰 Direct Web3 Wallet Monetization & Polar Integration

Support this project or license custom enterprise migration rules with **0 platform fees**:

- **Polar Subscription & Sponsorship:** [https://polar.sh/orderstream](https://polar.sh/orderstream)
- **Stellar Network (Native XLM / USDC):**
  - Public Key: `GABFQIK63R2NETJM7T673EAMZN4RJLLGP3OFUEJU5ZVTGWUKULZJNL6`
  - Memo (Required): `400566831`
- **EVM (Base / Arbitrum / Ethereum USDT & USDC):**
  - Address: `0x5de2b62434754bfd39ef350a3a867ed3eced5074`
