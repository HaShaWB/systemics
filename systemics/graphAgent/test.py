import asyncio
from graphAgent.stateInfo import StateInfo, AgentEvent
from graphAgent.stateNode import StateNode
from graphAgent.flowEdge import (
    SimpleLogicalEdge,
    BranchLogicalEdge,
    SimpleTimerEdge,
    BranchTimerEdge,
    SimpleEventEdge,
    BranchEventEdge,
)

async def test_simple_logical_edge():
    print("\nTesting SimpleLogicalEdge")
    state_info = StateInfo()
    start_state = StateNode("Start", "Start State")
    end_state = StateNode("End", "End State")
    
    edge = SimpleLogicalEdge(start_state, end_state, lambda x: True)
    result = edge.forward(state_info)
    print(f"SimpleLogicalEdge result: {result.state_name}")

async def test_branch_logical_edge():
    print("\nTesting BranchLogicalEdge")
    state_info = StateInfo()
    start_state = StateNode("Start", "Start State")
    state_a = StateNode("A", "State A")
    state_b = StateNode("B", "State B")
    
    def decision_func(info):
        return state_a if len(info.flow_event_list) == 0 else state_b
    
    edge = BranchLogicalEdge(start_state, [state_a, state_b], decision_func)
    result = edge.forward(state_info)
    print(f"BranchLogicalEdge result (empty event list): {result.state_name}")
    
    state_info.flow_event_list.append(AgentEvent("test", None))
    result = edge.forward(state_info)
    print(f"BranchLogicalEdge result (non-empty event list): {result.state_name}")

async def test_simple_timer_edge():
    print("\nTesting SimpleTimerEdge")
    state_info = StateInfo()
    start_state = StateNode("Start", "Start State")
    end_state = StateNode("End", "End State")
    
    edge = SimpleTimerEdge(start_state, end_state, lambda x: True, 2)
    result = await edge.forward(state_info)
    print(f"SimpleTimerEdge result: {result.state_name}")

async def test_branch_timer_edge():
    print("\nTesting BranchTimerEdge")
    state_info = StateInfo()
    start_state = StateNode("Start", "Start State")
    state_a = StateNode("A", "State A")
    state_b = StateNode("B", "State B")
    
    def decision_func(info):
        return state_a if len(info.flow_event_list) == 0 else state_b
    
    edge = BranchTimerEdge(start_state, [state_a, state_b], decision_func, 2)
    result = await edge.forward(state_info)
    print(f"BranchTimerEdge result (empty event list): {result.state_name}")
    
    state_info.flow_event_list.append(AgentEvent("test", None))
    result = await edge.forward(state_info)
    print(f"BranchTimerEdge result (non-empty event list): {result.state_name}")

async def test_simple_event_edge():
    print("\nTesting SimpleEventEdge")
    state_info = StateInfo()
    start_state = StateNode("Start", "Start State")
    end_state = StateNode("End", "End State")
    
    edge = SimpleEventEdge(start_state, end_state, "test_event")
    result = edge.forward(state_info)
    print(f"SimpleEventEdge result (no event): {result}")
    
    state_info.flow_event_list.append(AgentEvent("test_event", None))
    result = edge.forward(state_info)
    print(f"SimpleEventEdge result (with event): {result.state_name}")

async def test_branch_event_edge():
    print("\nTesting BranchEventEdge")
    state_info = StateInfo()
    start_state = StateNode("Start", "Start State")
    state_a = StateNode("A", "State A")
    state_b = StateNode("B", "State B")
    
    def decision_func(info, event_data):
        return state_a if event_data is None else state_b
    
    edge = BranchEventEdge(start_state, [state_a, state_b], decision_func, "test_event")
    result = edge.forward(state_info)
    print(f"BranchEventEdge result (no event): {result}")
    
    state_info.flow_event_list.append(AgentEvent("test_event", None))
    result = edge.forward(state_info)
    print(f"BranchEventEdge result (event with no data): {result.state_name}")
    
    state_info.flow_event_list.append(AgentEvent("test_event", "data"))
    result = edge.forward(state_info)
    print(f"BranchEventEdge result (event with data): {result.state_name}")

async def test_state_node():
    print("\nTesting StateNode")
    state_info = StateInfo()
    start_state = StateNode("Start", "Start State", state_info)
    end_state = StateNode("End", "End State", state_info)
    
    logical_edge = SimpleLogicalEdge(start_state, end_state, lambda x: True)
    start_state.set_logical_edges([logical_edge])
    
    result = await start_state.process()
    print(f"StateNode process result: {result.state_name}")

async def main():
    await test_simple_logical_edge()
    await test_branch_logical_edge()
    await test_simple_timer_edge()
    await test_branch_timer_edge()
    await test_simple_event_edge()
    await test_branch_event_edge()
    await test_state_node()

if __name__ == "__main__":
    asyncio.run(main())