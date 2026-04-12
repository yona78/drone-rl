# Cost Analysis (section 11 — Dr. Segal Guidelines)

## Token & API Cost Breakdown

This application is a **100% local desktop application**. It performs no external API calls, no cloud inference, and no network requests at runtime.

| Resource | Provider | Cost per Unit | Units Used | Total Cost |
|----------|----------|---------------|------------|------------|
| Q-Learning computation | Local CPU | $0.00 | All episodes | $0.00 |
| LLM tokens (inference) | None | N/A | 0 | $0.00 |
| Cloud storage | None | N/A | 0 | $0.00 |
| External API calls | None | N/A | 0 | $0.00 |
| **Total runtime cost** | | | | **$0.00** |

## Architectural Justification

The decision to use tabular Q-Learning (dictionary-based Q-table) rather than deep reinforcement learning (neural networks) means all computation is simple arithmetic performed on the local CPU. This eliminates any need for GPU resources, cloud APIs, or token-based pricing.

The `ApiGatekeeper` class (required by section 5) is implemented as an internal GUI event throttle rather than an external API rate limiter, because there are no external APIs to throttle.

## Development Costs

Development tooling costs (IDE, Git hosting, etc.) are outside the scope of this analysis.
