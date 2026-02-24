---
name: code-homework-grader
id: OC-0191
version: 1.0.0
description: "Run student code against unit tests and provide constructive feedback on style and logic."
env:
  - GITHUB_TOKEN
commands:
  - grade
  - feedback
---

# Code Homework Grader

Run student code against unit tests and provide constructive feedback on style and logic.

## Prerequisites
- A valid `GITHUB_TOKEN` environment variable to access assignments if using a platform like GitHub Classroom.

## Commands
| Command    | Description                              |
|------------|------------------------------------------|
| `grade`    | Run the unit tests against student code  |
| `feedback` | Provide constructive feedback on code style and logic |

## Usage
```bash
export GITHUB_TOKEN="ghp_..."
python3 scripts/code_homework_grader.py grade --submission student_submission.zip --tests test_suite.py
python3 scripts/code_homework_grader.py feedback --submission student_submission.zip
```
