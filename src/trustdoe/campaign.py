from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .domain import CampaignState, Observation, ProcessSpace
from .process import SyntheticAMOracle
from .doe import latin_hypercube
from .controller import CandidateDecision, select_next_experiment, adapt_trust_region

@dataclass
class CampaignStep:
    iteration: int
    decision: CandidateDecision
    observation: Observation
    trust_radius_after: float

@dataclass
class CampaignResult:
    state: CampaignState
    steps: list[CampaignStep]


def initialize_campaign(oracle: SyntheticAMOracle, n_initial: int = 14, seed: int = 41) -> CampaignState:
    state = CampaignState(trust_radius=0.72)
    for x in latin_hypercube(oracle.space, n_initial, seed=seed):
        state.append(oracle.evaluate(x))
    if not state.safe_observations():
        center = 0.5*(oracle.space.lows + oracle.space.highs)
        state.append(oracle.evaluate(center))
    return state


def candidate_pool(space: ProcessSpace, n: int, seed: int) -> np.ndarray:
    return latin_hypercube(space, n, seed=seed)


def run_closed_loop(oracle: SyntheticAMOracle, budget: int = 10, seed: int = 101) -> CampaignResult:
    state = initialize_campaign(oracle, n_initial=14, seed=seed)
    steps: list[CampaignStep] = []
    for k in range(budget):
        pool = candidate_pool(oracle.space, 1800, seed+100+k)
        previous_best = state.incumbent().objective
        decision = None
        for beta in (1.64, 1.28, 0.84):
            try:
                decision = select_next_experiment(state, oracle.space, pool, beta=beta)
                break
            except RuntimeError:
                state.trust_radius = min(1.25, state.trust_radius*1.18)
        if decision is None:
            # Dense local rescue search around the verified safe incumbent. This remains
            # shadow-only and still must pass the surrogate safety lower-bound gate.
            rng = np.random.default_rng(seed + 9000 + k)
            center = oracle.space.normalize(state.incumbent().recipe)
            local_z = np.clip(center + rng.normal(0.0, max(0.06, state.trust_radius/4), size=(5000, oracle.space.dimension)), -1, 1)
            local_pool = np.array([oracle.space.denormalize(z) for z in local_z])
            state.trust_radius = min(1.25, max(state.trust_radius, 0.35))
            decision = select_next_experiment(state, oracle.space, local_pool, beta=0.50)
        obs = oracle.evaluate(np.array(decision.recipe))
        state.append(obs)
        adapt_trust_region(state, previous_best, decision, obs.objective, obs.safe)
        steps.append(CampaignStep(state.iteration, decision, obs, state.trust_radius))
    return CampaignResult(state, steps)
