# agent.py
# -----------------------------------------------------------------------------
# DeepResearch MVP — Agent loop (ReAct-style) using the OpenAI Responses API.
#
# Key ideas:
# - We use STRICT JSON Schema structured outputs for Planner, Critic, Reporter.
# - During the ReAct loop, the model may emit function calls.
# -----------------------------------------------------------------------------

import json, os
from typing import List, Dict, Any
from openai import OpenAI
from tools.registry import tools
from tool_executor import handle_tool_call
from schemas import planner_schema, critic_schema, report_schema
from logger import logger

# System prompt to nudge planning discipline and citation policy.
SYSTEM_PROMPT = (
    "You are a rigorous research assistant. Use ReAct: plan first, then call tools, "
    "then reflect on evidence sufficiency.\n"
    "Rules:\n"
    "1) Every conclusion must cite >=2 independent sources, preferring the last 12 months.\n"
    "2) Prioritize surveys, reviews, or standards; then papers, official sources; then grey literature.\n"
    "3) Each round propose next search queries (keywords, sites, time range).\n"
    "4) If conflicting evidence appears, explicitly list disagreements and possible reasons.\n"
    "\n"
    "Available tool: web_search(query, top_k, recency_days). Do NOT invent or call any other tools. "
    "Use the returned titles/snippets/urls as evidence, and include citations in the report."
)


# Temperature tradeoff:
# - Higher = more creative but less stable and slower to converge.
TEMPERATURE = 1

def responses_structured(client: OpenAI, model: str, messages: List[Dict[str, str]], schema: Dict[str, Any]):
    """
    Call the Responses API asking for STRICT JSON Schema output.

    schema shape (from schemas.py):
      {
        "name": "<SchemaName>",
        "schema": { ... a valid JSON Schema ... }  # must have additionalProperties: false on every object,
                                                   # and required must list every key in properties (strict mode)
      }

    Responses API requirement for strict JSON Schema:
      text.format = {
        "type": "json_schema",
        "name": "<SchemaName>",
        "schema": { ...JSON Schema... },
        "strict": true
      }
    """
    return client.responses.create(
        model=model,
        input=messages,
        text={
            "format": {
                "type": "json_schema",
                "name": schema["name"],
                "schema": schema["schema"],
                "strict": True
            }
        },
        temperature=TEMPERATURE,
    )

def deep_research(topic: str, max_iters: int = 6, model: str = None):
    """
    Main ReAct loop:
      1) Planner (structured): produce an initial plan.
      2) Iteratively let the model call tools; we execute, then feed outputs back.
      3) Critic (structured): check sufficiency; possibly stop early.
      4) Reporter (structured): produce final JSON report.

    Args:
      topic: Research topic or question.
      max_iters: Max tool-plan iterations before reporting.
      model: Override model via param or via DR_MODEL env var.

    Returns:
      Dict (parsed JSON report) or {"raw": "..."} if parsing failed.
    """
    client = OpenAI()
    model = model or os.environ.get("DR_MODEL", "gpt-5")
    
    logger.info(f"Starting research on: {topic}")
    memory: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # ---- (1) Planner: ask the model for a structured first search plan ----
    logger.info("Generating initial search plan...")
    plan = responses_structured(
        client, model,
        memory + [{"role": "user", "content": f"Research topic: {topic}\nGive me the first search plan (Structured)."}],
        planner_schema
    )
    logger.debug(f"Plan raw output: {plan.output_text}")
    memory.append({"role": "assistant", "content": plan.output_text})

    # ---- (2) ReAct loop: tool calls + critique each round ----
    for i in range(max_iters):
        logger.info(f"--- Iteration {i+1}/{max_iters} ---")
        res = client.responses.create(
            model=model,
            input=memory,
            tools=tools,
            tool_choice="auto",
            temperature=TEMPERATURE
        )
        logger.debug(f"Response raw: {res.output}")
        tool_messages = []
        for item in (res.output or []):
            if item.type == "function_call":
                name = item.name
                logger.info(f"Tool call requested: {name}")
                args = json.loads(item.arguments or "{}")
                logger.debug(f"Tool args: {args}")
                result = handle_tool_call(name, args)
                logger.debug(f"Tool result: {result}")
                tool_messages.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result, ensure_ascii=False)
                })

        memory.extend([output.to_dict() for output in res.output])
        if tool_messages:
            memory.extend(tool_messages)
        else:
            logger.info("No tool calls this round.")

        # Critic
        logger.info("Critiquing evidence sufficiency...")


         # ---- (3) Critic (structured) ----
        critique = responses_structured(
            client, model,
            memory + [{"role": "user", "content": "Evaluate evidence sufficiency and propose next search."}],
            critic_schema
        )
        logger.debug(f"Critic raw: {critique.output_text}")
        memory.append({"role": "assistant", "content": critique.output_text})
        try:
            j = json.loads(critique.output_text)
            if j.get("sufficient") is True:
                logger.info("Critic judged evidence sufficient. Stopping early.")
                break
        except Exception as e:
            logger.warning(f"Critic output parse failed: {e}")
            pass

    # ---- (4) Reporter (structured) ----
    logger.info("Producing final report...")
    report = responses_structured(
        client, model,
        memory + [{"role": "user", "content": "Produce the final research report with citations and TODOs."}],
        report_schema
    )
    logger.debug(f"Report raw: {report.output_text}")

    # Return the final structured JSON (or raw text if parsing fails).
    try:
        return json.loads(report.output_text)
    except Exception:
        return {"raw": report.output_text}
