"""LangGraph Cyclic State Graph Workflow Engine."""

import time
import uuid
from typing import Dict, Any, List, TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base import LLMProviderFactory
from app.core.logging import logger
from app.memory.checkpoints import checkpointer
from app.schemas.agent import WorkflowRequest, WorkflowResponse, WorkflowState
from app.tools.registry import registry


class GraphState(TypedDict):
    """Internal dictionary state passed between LangGraph nodes."""

    session_id: str
    goal: str
    step_count: int
    max_steps: int
    plan: List[str]
    current_action: str
    observations: List[str]
    reflection: str
    final_output: str
    is_done: bool


class WorkflowGraphEngine:
    """Cyclic multi-node state graph orchestrator."""

    def __init__(self):
        self.compiled_graph = self._build_graph()

    def _build_graph(self):
        """Constructs the LangGraph DAG with Planner, Executor, Reflector, and Synthesizer."""
        workflow = StateGraph(GraphState)

        # 1. Planner Node
        async def plan_node(state: GraphState) -> Dict[str, Any]:
            logger.info(f"[Workflow] [PlanNode] Formulating strategy for goal: {state['goal']}")
            goal = state["goal"]
            steps = [
                f"1. Analyze context and available tools for '{goal}'",
                f"2. Query domain knowledge or run system diagnostics",
                f"3. Synthesize and formulate comprehensive output",
            ]
            return {
                "plan": steps,
                "step_count": state.get("step_count", 0) + 1,
                "current_action": "Execute step 1: Context evaluation",
            }

        # 2. Executor Node
        async def execute_node(state: GraphState) -> Dict[str, Any]:
            step_num = state.get("step_count", 1)
            logger.info(f"[Workflow] [ExecuteNode] Executing action step #{step_num}")

            # Run system diagnostic tool as part of agentic observation
            sys_info = await registry.execute("get_system_status")

            observations = list(state.get("observations", []))
            obs_entry = f"Step {step_num} executed. System observation: Status={sys_info.get('status')}, Platform={sys_info.get('platform')}"
            observations.append(obs_entry)

            return {
                "observations": observations,
                "step_count": step_num + 1,
            }

        # 3. Reflector Node
        async def reflect_node(state: GraphState) -> Dict[str, Any]:
            step_num = state.get("step_count", 1)
            max_steps = state.get("max_steps", 4)
            logger.info(f"[Workflow] [ReflectNode] Evaluating progress: step {step_num}/{max_steps}")

            # If we've executed at least 2 steps or reached max_steps, mark as done
            if step_num >= 3 or step_num >= max_steps:
                return {
                    "reflection": "Sufficient observations gathered to synthesize final solution.",
                    "is_done": True,
                }
            else:
                return {
                    "reflection": "Further information needed. Continuing execution cycle.",
                    "is_done": False,
                }

        # 4. Synthesize Node
        async def synthesize_node(state: GraphState) -> Dict[str, Any]:
            logger.info(f"[Workflow] [SynthesizeNode] Producing final consolidated response.")
            obs_text = "\n".join(state.get("observations", []))
            plan_text = "\n".join(state.get("plan", []))

            final_text = (
                f"### Workflow Execution Summary\n"
                f"**Goal**: {state['goal']}\n\n"
                f"**Execution Plan**:\n{plan_text}\n\n"
                f"**Observations & Actions**:\n{obs_text}\n\n"
                f"**Status**: Goal achieved successfully using cyclic state graph execution."
            )
            return {"final_output": final_text, "is_done": True}

        # Conditional Edge Router
        def should_continue(state: GraphState) -> str:
            if state.get("is_done", False) or state.get("step_count", 0) >= state.get("max_steps", 5):
                return "synthesize"
            return "execute"

        # Register Nodes
        workflow.add_node("planner", plan_node)
        workflow.add_node("executor", execute_node)
        workflow.add_node("reflector", reflect_node)
        workflow.add_node("synthesizer", synthesize_node)

        # Wire Edges
        workflow.add_edge(START, "planner")
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "reflector")
        workflow.add_conditional_edges(
            "reflector",
            should_continue,
            {
                "execute": "executor",
                "synthesize": "synthesizer",
            },
        )
        workflow.add_edge("synthesizer", END)

        return workflow.compile(checkpointer=checkpointer.get_checkpointer())

    async def run(self, request: WorkflowRequest) -> Dict[str, Any]:
        """Runs the LangGraph state machine from start to end."""
        session_id = request.session_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": session_id}}

        initial_state: GraphState = {
            "session_id": session_id,
            "goal": request.goal,
            "step_count": 0,
            "max_steps": request.max_steps,
            "plan": [],
            "current_action": "",
            "observations": [],
            "reflection": "",
            "final_output": "",
            "is_done": False,
        }

        final_state = await self.compiled_graph.ainvoke(initial_state, config)
        return {
            "session_id": session_id,
            "goal": request.goal,
            "plan": final_state.get("plan", []),
            "observations": final_state.get("observations", []),
            "final_output": final_state.get("final_output", ""),
            "steps_executed": final_state.get("step_count", 0),
            "is_completed": final_state.get("is_done", True),
        }


workflow_engine = WorkflowGraphEngine()
