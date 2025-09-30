import sys, json
from agent import deep_research

def main():
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "System prompt leakage prevention in LLM benchmarks"
    result = deep_research(topic, max_iters=5)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
