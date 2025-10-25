import argparse, json
from .agent import run_agent

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--topic", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    res = run_agent(a.topic, a.out)
    print(json.dumps(res))

if __name__ == "__main__":
    main()
