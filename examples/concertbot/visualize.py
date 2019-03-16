import asyncio

from rasa_core.agent import Agent
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy

if __name__ == '__main__':
    agent = Agent("domain.yml",
                  policies=[MemoizationPolicy(), KerasPolicy()])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        agent.visualize("data/stories.md",
                        output_file="graph.html", max_history=2))
