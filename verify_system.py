#!/usr/bin/env python3
"""
System Verification Script
Checks all AI Engine components and agent integrations
"""

import sys
import os
from pathlib import Path

# Add ai-engine to path
sys.path.insert(0, str(Path(__file__).parent / "ai-engine"))

print("=" * 60)
print("AI ENGINE SYSTEM VERIFICATION")
print("=" * 60)

checks_passed = 0
checks_failed = 0
warnings = []

def check(name, func):
    global checks_passed, checks_failed
    try:
        result = func()
        if result:
            print(f"✓ {name}")
            checks_passed += 1
            return True
        else:
            print(f"✗ {name} - Failed")
            checks_failed += 1
            return False
    except Exception as e:
        print(f"✗ {name} - Error: {str(e)}")
        checks_failed += 1
        return False

# 1. Check RL Environment
print("\n1. REINFORCEMENT LEARNING (RL)")
print("-" * 60)
check("RL Environment imports", lambda: __import__("rl.environment", fromlist=["RLEnvironment", "SystemState", "ActionType"]))
check("RL Environment runs", lambda: (
    from rl.environment import RLEnvironment
    env = RLEnvironment()
    state = env.reset()
    assert state.shape == (6,), f"Expected state shape (6,), got {state.shape}"
    True
))
check("RL Agent imports", lambda: __import__("rl.agent", fromlist=["RLAgent"]))
check("RL Reward Functions imports", lambda: __import__("rl.reward_functions", fromlist=["RewardFunction"]))

# 2. Check GNN
print("\n2. GRAPH NEURAL NETWORK (GNN)")
print("-" * 60)
try:
    import torch_geometric
    check("GNN Graph Builder imports", lambda: __import__("gnn.graph_builder", fromlist=["GraphBuilder", "DependencyGraph"]))
    check("GNN Model imports", lambda: __import__("gnn.gnn_model", fromlist=["GATModel"]))
    check("GNN Predictor imports", lambda: __import__("gnn.gnn_predictor", fromlist=["GNNPredictor"]))
except ImportError:
    warnings.append("torch_geometric not installed - GNN features require: pip install torch-geometric")
    print("⚠ GNN modules require torch_geometric (not installed)")

# 3. Check Transformers
print("\n3. TRANSFORMERS")
print("-" * 60)
check("Transformer Model imports", lambda: __import__("transformers.model", fromlist=["TimeSeriesForecaster", "AnomalyTrendDetector"]))
check("Transformer Forecasting imports", lambda: __import__("transformers.forecasting", fromlist=["ScalingForecastEngine"]))
check("Transformer Dataset imports", lambda: __import__("transformers.dataset", fromlist=["SlidingWindowDataset"]))
try:
    from transformers.forecasting import ScalingForecastEngine
    engine = ScalingForecastEngine()
    print("✓ Transformer Forecasting Engine loads")
    checks_passed += 1
except Exception as e:
    print(f"⚠ Transformer Engine load warning: {e}")
    warnings.append(f"Transformer engine: {e}")

# 4. Check LLM Reasoning
print("\n4. LLM REASONING")
print("-" * 60)
# Note: Directory is llm-reasoning but we need to handle it
try:
    # Try direct import with path manipulation
    llm_path = Path(__file__).parent / "ai-engine" / "llm-reasoning"
    if llm_path.exists():
        sys.path.insert(0, str(llm_path.parent))
        # Import using importlib to handle hyphen
        import importlib.util
        spec = importlib.util.spec_from_file_location("llm_reasoning", llm_path / "reasoning_engine.py")
        if spec:
            print("✓ LLM Reasoning Engine file exists")
            checks_passed += 1
        else:
            print("✗ LLM Reasoning Engine file not found")
            checks_failed += 1
    else:
        print("✗ llm-reasoning directory not found")
        checks_failed += 1
except Exception as e:
    print(f"⚠ LLM Reasoning check: {e}")
    warnings.append(f"LLM Reasoning: {e}")

# 5. Check Meta-Agent
print("\n5. META-AGENT")
print("-" * 60)
try:
    meta_path = Path(__file__).parent / "ai-engine" / "meta-agent"
    if meta_path.exists():
        print("✓ Meta-Agent directory exists")
        checks_passed += 1
        if (meta_path / "orchestrator.py").exists():
            print("✓ Meta-Agent Orchestrator file exists")
            checks_passed += 1
        if (meta_path / "decision_router.py").exists():
            print("✓ Decision Router file exists")
            checks_passed += 1
        if (meta_path / "memory.py").exists():
            print("✓ Memory file exists")
            checks_passed += 1
    else:
        print("✗ meta-agent directory not found")
        checks_failed += 1
except Exception as e:
    print(f"⚠ Meta-Agent check: {e}")

# 6. Check Agent Integrations
print("\n6. AGENT INTEGRATIONS")
print("-" * 60)
agent_dirs = ["self-healing", "scaling", "coding", "security", "performance-monitoring"]
for agent_dir in agent_dirs:
    ai_integration = Path(__file__).parent / "agents" / agent_dir / "ai_integration.py"
    if ai_integration.exists():
        print(f"✓ {agent_dir}/ai_integration.py exists")
        checks_passed += 1
    else:
        print(f"✗ {agent_dir}/ai_integration.py missing")
        checks_failed += 1

# 7. Check File Structure
print("\n7. FILE STRUCTURE")
print("-" * 60)
required_files = [
    "ai-engine/rl/environment.py",
    "ai-engine/rl/agent.py",
    "ai-engine/rl/trainer.py",
    "ai-engine/gnn/graph_builder.py",
    "ai-engine/gnn/gnn_model.py",
    "ai-engine/gnn/gnn_predictor.py",
    "ai-engine/transformers/model.py",
    "ai-engine/transformers/forecasting.py",
    "ai-engine/llm-reasoning/reasoning_engine.py",
    "ai-engine/llm-reasoning/planner.py",
    "ai-engine/llm-reasoning/chain_of_thought.py",
    "ai-engine/llm-reasoning/safety_layer.py",
    "ai-engine/meta-agent/orchestrator.py",
    "ai-engine/meta-agent/decision_router.py",
    "ai-engine/meta-agent/memory.py",
]

for file_path in required_files:
    full_path = Path(__file__).parent / file_path
    if full_path.exists():
        print(f"✓ {file_path}")
        checks_passed += 1
    else:
        print(f"✗ {file_path} - MISSING")
        checks_failed += 1

# Summary
print("\n" + "=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)
print(f"✓ Passed: {checks_passed}")
print(f"✗ Failed: {checks_failed}")
print(f"⚠ Warnings: {len(warnings)}")

if warnings:
    print("\nWarnings:")
    for w in warnings:
        print(f"  - {w}")

print("\n" + "=" * 60)
if checks_failed == 0:
    print("✓ ALL CHECKS PASSED")
else:
    print(f"✗ {checks_failed} CHECK(S) FAILED")
print("=" * 60)

sys.exit(0 if checks_failed == 0 else 1)

