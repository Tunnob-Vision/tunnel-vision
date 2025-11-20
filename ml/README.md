# Poker Decision Module Plan

## 1. System Architecture & Data Flow

1. **Vision Layer (`cv/src/card_detector.py`)**
   - Detects individual card ranks/suits using YOLOv8 (`models/best.pt`).
   - Outputs: annotated frame + raw detections (`[{class, confidence}]`).

2. **Card Interpreter (new)**
   - Converts detections into `utils.models.Card` objects and attaches confidence.
   - Handles dedupes, conflict resolution, and fallbacks when suits/ranks missing.
   - Output: `Hand`, optional partial `Community`, detection metadata.

3. **Game State Collector (new Streamlit form)**
   - Extends confirmation page to capture stacks, pot, blinds, positions, and recent actions.
   - Builds `utils.models.PokerGameState` + contextual info (opponent tendencies, profile selection).

4. **Decision Engine (`ml/src/decision_engine.py`)**
   - Consumes `PokerGameState` + context.
   - Calls analytics submodules:
     - **Equity**: Monte Carlo simulator or deterministic odds library for street-specific equity.
     - **Range**: Bayesian updater maintaining villain combo weights.
     - **Policy Model**: Learned model (GBM / RL) returning action logits and EVs.
     - **Strategy Adapter**: Adjusts logits per profile (Tight/Aggressive/Balanced).
   - Output: structured recommendation `{action, confidence, bet_size(optional), rationale}`.

5. **UI Layer (`views/…`)**
   - Displays recommendation, rationale, and lets user flip strategy profile.
   - Provides logging hook to append anonymized `(state, model_action, user_action)` for retraining.

## 2. Decision Algorithm Research Summary

| Approach | Use Case | Pros | Cons |
| --- | --- | --- | --- |
| Monte Carlo Equity | Rapid EV estimates for hand vs. sampled range | Simple, interpretable | Needs range assumptions; slower for many sims |
| Range vs. Range Sims | Multiway/postflop accuracy | Captures blockers/board texture | Requires robust range modeling |
| Simplified CFR / GTO tables | Baseline optimality | Low exploitability, deterministic | Hard to customize, computationally heavy to derive |
| Supervised Gradient Boosting | Fast inference on structured features | Easy to train, interpretable | Limited sequential reasoning |
| Deep RL (DQN/PPO) | Learn adaptive policies | Handles sequential/hidden info | Needs large training data & tuning |
| Hybrid Rule+Model | Safety net with ML exploration | Lower blunders, adjustable | Requires careful blending |

Recommendation: iterate from (1) Monte Carlo equity + heuristic policy, (2) supervised model on solver/hand-history data, (3) RL fine-tuning or CFR-informed policy.

## 3. Data Collection & Preparation

1. **Sources**
   - Public HH repositories (PokerStars, GG, 2+2 forums). Respect ToS/licensing.
   - Simulated hands via `pypokerengine`, `OpenSpiel`, or custom Monte Carlo self-play.
   - Synthetic solver output: run turn/river solvers (SimplePostflop/PIO export) over canonical spots.

2. **Schema**
   - `hand_id`, stakes, hero position, board cards, hero hand, opponent count.
   - Stack sizes (hero + villains), bet history (size, street, actor), pot size per street.
   - Opponent model snapshot (VPIP, PFR, aggression).
   - Target labels: solver action probs or EVs.

3. **Processing Steps**
   - Normalize to big blind units, encode missing board cards with mask bits.
   - Compute derived stats: SPR, pot odds, implied odds, effective stack.
   - Split by street, ensure temporal ordering; optionally augment via suit/rank permutations.
   - Store as Parquet; index by street for stratified sampling.

4. **Label Quality**
   - Cross-check actions with solver EV; set confidence score.
   - Mark noisy hands (multiway >4 players, unknown stacks) for exclusion or lower weight.

## 4. Feature Engineering Plan

- **Cards**: binary matrix (52 dims) + embeddings; made-hand class, draw potential, blockers.
- **Equity Metrics**: hero absolute equity, equity vs. top-% range, equity realization estimate.
- **Pot/Stack Metrics**: pot odds, implied odds, SPR, bet-to-pot ratios, effective stack, commitment threshold.
- **Positions & Players**: one-hot position, num players left, button distance, blind indicators.
- **Opponent Tendencies**: rolling aggression factor, c-bet %, fold-to-3bet, range entropy.
- **Action History**: sequence encoding (street, size bucket, polarity) processed by transformer/GRU.
- **Board Texture**: flush/straight draw counts, pairing, high-card concentration, suitedness bins.

## 5. Model Training Roadmap

1. **Baseline GBM**
   - Inputs: engineered tabular features.
   - Outputs: action class (fold/call/raise) + size bucket.
   - Loss: focal loss or weighted cross-entropy using solver probs.

2. **Neural Policy Net**
   - Architecture: shared MLP/transformer, dual heads (action logits, EV scalar).
   - Training: KL-divergence to solver distribution + MSE on EV.
   - Calibration: temperature scaling, reliability diagrams.

3. **Reinforcement Learning**
   - Environment: extend OpenSpiel Texas Hold’em to support multi sizing options.
   - Warm-start weights from supervised model, then run PPO/DQN self-play.
   - Reward: hand EV adjusted for rake, penalty for deviating from profile.

4. **Evaluation**
   - Accuracy vs. solver actions, expected value gap, average regret.
   - Street/position-specific dashboards, confusion matrices, cumulative EV in simulated matches.

5. **MLOps**
   - Version datasets + models, log metrics via Weights & Biases.
   - Export ONNX for lightweight inference, keep PyTorch for research.

## 6. Action Confidence & Strategy Profiles

- Compute softmax probabilities from policy head; report top action prob as confidence.
- Attach EV delta vs. second-best action for clearer rationale.
- Profiles:
  - **Tight**: add prior favoring folds/calls; lower raise probability unless EV margin > threshold.
  - **Balanced**: raw policy output.
  - **Aggressive**: temperature < 1 on raise logits or EV boost; enforce min bluff frequency.
- Provide slider/tabs in UI to pick profile; log selection for analytics.

## 7. Integration Steps

1. Build card-mapping utility (`cv` → `utils.models.Card`).
2. Extend confirmation UI to capture stacks/pot/profile; create `GameStateForm` helper.
3. Implement `ml/src/decision_engine.py` API returning `DecisionResult` with action/confidence/rationale.
4. Wire decision call after hand confirmation; store result in `st.session_state` for display.
5. Add analytics pane showing equity, villain range snapshot, chosen profile.
6. Create background job or manual trigger to export logged hands for retraining.
7. Document configuration (`config/decision.yaml`) for swapping models/checkpoints.

## 8. Next Actions

1. Scaffold `decision_engine` module (policy stub + Monte Carlo equity placeholder).
2. Implement card interpreter + UI for stacks/pot/profile selection.
3. Create dataset specification + example notebook for data ingestion.
4. Prototype baseline GBM using synthetic data; validate inference latency.
5. Add logging pipeline for real-user hands.
