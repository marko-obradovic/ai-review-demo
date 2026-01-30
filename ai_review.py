import os
import requests
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PR_NUMBER = os.environ["PR_NUMBER"]
REPO = os.environ["REPO"]
GH_TOKEN = os.environ["GH_TOKEN"]

with open("diff.txt", "r") as f:
    diff = f.read()

# Safety valve: don’t review massive diffs
MAX_DIFF_CHARS = 12000
if len(diff) > MAX_DIFF_CHARS:
    diff = diff[:MAX_DIFF_CHARS] + "\n\n[Diff truncated]"

prompt = f"""
You are a senior software engineer performing a pull request review.

Review the diff below and focus ONLY on:
- Bugs or logical errors
- Security concerns
- Performance issues
- Readability and maintainability
- Violations of common engineering best practices

Rules:
- Be concise
- Avoid nitpicks
- Do NOT comment on formatting unless it impacts readability
- If something looks good, say so
- If there are no major issues, explicitly say "No major issues found"

Diff:
{diff}
"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": prompt}],
)

review = response.choices[0].message.content

# Post comment to PR
url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
headers = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json",
}

requests.post(
    url,
    headers=headers,
    json={"body": f"🤖 **AI Code Review**\n\n{review}"},
)
