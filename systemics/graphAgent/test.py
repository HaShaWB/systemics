import asyncio
from typing import Any
from graphAgent.agentGraph import StateNode, LogicalEdge, EventEdge  # your_module은 원래 코드가 있는 파일명으로 변경해주세요

class DebugStateNode(StateNode):
    def action(self, state_data: Any) -> None:
        print(f"Executing action in state: {self.state_name}")
        print(f"Current state data: {state_data}")

class IncrementLogicalEdge(LogicalEdge):
    def __init__(self, prev_state: StateNode, next_state: StateNode, threshold: int):
        super().__init__(prev_state, next_state, self.increment_condition, f"Increment until {threshold}")
        self.threshold = threshold

    def increment_condition(self, state_data: dict) -> bool:
        state_data['counter'] += 1
        print(f"Incremented counter to: {state_data['counter']}")
        return state_data['counter'] >= self.threshold

class DelayEventEdge(EventEdge):
    def __init__(self, prev_state: StateNode, next_state: StateNode, delay: float):
        super().__init__(prev_state, next_state, f"Delay for {delay} seconds")
        self.delay = delay

    async def forward(self, state_data: Any) -> StateNode:
        print(f"Waiting for {self.delay} seconds...")
        await asyncio.sleep(self.delay)
        print("Delay completed")
        return self.next_state

async def run_state_machine(start_state: StateNode, end_state: StateNode, initial_state_data: dict):
    current_state = start_state
    state_data = initial_state_data

    while current_state != end_state:
        print(f"\nCurrent state: {current_state.state_name}")
        current_state = await current_state.process(state_data)

    print(f"\nState machine completed. Final state: {current_state.state_name}")
    print(f"Final state data: {state_data}")

# 상태 노드 생성
start = DebugStateNode("Start", "Initial state")
middle = DebugStateNode("Middle", "Intermediate state")
end = DebugStateNode("End", "Final state")

# 엣지 생성 및 연결
logical_edge = IncrementLogicalEdge(start, middle, 5)
start.logical_edges.append(logical_edge)

event_edge = DelayEventEdge(middle, end, 3.0)
middle.event_edges.append(event_edge)

# 상태 기계 실행
initial_data = {'counter': 0}
asyncio.run(run_state_machine(start, end, initial_data))