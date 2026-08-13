"""
generator.py — Experiment task manager for the String Interpolation Study.

Commands
--------
(default)       Generate generated_experiment.html and print a task summary.
--summary-only  Print the task summary table; skip HTML generation.
--template      Print a blank task entry (JSON) to stdout; copy it into
                questions.json to add a new task.
--validate      Validate every task in questions.json against the schema and
                pseudo-syntax rules; report errors without generating HTML.
--output PATH   Write generated HTML to PATH instead of the default location.

Adding a new task
-----------------
1. Run:  python generator.py --template
2. Fill in the printed JSON skeleton and append it to the "tasks" array in
   questions.json.  Required fields and allowed values are described in the
   template output and in TASK_DESIGN.md.
3. Run:  python generator.py --validate
   Fix any errors reported before continuing.
4. Run:  python generator.py
   This regenerates generated_experiment.html with the new task included.
5. If the new task will be used in the live Flask experiment, manually add the
   corresponding <div> block to templates/experiment.html following the pattern
   of the existing task blocks.

Pseudo-syntax evaluation rules are documented in TASK_DESIGN.md.
"""

import json
import sys
import argparse
from pathlib import Path
from html import escape

QUESTIONS_PATH = Path(__file__).parent / "questions.json"
DEFAULT_OUTPUT = Path(__file__).parent / "generated_experiment.html"

VALID_TYPES = {"Concatenation", "Interpolation"}
VALID_COMPLEXITY = {"L-1", "L-2", "L-3", "L-4"}

BLANK_TASK_TEMPLATE = {
    "id": "<int: next sequential ID>",
    "type": "<'Concatenation' or 'Interpolation'>",
    "complexity": "<'L-1' | 'L-2' | 'L-3' | 'L-4'>",
    "domain": "<short description of the real-world context, e.g. 'URL construction'>",
    "variables": {
        "<var_name>": "<quoted value, e.g. '\"hello\"' or '42'>"
    },
    "expression": "<the string expression participants will read>",
    "options": [
        "<option 1 — the output string>",
        "<option 2>",
        "<option 3>",
        "<option 4>"
    ],
    "correct_option": "<int 1–4: which option is correct>",
    "correct_output": "<the exact correct output string>",
    "distractor_types": [
        "<describe the comprehension error each wrong option targets>"
    ],
    "notes": "<optional: design rationale or clarification; omit field if not needed>"
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_questions(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(data: dict) -> list[str]:
    """Return a list of error strings; empty list means all tasks are valid."""
    errors = []
    tasks = data.get("tasks", [])
    seen_ids = set()

    for i, task in enumerate(tasks):
        prefix = f"Task at index {i} (id={task.get('id', '?')})"

        tid = task.get("id")
        if not isinstance(tid, int):
            errors.append(f"{prefix}: 'id' must be an integer.")
        elif tid in seen_ids:
            errors.append(f"{prefix}: duplicate id {tid}.")
        else:
            seen_ids.add(tid)

        if task.get("type") not in VALID_TYPES:
            errors.append(f"{prefix}: 'type' must be one of {sorted(VALID_TYPES)}.")

        if task.get("complexity") not in VALID_COMPLEXITY:
            errors.append(f"{prefix}: 'complexity' must be one of {sorted(VALID_COMPLEXITY)}.")

        if not isinstance(task.get("domain"), str) or not task["domain"].strip():
            errors.append(f"{prefix}: 'domain' must be a non-empty string.")

        if not isinstance(task.get("variables"), dict):
            errors.append(f"{prefix}: 'variables' must be a dict (use {{}} if none).")

        if not isinstance(task.get("expression"), str) or not task["expression"].strip():
            errors.append(f"{prefix}: 'expression' must be a non-empty string.")

        options = task.get("options")
        if not isinstance(options, list) or len(options) != 4:
            errors.append(f"{prefix}: 'options' must be a list of exactly 4 strings.")
        elif not all(isinstance(o, str) for o in options):
            errors.append(f"{prefix}: every entry in 'options' must be a string.")

        correct = task.get("correct_option")
        if correct not in (1, 2, 3, 4):
            errors.append(f"{prefix}: 'correct_option' must be an integer 1–4.")

        if not isinstance(task.get("correct_output"), str) or not task["correct_output"].strip():
            errors.append(f"{prefix}: 'correct_output' must be a non-empty string.")

    return errors


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def render_variables(variables: dict) -> str:
    if not variables:
        return ""
    return "\n".join(f"{k} = {v}" for k, v in variables.items())


def render_task_html(task: dict, total: int) -> str:
    tid = task["id"]
    task_type = task["type"]
    complexity = task["complexity"]
    expression = task["expression"]
    options = task["options"]
    correct = task["correct_option"]
    correct_output = task["correct_output"]
    variables = task.get("variables", {})
    notes = task.get("notes", "")

    symbol = "+" if task_type == "Concatenation" else "{ }"
    symbol_desc = "concatenation" if task_type == "Concatenation" else "interpolation"

    var_block = render_variables(variables)
    code_content = (var_block + "\n\n" + expression).strip() if var_block else expression

    options_html = ""
    for i, opt in enumerate(options, start=1):
        marker = " ✓" if i == correct else ""
        css = ' class="correct-answer"' if i == correct else ""
        options_html += f'      <li{css}>{i}. {escape(opt)}{marker}</li>\n'

    notes_html = (
        f'\n    <div class="task-notes"><strong>Design note:</strong> {escape(notes)}</div>'
        if notes else ""
    )

    return f"""
  <section class="task" id="task-{tid}">
    <h2>Task {tid} of {total} &mdash; {task_type} &mdash; Complexity: {complexity}</h2>
    <p class="instruction">
      The <code>"{escape(symbol)}"</code> symbol represents {symbol_desc}.
      Select the correct output.
    </p>
    <pre><code>{escape(code_content)}</code></pre>
    <ol class="options">
{options_html.rstrip()}
    </ol>
    <p class="correct-label">Correct answer: option {correct} &rarr; <code>{escape(correct_output)}</code></p>{notes_html}
  </section>
"""


def render_html(data: dict) -> str:
    meta = data["meta"]
    tasks = data["tasks"]
    total = len(tasks)

    task_sections = "".join(render_task_html(t, total) for t in tasks)

    complexity_rows = "".join(
        f"      <tr><td><strong>{lvl}</strong></td><td>{escape(desc)}</td></tr>\n"
        for lvl, desc in meta["complexity_levels"].items()
    )
    notes_items = "".join(
        f"      <li>{escape(n)}</li>\n" for n in meta.get("notes", [])
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Experiment Tasks — {escape(meta['study'])}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
    h1 {{ font-size: 1.4rem; border-bottom: 2px solid #333; padding-bottom: .4rem; }}
    h2 {{ font-size: 1.1rem; background: #f0f0f0; padding: .5rem .75rem; border-left: 4px solid #555; margin-top: 2rem; }}
    .instruction {{ color: #444; margin-bottom: .5rem; }}
    pre {{ background: #fafafa; border: 1px solid #ddd; padding: .75rem 1rem; border-radius: 4px; overflow-x: auto; }}
    code {{ font-family: "Courier New", monospace; font-size: .92rem; }}
    ol.options {{ list-style: none; padding: 0; margin: .5rem 0; }}
    ol.options li {{ padding: .2rem .5rem; font-family: monospace; font-size: .9rem; }}
    li.correct-answer {{ background: #e6f4ea; font-weight: bold; }}
    .correct-label {{ font-size: .88rem; color: #2a6b2a; margin-top: .4rem; }}
    .task-notes {{ font-size: .85rem; color: #555; background: #fffbe6; border: 1px solid #e0d080; padding: .5rem .75rem; margin-top: .75rem; border-radius: 3px; }}
    table {{ border-collapse: collapse; margin: .75rem 0; }}
    th, td {{ border: 1px solid #ccc; padding: .4rem .75rem; font-size: .88rem; }}
    th {{ background: #f0f0f0; }}
    .meta-block {{ background: #f7f7f7; border: 1px solid #ddd; padding: .75rem 1rem; font-size: .88rem; margin-bottom: 1.5rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>{escape(meta['study'])}</h1>
  <div class="meta-block">
    <p>{escape(meta['description'])}</p>
    <p>For pseudo-syntax evaluation rules, see <code>TASK_DESIGN.md</code>.</p>
    <h3 style="margin-top:.75rem;font-size:.95rem;">Complexity Levels</h3>
    <table>
      <tr><th>Level</th><th>Definition</th></tr>
{complexity_rows.rstrip()}
    </table>
    <h3 style="margin-top:.75rem;font-size:.95rem;">Notes</h3>
    <ul>
{notes_items.rstrip()}
    </ul>
  </div>
{task_sections}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def print_summary(data: dict) -> None:
    tasks = data["tasks"]
    print(f"{'ID':>3}  {'Type':<15}  {'Complexity':<10}  {'Correct':>7}  Domain")
    print("-" * 80)
    for t in tasks:
        print(
            f"{t['id']:>3}  {t['type']:<15}  {t['complexity']:<10}  "
            f"{t['correct_option']:>7}  {t['domain']}"
        )
    print(f"\nTotal tasks: {len(tasks)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Manage experiment tasks: generate HTML, validate, or print a new-task template.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generator.py                    # generate HTML + print summary
  python generator.py --summary-only     # print summary only
  python generator.py --validate         # check questions.json for errors
  python generator.py --template         # print blank task JSON to stdout
  python generator.py --output out.html  # write HTML to a custom path
""",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output path for generated HTML (default: generated_experiment.html)")
    parser.add_argument("--summary-only", action="store_true",
                        help="Print task summary table only; skip HTML generation")
    parser.add_argument("--validate", action="store_true",
                        help="Validate questions.json and report errors; skip HTML generation")
    parser.add_argument("--template", action="store_true",
                        help="Print a blank task JSON template to stdout")
    args = parser.parse_args()

    if args.template:
        print("# Paste this object into the 'tasks' array in questions.json.")
        print("# Remove the 'notes' field if you have nothing to add.")
        print("# Run --validate after editing to check for errors.\n")
        print(json.dumps(BLANK_TASK_TEMPLATE, indent=2))
        return

    data = load_questions(QUESTIONS_PATH)

    if args.validate:
        errors = validate(data)
        if errors:
            print(f"Found {len(errors)} error(s) in {QUESTIONS_PATH}:\n")
            for e in errors:
                print(f"  • {e}")
            sys.exit(1)
        else:
            print(f"All {len(data['tasks'])} tasks in {QUESTIONS_PATH.name} are valid.")
        return

    print_summary(data)

    if args.summary_only:
        return

    html = render_html(data)
    args.output.write_text(html, encoding="utf-8")
    print(f"\nGenerated: {args.output}")


if __name__ == "__main__":
    main()
