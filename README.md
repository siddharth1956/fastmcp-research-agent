# FastMCP × PydanticAI Research Agent

## 🧠 How to Run
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -U pip
   pip install -r requirements.txt
python -m student.run --topic "US semiconductor export controls (2024–2025) overview" --out artifacts

🚀 How to Run This Project

Follow these steps to set up and run the FastMCP × PydanticAI Research Agent locally:

1️⃣ Clone this repository
git clone https://github.com/siddharth1956/fastmcp-research-agent.git
cd fastmcp-research-agent

2️⃣ Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# or on Windows:
venv\Scripts\activate

3️⃣ Install dependencies
pip install -U pip
pip install -r requirements.txt

4️⃣ Create your .env file
Copy the example file and update it with your own OpenAI API key:
cp .env.example .env

Open .env and fill in the values:
OPENAI_API_KEY=sk-yourkeyhere
OPENAI_MODEL=openai:gpt-4o-mini
MCP_HTTP_URL=http://127.0.0.1:8765
ASSIGNMENT_MODE=dev

⚠️ Do not commit .env to GitHub.
It contains your private API key.

5️⃣ Run the research agent
python -m student.run --topic "US semiconductor export controls (2024–2025) overview" --out artifacts

This command:
	•	Connects to the MCP server.
	•	Runs the PydanticAI agent.
	•	Produces a research brief and logs in the artifacts/ folder.

⸻

6️⃣ Check generated outputs
ls -la artifacts
cat artifacts/brief.md
cat artifacts/report.json
sqlite3 notes.sqlite "SELECT COUNT(*) FROM notes;"
You should see:
	•	brief.md — 5–8 paragraph synthesis with citations [1], [2]
	•	report.json — includes "pii_flagged": false
	•	search_results.json, selected_urls.json, snippets.json
	•	notes.sqlite — persistent memory database

⸻

7️⃣ Optional (for graders)

If you’re grading or running in a sandboxed environment (no API key):
export ASSIGNMENT_MODE=grading
python -m student.run --topic "Any test topic" --out artifacts
The project will run with stubbed MCP responses — no internet or API key required.

⸻

✅ Folder Structure
fastmcp-research-agent/
├─ student/
│  ├─ agent.py
│  ├─ run.py
│  ├─ mcp_client.py
│  └─ __init__.py
├─ artifacts/
│  └─ .gitkeep
├─ .env.example
├─ .gitignore
├─ README.md
└─ requirements.txt
