import asyncio
from Element import StateInfo, FlowEdge, LogicalEdge, EventEdge, TimerEdge, StateNode

# 상태 정보 초기화
state_info = StateInfo()


# 상태 노드 정의
class ExampleNode(StateNode):
    def __init__(self, name):
        super().__init__(name)
        self.visits = 0

    def action(self, state_info):
        self.visits += 1
        print(f"Visiting {self.state_name} (visit count: {self.visits})")


# 노드 생성
node_a = ExampleNode("Node A")
node_b = ExampleNode("Node B")
node_c = ExampleNode("Node C")

# 엣지 설정
node_a.logical_edges.append(LogicalEdge(node_a, node_b, lambda _: True, "A to B"))
node_b.event_edges.append(EventEdge(node_b, node_c, "GO_TO_C", "B to C on event"))
node_c.timer_edge = TimerEdge(node_c, node_a, 2, "C to A after 2 seconds")


async def run_state_machine():
    current_node = node_a
    for _ in range(10):  # 10번 반복
        print(f"\nCurrent node: {current_node.state_name}")

        if current_node == node_b:
            print("Triggering GO_TO_C event")
            state_info.event_queue.put("GO_TO_C")

        try:
            next_node = await asyncio.wait_for(current_node.process(state_info), timeout=5.0)
        except asyncio.TimeoutError:
            print(f"Timeout occurred in {current_node.state_name}. Moving to next node.")
            next_node = node_c if current_node == node_b else node_a

        current_node = next_node
        await asyncio.sleep(0.1)  # 상태 변화를 더 잘 관찰하기 위한 짧은 대기


# Element.py의 StateNode 클래스 수정 (이 부분은 Element.py 파일에서 수정해야 합니다)
"""
class StateNode:
    # ... (기존 코드)

    async def process(self, stateInfo: StateInfo) -> "StateNode":
        self.action(stateInfo)

        for edge in self.logical_edges:
            next_state = edge.forward(stateInfo)
            if next_state:
                return next_state

        event_tasks = [edge.forward(stateInfo) for edge in self.event_edges]
        if self.timer_edge:
            event_tasks.append(self.timer_edge.forward(stateInfo))

        if not event_tasks:
            return self

        done, pending = await asyncio.wait(event_tasks, return_when=asyncio.FIRST_COMPLETED)

        next_state = done.pop().result()
        for task in pending:
            task.cancel()

        return next_state
"""

# 상태 머신 실행
asyncio.run(run_state_machine())