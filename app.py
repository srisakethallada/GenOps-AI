from unicodedata import category

from flask import Flask, render_template, request
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import os
import re

load_dotenv()

app = Flask(__name__)
history = []

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

@app.route('/')
def home():
    return render_template(
        'index.html',
        root_cause="",
        solution="",
        prevention=""
    )

@app.route('/analyze', methods=['POST'])
def analyze():

    category = request.form['category']
    error = request.form['error_message']

    prompt = f"""
You are a senior DevOps Engineer with expertise in AWS, Linux, Docker, Terraform, Jenkins, Kubernetes, CI/CD and Cloud Infrastructure.

Category: {category}

Error:
{error}

Analyze the error professionally.

Provide the response EXACTLY in the following format:

ROOT CAUSE:
Provide a concise explanation of why the error occurred.

SOLUTION:
Provide numbered step-by-step instructions to fix the issue.

PREVENTION:
Provide best practices, monitoring recommendations, and preventive measures to avoid this issue in production.

Keep the response practical, production-ready, and easy for DevOps engineers to follow.
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.3-70b-versatile"
    )

    result = chat_completion.choices[0].message.content

    root_cause = ""
    solution = ""
    prevention = ""

    root_match = re.search(
        r"ROOT CAUSE:(.*?)(?=SOLUTION:|$)",
        result,
        re.DOTALL | re.IGNORECASE
    )

    solution_match = re.search(
        r"SOLUTION:(.*?)(?=PREVENTION:|$)",
        result,
        re.DOTALL | re.IGNORECASE
    )

    prevention_match = re.search(
        r"PREVENTION:(.*)",
        result,
        re.DOTALL | re.IGNORECASE
    )

    if root_match:
        root_cause = root_match.group(1).strip()

    if solution_match:
        solution = solution_match.group(1).strip()

    if prevention_match:
        prevention = prevention_match.group(1).strip()

    return render_template(
        'index.html',
        root_cause=root_cause,
        solution=solution,
        prevention=prevention,
        history=history
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)