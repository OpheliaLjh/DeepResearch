# DeepResearch (Python MVP)

This project implements a minimal version of **DeepResearch** using only the **OpenAI public API** and **Brave Search API**:
- ReAct planning → tool calls for web search/fetch.
- Iterative retrieval with Critic → final structured research report (with citations & TODOs).

## Configuration (Environment Variables)
* `OPENAI_API_KEY` — OpenAI key for Responses (Required)
* `BRAVE_API_KEY` — Brave Search API key (Required)
* `DR_MODEL` - Reasoning model to use (Optional) (e.g., gpt-4.1, gpt-4o-mini, or another you have). Default in code: gpt-5.

## Quickstart

1. Install dependencies:
```bash
cd deepresearch
pip install -r requirements.txt
```

2. Run it:
```bash
python3 -m main "<YOUR_RESEARCH_TOPIC>"
```

## Project Structure
```
├─ main.py
├─ agent.py
├─ schemas.py
├─ tool_executor.py
├─ logger.py
└─ tools/
   ├─ __init__.py
   ├─ registry.py
   ├─ web_search.py
```

## How it works

1. Planner (Structured)
* Uses OpenAI Responses API with strict JSON Schema for a search plan.
* Schema files live in schemas.py.


2. Tool Loop (ReAct)
* Call client.responses.create(..., tools=tools, tool_choice="auto").
* The model may emit assistant content items of type function_call.
* The code executes local Python tools (handle_tool_call) and then returns user content items of type function_call_output with the same call_id.

3. Tools supported (tools/)
* web_search.py
  * Brave Search: hardened params, header validation, optional proxy disable.

4. Critic (Structured)
* Structured evaluation of sufficiency + next queries. Stops early if sufficient.

5. Reporter (Structured)
* Generates final TL;DR, sections (with citations), and next TODOs.



## Limitations

### Core capability gaps

* Search-only: The agent can’t parse PDF, or build a local knowledge base. It synthesizes from search snippets, which limits depth and accuracy.

* No iterative crawl frontier: Without fetch/parse, it can’t follow outbound links, de-duplicate sources, or expand coverage systematically.

* No persistent vector RAG: The agent retains prior tool outputs in the conversation history and can reason over them in later iterations. However, without the FAISS store, there’s no semantic index for scalable retrieval of many documents, no cross-run persistence, and recall is bounded by the model’s context window and token budget.

### Reliability, scaling & ops

* No rate limiting/backoff policies: Beyond basic try/except; could hit provider quotas/throttling.

* No caching: Repeated queries re-hit search APIs; costs and latency are higher.

* No parallelism: Tool calls are serial; long topics take longer than needed.

* Proxy/network sensitivity: Corporate proxies can strip Brave headers; ChatGPT API can block.


## Examples
Input:
```bash
python3 -m main "The analysis of speculative decoding"
```
Final Report:
```
{
  "tldr": "Speculative decoding accelerates LLM generation by drafting multiple tokens then verifying them in one pass, achieving 2–3.6× throughput gains in mature systems without loss of quality in lossless modes. Best results in the last 12 months come from self-speculative methods (EAGLE family), RNN drafters (ReDrafter) and optimized engines (TensorRT‑LLM, vLLM), with speedups sensitive to acceptance rate, sampling temperature, batching/scheduler, and KV-cache constraints in long-context settings. Integration with grammar constraints, beam search, safety/jailbreak defense, and multilingual/multimodal tasks remains underexplored and needs standardized, cross‑engine, cross‑hardware benchmarks.",
  "sections": [
    {
      "title": "Definition and taxonomy",
      "bullets": [
        "Speculative decoding drafts multiple candidate tokens (chain or tree) using a fast mechanism, then verifies with the target model via rejection sampling to accept the longest matching prefix; lossless settings preserve the target distribution.",
        "Variants include auxiliary drafter (smaller LM), self-speculation (additional heads or feature-space drafting), and chain vs dynamic tree drafting. Related but distinct exact accelerators include lookahead/blockwise decoding that do not use a separate drafter."
      ],
      "citations": [
        {
          "url": "https://developer.nvidia.com/blog/an-introduction-to-speculative-decoding-for-reducing-latency-in-ai-inference/",
          "title": "An Introduction to Speculative Decoding for Reducing Latency in AI Inference",
          "published_at": "2025-09-",
          "snippet": "The draft-target approach pairs a target model with a lightweight draft mechanism proposing several next tokens; the target verifies and accepts the longest matching prefix."
        },
        {
          "url": "https://arxiv.org/abs/2403.09919",
          "title": "Recurrent Drafter for Fast Speculative Decoding in Large Language Models",
          "published_at": "2024-12-13",
          "snippet": "Introduces an RNN drafter and reports state-of-the-art speedups; discusses speculative streaming and engine integration."
        },
        {
          "url": "https://arxiv.org/abs/2406.16858",
          "title": "EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees",
          "published_at": "2024-06-30",
          "snippet": "Proposes dynamic draft trees for speculative decoding to improve acceptance and speed."
        },
        {
          "url": "https://arxiv.org/abs/2402.02057",
          "title": "Break the Sequential Dependency of LLM Inference Using Lookahead Decoding",
          "published_at": "2024-02-03",
          "snippet": "Presents an exact, parallel decoding algorithm without a separate drafter; related but distinct from speculation."
        },
        {
          "url": "https://arxiv.org/abs/2402.05109",
          "title": "Hydra: Sequentially-Dependent Draft Heads for Medusa Decoding",
          "published_at": "2024-10-07",
          "snippet": "Analyzes head structures and tree-style speculative decoding within Medusa-like frameworks."
        }
      ]
    },
    {
      "title": "Algorithms and theory: acceptance, expected speedup, quality",
      "bullets": [
        "Lossless speculative decoding with exact rejection sampling preserves the target distribution; expected speedup grows with acceptance rate and drafted length but is bounded by drafter/verify overheads.",
        "Acceptance and speedups degrade as sampling temperature rises; aligning drafter and target sampling improves efficiency.",
        "Serving-level goodput depends on continuous batching and scheduler interaction with acceptance variability, implying that theoretical token-level gains do not directly translate to end-to-end gains without system tuning."
      ],
      "citations": [
        {
          "url": "https://arxiv.org/abs/2302.01318",
          "title": "Accelerating Large Language Model Decoding with Speculative Sampling",
          "published_at": "2023-02-02",
          "snippet": "Original lossless speculative sampling with rejection sampling and expected speedup intuition."
        },
        {
          "url": "https://developer.nvidia.com/blog/an-introduction-to-speculative-decoding-for-reducing-latency-in-ai-inference/",
          "title": "An Introduction to Speculative Decoding for Reducing Latency in AI Inference",
          "published_at": "2025-09-",
          "snippet": "Explains acceptance and lossless property; system-level considerations for speedup."
        },
        {
          "url": "https://arxiv.org/abs/2410.10141",
          "title": "Temperature-Centric Investigation of Speculative Decoding with Knowledge Distillation",
          "published_at": "2024-10-14",
          "snippet": "Shows decoding efficiency degrades with higher temperature and improves with consistent drafter/target temperatures."
        },
        {
          "url": "https://arxiv.org/abs/2406.14066",
          "title": "Optimizing Speculative Decoding for Serving Large Language Models Using Goodput",
          "published_at": "2024-06-25",
          "snippet": "Proposes SmartSpec; highlights batching/scheduler effects and stabilizing acceptance for end-to-end gains."
        },
        {
          "url": "https://docs.vllm.ai/en/v0.9.0/features/spec_decode.html",
          "title": "Speculative Decoding - vLLM",
          "published_at": "2025-",
          "snippet": "Documents greedy sampling equality in vLLM’s speculative decoding as a lossless guarantee and system integration aspects."
        }
      ]
    },
    {
      "title": "Empirical performance and systems",
      "bullets": [
        "Mature, optimized engines report 2.8–3.6× throughput gains with speculation under favorable settings; earlier implementations sometimes showed limited benefit due to pipeline immaturity.",
        "Reported gains vary by hardware (A100 vs H100), drafter design (EAGLE/ReDrafter/aux LM), sampling temperature, batching strategy, and prompt mix affecting acceptance."
      ],
      "citations": [
        {
          "url": "https://blog.vllm.ai/2024/10/17/spec-decode.html",
          "title": "How Speculative Decoding Boosts vLLM Performance by up to 2.8x",
          "published_at": "2024-10-17",
          "snippet": "Shows up to 2.8× speedups in vLLM with optimized speculative decoding pipelines and configurations."
        },
        {
          "url": "https://developer.nvidia.com/blog/boost-llama-3-3-70b-inference-throughput-3x-with-nvidia-tensorrt-llm-speculative-decoding/",
          "title": "Boost Llama 3.3 70B Inference Throughput 3x with NVIDIA TensorRT-LLM Speculative Decoding",
          "published_at": "2024-12-19",
          "snippet": "Demonstrates ~3× throughput with TRT‑LLM speculative decoding on Llama 3.3 70B."
        },
        {
          "url": "https://developer.nvidia.com/blog/tensorrt-llm-speculative-decoding-boosts-inference-throughput-by-up-to-3-6x/",
          "title": "TensorRT-LLM Speculative Decoding Boosts Inference Throughput by up to 3.6x",
          "published_at": "2025-01-11",
          "snippet": "Reports up to 3.6× total token throughput gains with TRT‑LLM speculative decoding."
        },
        {
          "url": "https://docs.sglang.ai/advanced_features/speculative_decoding.html",
          "title": "Speculative Decoding — SGLang",
          "published_at": "2025-",
          "snippet": "Describes EAGLE‑based speculative decoding in SGLang with throughput improvements and configuration notes."
        }
      ]
    },
    {
      "title": "Implementations and deployment paths",
      "bullets": [
        "vLLM, TensorRT‑LLM, and SGLang all support speculative decoding with differing integration depth; TRT‑LLM integrates drafter, beam search, and acceptance inside the engine for minimal overhead; vLLM provides lossless checks and EAGLE integration; SGLang provides fast EAGLE‑2/3 paths.",
        "NVIDIA Triton tutorials exist for both vLLM and TRT‑LLM speculative serving, easing production deployment."
      ],
      "citations": [
        {
          "url": "https://docs.vllm.ai/en/v0.9.0/features/spec_decode.html",
          "title": "Speculative Decoding - vLLM",
          "published_at": "2025-",
          "snippet": "Feature documentation for speculative decoding with equality checks and usage."
        },
        {
          "url": "https://nvidia.github.io/TensorRT-LLM/advanced/speculative-decoding.html",
          "title": "Speculative Sampling — TensorRT‑LLM",
          "published_at": "2025-",
          "snippet": "TRT‑LLM implements ReDrafter such that logits prediction, beam search, and acceptance are inside the engine."
        },
        {
          "url": "https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/tutorials/Feature_Guide/Speculative_Decoding/TRT-LLM/README.html",
          "title": "Speculative Decoding with TensorRT‑LLM — NVIDIA Triton Inference Server",
          "published_at": "2025-",
          "snippet": "Tutorial to build and serve speculative decoding with TRT‑LLM backend."
        },
        {
          "url": "https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/tutorials/Feature_Guide/Speculative_Decoding/vLLM/README.html",
          "title": "Speculative Decoding with vLLM — NVIDIA Triton Inference Server",
          "published_at": "2025-",
          "snippet": "Tutorial to serve EAGLE and draft-model based speculation via vLLM in Triton."
        },
        {
          "url": "https://docs.sglang.ai/advanced_features/speculative_decoding.html",
          "title": "Speculative Decoding — SGLang",
          "published_at": "2025-",
          "snippet": "EAGLE‑based speculative decoding with tuning flags and performance notes."
        }
      ]
    },
    {
      "title": "Applicability limits and edge cases",
      "bullets": [
        "In long‑context, large‑batch regimes, KV‑cache bandwidth becomes the bottleneck; pairing speculation with KV‑efficient methods (e.g., quantized/sparse KV, attention sinks) is required to retain gains.",
        "Integration with grammar‑constrained/structured decoding is conceptually possible but under‑studied, especially for tree‑based speculation and per‑step masking/acceptance interactions.",
        "Speculative beam search is emerging but lacks standardized implementations and comparisons vs greedy/sampling speculation."
      ],
      "citations": [
        {
          "url": "https://arxiv.org/abs/2502.10424",
          "title": "QuantSpec: Self-Speculative Decoding with Hierarchical Quantized KV Cache",
          "published_at": "2025-02-05",
          "snippet": "Proposes self-spec with hierarchical KV quantization to relieve KV bottlenecks in long-context inference."
        },
        {
          "url": "https://arxiv.org/abs/2412.10319",
          "title": "SCBench: A KV Cache-Centric Analysis of Long-Context Methods",
          "published_at": "2025-03-11",
          "snippet": "Analyzes long-context methods with KV-centric perspective; underscores KV cache as a primary bottleneck."
        },
        {
          "url": "https://www.frontiersin.org/articles/10.3389/frai.2024.1406857/full",
          "title": "Grammar-constrained decoding for structured information extraction...",
          "published_at": "2024-12-12",
          "snippet": "Demonstrates grammar-constrained decoding in a real application; highlights structured output needs."
        },
        {
          "url": "https://arxiv.org/abs/2409.16560",
          "title": "Dynamic-Width Speculative Beam Decoding for Efficient LLM Inference",
          "published_at": "2025-03-14",
          "snippet": "Introduces speculative beam decoding with dynamic width; early-stage evaluation."
        }
      ]
    },
    {
      "title": "Training and coupling of draft mechanisms",
      "bullets": [
        "Self-speculative approaches (Medusa/EAGLE) require finetuning heads or target features and can yield higher acceptance per unit overhead; auxiliary drafters (small Transformer) or RNN drafters (ReDrafter) reduce coupling but need distillation to match target distribution.",
        "Alignment of sampling settings and distillation on in‑domain traffic improves acceptance and stability; evidence shows temperature consistency between drafter and target is important for efficiency."
      ],
      "citations": [
        {
          "url": "https://arxiv.org/abs/2401.10774",
          "title": "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads",
          "published_at": "2024-06-14",
          "snippet": "Presents self-spec heads, Medusa‑2 joint training recipe, and distillation guidance."
        },
        {
          "url": "https://arxiv.org/abs/2403.09919",
          "title": "Recurrent Drafter for Fast Speculative Decoding in Large Language Models",
          "published_at": "2024-12-13",
          "snippet": "RNN-based drafter achieving strong speedups; practical for on-device and integrated engines."
        },
        {
          "url": "https://arxiv.org/abs/2401.15077",
          "title": "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty",
          "published_at": "2025-03-04",
          "snippet": "Core EAGLE concept of feature-level drafting; complements EAGLE‑2 dynamic trees."
        },
        {
          "url": "https://arxiv.org/abs/2410.10141",
          "title": "Temperature-Centric Investigation of Speculative Decoding with Knowledge Distillation",
          "published_at": "2024-10-14",
          "snippet": "Shows efficiency degrades with higher T and improves with consistent temperatures and distillation."
        }
      ]
    },
    {
      "title": "Failure modes, robustness, and safety",
      "bullets": [
        "Acceptance rates are sensitive to distribution shift in prompts and domains, impacting throughput and jitter; serving-level strategies (goodput-aware scheduling, continuous batching) help stabilize performance.",
        "Safety-aware decoding can be stacked with speculation; preliminary work proposes speculative safety-aware decoding, but controlled evidence on speculation’s impact on jailbreak/refusal rates is limited."
      ],
      "citations": [
        {
          "url": "https://arxiv.org/abs/2406.14066",
          "title": "Optimizing Speculative Decoding for Serving Large Language Models Using Goodput",
          "published_at": "2024-06-25",
          "snippet": "Demonstrates scheduler/batching impacts and proposes SmartSpec for stable goodput."
        },
        {
          "url": "https://arxiv.org/abs/2402.08983",
          "title": "SafeDecoding: Defending against Jailbreak Attacks via Safety-Aware Decoding",
          "published_at": "2024-07-25",
          "snippet": "Introduces safety-aware decoding that adjusts token probabilities to mitigate jailbreaks."
        },
        {
          "url": "https://arxiv.org/abs/2508.17739",
          "title": "Speculative Safety-Aware Decoding",
          "published_at": "2025-08-25",
          "snippet": "Proposes integrating safety signals into speculative decoding; early-stage evidence."
        }
      ]
    },
    {
      "title": "Benchmarks and evaluation",
      "bullets": [
        "Spec-Bench (ACL Findings 2024) offers a baseline unified evaluation for speculative methods, but a 2025 refresh is needed to include EAGLE‑3/ReDrafter-in-TRT‑LLM and engines like SGLang/vLLM latest.",
        "Vendor and independent blogs show strong gains but differ in configs, prompting, and hardware; standardized, cross‑engine A/Bs are required."
      ],
      "citations": [
        {
          "url": "https://github.com/hemingkx/Spec-Bench",
          "title": "Spec-Bench: A Comprehensive Benchmark and Unified Evaluation Platform for Speculative Decoding",
          "published_at": "2024-",
          "snippet": "Benchmark suite for speculative decoding methods referenced by ACL Findings 2024 survey."
        },
        {
          "url": "https://blog.vllm.ai/2024/10/17/spec-decode.html",
          "title": "How Speculative Decoding Boosts vLLM Performance by up to 2.8x",
          "published_at": "2024-10-17",
          "snippet": "Demonstration of speedups in vLLM with detailed configs."
        },
        {
          "url": "https://developer.nvidia.com/blog/tensorrt-llm-speculative-decoding-boosts-inference-throughput-by-up-to-3-6x/",
          "title": "TensorRT-LLM Speculative Decoding Boosts Inference Throughput by up to 3.6x",
          "published_at": "2025-01-11",
          "snippet": "Shows highest reported throughput improvements and setup details."
        },
        {
          "url": "https://predibase.com/blog/llm-inference-benchmarks-predibase-fireworks-vllm",
          "title": "Real-World LLM Inference Benchmarks: How Predibase Built the Fastest Stack",
          "published_at": "2025-05-28",
          "snippet": "Independent benchmarking discussing latency/throughput under load and engine differences."
        }
      ]
    },
    {
      "title": "Best practices and decision guidelines",
      "bullets": [
        "Start lossless with engine-native support (TRT‑LLM or vLLM/SGLang) and verify greedy equality; log acceptance distributions by prompt category; then tune.",
        "Maximize acceptance per unit draft cost: align sampling (temperature/top‑p) across drafter and target; train self-spec heads or distill auxiliary drafters on in‑domain traffic; consider dynamic trees (EAGLE‑2/3) or RNN drafter (ReDrafter).",
        "Engineer the serving path: enable continuous batching; keep acceptance inside engine when possible (TRT‑LLM); measure end‑to‑end latency/throughput (goodput) rather than per-token timings.",
        "Long‑context: pair speculation with KV‑efficient approaches (quantized/sparse KV, attention sinks/self‑spec with KV compression) to avoid memory bottlenecks; otherwise gains shrink.",
        "Safety-critical deployments: combine speculation with safety-aware decoding and re‑evaluate refusal/jailbreak metrics under lossless and lossy settings."
      ],
      "citations": [
        {
          "url": "https://docs.vllm.ai/en/v0.9.0/features/spec_decode.html",
          "title": "Speculative Decoding - vLLM",
          "published_at": "2025-",
          "snippet": "Greedy Sampling Equality and usage guidance for lossless speculation."
        },
        {
          "url": "https://nvidia.github.io/TensorRT-LLM/advanced/speculative-decoding.html",
          "title": "Speculative Sampling — TensorRT‑LLM",
          "published_at": "2025-",
          "snippet": "Integration of ReDrafter/beam/acceptance within engine; configuration details."
        },
        {
          "url": "https://arxiv.org/abs/2410.10141",
          "title": "Temperature-Centric Investigation of Speculative Decoding with Knowledge Distillation",
          "published_at": "2024-10-14",
          "snippet": "Evidence for temperature alignment benefits and efficiency degradation at higher T."
        },
        {
          "url": "https://arxiv.org/abs/2406.16858",
          "title": "EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees",
          "published_at": "2024-06-30",
          "snippet": "Dynamic tree drafting improves acceptance; practical configurations."
        },
        {
          "url": "https://arxiv.org/abs/2502.10424",
          "title": "QuantSpec: Self-Speculative Decoding with Hierarchical Quantized KV Cache",
          "published_at": "2025-02-05",
          "snippet": "KV‑efficient self‑spec; recommendations for long‑context memory constraints."
        },
        {
          "url": "https://arxiv.org/abs/2402.08983",
          "title": "SafeDecoding: Defending against Jailbreak Attacks via Safety-Aware Decoding",
          "published_at": "2024-07-25",
          "snippet": "Stackable safety-aware decoding strategy applicable to speculative pipelines."
        }
      ]
    },
    {
      "title": "Conflicts and disagreements",
      "bullets": [
        "Speedup discrepancies: earlier vLLM warnings vs later 2.8×, and TRT‑LLM up to 3.6×; causes likely include engine maturity, hardware (A100 vs H100), drafter variant, batching/scheduler, and sampling temperature/prompt mix affecting acceptance.",
        "Long‑context benefits: strong claims when KV‑aware vs mixed outcomes otherwise; pairing speculation with KV compression/quantization appears necessary for robust gains across tasks and engines."
      ],
      "citations": [
        {
          "url": "https://docs.vllm.ai/en/v0.6.0/models/spec_decode.html",
          "title": "Speculative decoding in vLLM — older note",
          "published_at": "2024-",
          "snippet": "Early warning that speculative decoding was not yet optimized, with limited inter-token latency gains."
        },
        {
          "url": "https://blog.vllm.ai/2024/10/17/spec-decode.html",
          "title": "How Speculative Decoding Boosts vLLM Performance by up to 2.8x",
          "published_at": "2024-10-17",
          "snippet": "Later report of up to 2.8× speedups with optimized implementation."
        },
        {
          "url": "https://developer.nvidia.com/blog/tensorrt-llm-speculative-decoding-boosts-inference-throughput-by-up-to-3-6x/",
          "title": "TensorRT-LLM Speculative Decoding Boosts Inference Throughput by up to 3.6x",
          "published_at": "2025-01-11",
          "snippet": "Higher reported gains on recent NVIDIA hardware with integrated engine path."
        },
        {
          "url": "https://arxiv.org/abs/2502.10424",
          "title": "QuantSpec: Self-Speculative Decoding with Hierarchical Quantized KV Cache",
          "published_at": "2025-02-05",
          "snippet": "Supports the view that KV-aware designs are crucial in long-context."
        },
        {
          "url": "https://arxiv.org/abs/2412.10319",
          "title": "SCBench: A KV Cache-Centric Analysis of Long-Context Methods",
          "published_at": "2025-03-11",
          "snippet": "KV cache is a primary bottleneck for long-context inference, affecting speculation gains."
        }
      ]
    }
  ],
  "next_todos": [
    "Design a cross-engine, cross-hardware benchmark: vLLM (latest), TensorRT‑LLM, and SGLang on identical A100/H100/MI300 setups with identical prompts and sampling. Measure acceptance distributions, throughput, latency, and quality drift (lossless vs lossy).",
    "Evaluate long-context performance with KV strategies: baseline vs QuantSpec‑style KV quantization vs sparse KV; test draft methods (EAGLE‑2/3, ReDrafter, small LM) under 32k–128k contexts and large batches.",
    "Study sampling sensitivity: systematically vary temperature and top‑p for each drafter/engine, logging acceptance and end‑to‑end goodput; validate temperature-alignment recommendations.",
    "Investigate grammar/structured decoding with speculation: implement CFG/regex masks in both draft and verify, including tree‑based acceptance; report acceptance/throughput impact and correctness rates.",
    "Prototype speculative beam decoding: reproduce dynamic‑width speculative beam and compare to greedy/sampling speculation in lossless and lossy modes; quantify search quality vs speed.",
    "Assess safety/jailbreak: layer SafeDecoding atop speculation; measure refusal/jailbreak metrics and utility retention under lossless vs lossy acceptance on public red‑teaming suites.",
    "Run multilingual and multimodal tests: cross‑lingual acceptance rates (high/low-resource languages) and VLM setups; evaluate speed/quality tradeoffs per language/modality.",
    "Provide an updated Spec‑Bench 2025 fork adding EAGLE‑3/ReDrafter-in-TRT‑LLM, SGLang/vLLM latest, and standardized configs; release reproducible scripts and seeds.",
    "Model the cost of acceptance variability: integrate SmartSpec-style scheduling in open-source engines; study tail latencies and throughput stability under mixed prompt distributions.",
    "Build a practitioner guide: decision tree for when/what to deploy (aux drafter vs self-spec; tree vs chain), tuning knobs, and cost model templates for production planning."
  ]
}
```