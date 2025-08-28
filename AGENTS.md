# AGENTS.md: The Development Constitution

This document outlines the principles, processes, and quality standards that all agents must adhere to when contributing to this project. Our goal is to build a high-quality, maintainable, and understandable system.

## 1. Core Philosophy

Two core principles guide all development:

1.  **Domain == Documentation == Code:** The domain model, the documentation, and the source code are not separate artifacts; they are different representations of the same reality. They must always be kept in perfect synchronization. A change in one necessitates a change in the others.
2.  **Quality is a Trajectory:** Every commit must demonstrably improve the overall quality of the product. Quality is not a static state but a continuous upward trend. This is ensured by rigorous testing and quantifiable metrics.

## 2. Development Methodology

We adhere to a strict methodology that combines Domain-Driven Design, Literate Programming, and Test-Driven Development.

### 2.1. Domain-Driven Design (DDD)

The code's structure must mirror the domain model described in the `README.md`.

-   **Directory Structure:** All core domain logic will reside in `src/domains/`. Each primary domain concept (e.g.,   ) will have its own dedicated module within this directory.
    ```
    src/
    └── ├── domains/
        │   ├── domain1/
        │   │   ├── models.py
        │   │   ├── repository.py
        │   │   └── services.py
        │   └── ...
        ├── main.py
        └── ...
    ```
-   **Ubiquitous Language:** Use the terminology from the domain model (  ) consistently in the code, comments, and documentation.
-   **Boundaries and Repositories:** To maintain a clean separation of concerns, the following structure is required for every domain:
    -   `schemas.py`: Contains Pydantic models for defining data shapes at API boundaries (e.g., for request and response validation). All API communication must use these schemas.
    -   `repository.py`: Contains a dedicated repository class that encapsulates all database access logic for the domain. All methods must be fully type-hinted. The API layer should use this repository and not interact with the database directly.

### 2.2. Literate Programming

Code MUST be written as a narrative. It should be optimized for human understanding first, and machine execution second.

-   **Docstrings:** Every module, class, and function must have a comprehensive docstring explaining its purpose, arguments, and return values. Use Google-style docstrings.
-   **Comments:** Use inline comments to explain complex logic, assumptions, or the "why" behind a particular implementation choice. The goal is to make the code's intent self-evident without the reader having to reverse-engineer it.

### 2.3. Test-Driven Development (TDD)

All development MUST follow the strict "Red-Green-Refactor" cycle.

1.  **Red:** Write a new test case that captures a requirement or bug. It must fail because the implementation does not yet exist. Commit this failing test.
2.  **Green:** Write the simplest possible code to make the test pass.
3.  **Refactor:** Clean up the implementation code while ensuring all tests still pass.
4.  **Commit:** Commit the passing code and the refactoring.

### 2.4. AICODE- Comment Prefixes

When working with code, you MUST use and recognize specific comment prefixes to structure your interactions. Before you begin editing any file, you must first scan the entire file for comments with the "AICODE-" prefix. Here are the comment prefixes to use:

- AICODE-NOTE: Use this prefix to leave a note or comment for the AI Code system (Jules, Codex, Cursor).
- AICODE-TODO: Use this prefix to create a task for yourself to address later in the session.
These single-line comments should be used to provide context, leave reminders, or outline pending tasks.

- AICODE-PSEUDO: use this prefix for writing pseudocode _before_ implementing actual logic in code.
- AICODE-MATH: use this prefix to develop mathematics for non-trivial algorithms or other challenges. Assume identity of mathematics PhD for the time of developing mathematics and writing this comment.

Always check for these comments to inform your workflow and ensure that you are incorporating any relevant notes or tasks into your process.

**Searching for AICODE Comments:**
To efficiently find all `AICODE-` comments across the project, use `ripgrep` (`rg`):
```sh
rg "AICODE-"
```

## 3. Quantifiable Quality Gates

Every change will be evaluated against a set of objective quality metrics. A change that does not meet these standards will be rejected.

### 3.1. Test Suite
-   **Coverage:** Overall test coverage must be **95% or higher**, as measured by `coverage.py`. A commit is not allowed to decrease the current coverage percentage.
-   **Test Types:** New features must be accompanied by both **unit tests** for individual components and **integration tests** that verify the entire workflow.

### 3.2. Code Health
-   **Linting & Typing:** The code must pass both `ruff` and `mypy` with **zero errors or warnings**. The `mypy` configuration includes the official Pydantic plugin, which is configured in `pyproject.toml`.
-   **Code Complexity:** The cyclomatic complexity of any function must not exceed **10**, as measured by `radon`. Functions exceeding this limit must be refactored.
-   **Anti-Patterns:** The code must be free of known anti-patterns. The official reference for this is **The Hitchhiker's Guide to Python** (docs.python-guide.org), particularly its section on "Writing Great Python Code".

### 3.3. Documentation
-   **Docstrings & Comments:** All new code must follow the Literate Programming guidelines in section 2.2.
-   **README Sync:** The `README.md` and any other architectural documents must be updated to reflect any changes in the code.

### 3.4. Property-Based Testing with Hypothesis

In addition to unit and integration tests, this project mandates the use of **property-based testing** for any component involving complex logic, data processing, or parsing. Property-based tests check that certain properties of your code hold true across a wide range of automatically generated inputs, helping to uncover edge cases that are easy to miss with example-based testing.

We use the [Hypothesis](https://hypothesis.readthedocs.io/) library for this purpose.

**Core Principle:** Instead of writing a test for a single input, you write a test that describes a *property* that should be true for *all* valid inputs. Hypothesis then generates hundreds of diverse examples to try to falsify this property.

**Example:**
Consider a function `encode_and_decode()` that should be perfectly reversible. A property-based test would look like this:

```python
from hypothesis import given, strategies as st

# Assumes the function can handle any unicode text
@given(st.text())
def test_reversibility(original_string):
    """
    Tests that encoding and then decoding a string returns the original value.
    """
    encoded = my_encoder(original_string)
    decoded = my_decoder(encoded)
    assert original_string == decoded
```

Hypothesis will generate a wide variety of strings—empty, very long, with strange Unicode characters, etc.—to robustly test this property. If it finds a failing example, it will automatically simplify it to the smallest possible failing case to aid in debugging.

**Requirement:** For any new feature that involves complex data manipulation, at least one property-based test MUST be included.

#### 3.4.1. Advanced Fuzzing with HypoFuzz

For particularly critical or complex parts of the system, we can enhance our property-based tests using [HypoFuzz](https://hypofuzz.com/). HypoFuzz is a tool that applies advanced, coverage-guided fuzzing techniques to your existing Hypothesis test suite.

**When to Use It:**
-   When you have a complex piece of logic that you want to test more exhaustively than the standard Hypothesis run.
-   When you have idle compute resources and want to dedicate them to finding deep bugs.

HypoFuzz can be run against your test suite to "farm" for bugs over a long period. It is free for open-source and non-commercial projects. Refer to the [HypoFuzz documentation](https://hypofuzz.com/docs/) to get started.

**CLI Usage:**

HypoFuzz integrates with the `hypothesis` command-line tool. The main command is `hypothesis fuzz`. This command will run indefinitely, so you'll need to stop it with `Ctrl+C`.

*   **Run on all cores:**
    ```sh
    hypothesis fuzz
    ```
*   **Run on a specific number of cores (e.g., 2):**
    ```sh
    hypothesis fuzz -n 2
    ```
*   **Run only the dashboard without fuzzing:**
    ```sh
    hypothesis fuzz --dashboard-only
    ```
*   **Run only fuzzing without the dashboard:**
    ```sh
    hypothesis fuzz --no-dashboard
    ```
*   **Run against specific tests (e.g., tests with "parse" in the name):**
    Arguments after `--` are passed to `pytest`.
    ```sh
    hypothesis fuzz -- -k parse
    ```

## 4. Task Implementation Workflow

Every task, from a new feature to a bug fix, must follow this structured, multi-persona workflow. This ensures that work is thoroughly understood, planned, and executed to the highest standard.

### Phase 1: Product Analysis (Product Manager Persona)
Before writing any code, you must first deeply understand the task's goals and context.
1.  **Study:** Analyze the user request, the existing codebase, and any relevant documentation (`README.md`, etc.).
2.  **Define:** Act as a Product Manager. Create a temporary file named `product_brief_temp.md`. In this file, define the "what" and "why" of the task, the user stories, and the acceptance criteria.

### Phase 2: Developer Briefing
Translate the product brief into a technical brief.
1.  **Formulate:** Act as a technical lead. Create a `brief_temp.md` file that outlines the technical approach, potential challenges, and the parts of the codebase that will be affected.

### Phase 3: Granular Planning (Senior Developer Persona)
Create a detailed implementation plan suitable for a junior developer to understand and follow.
1.  **Plan:** Act as a seasoned, pragmatic senior developer. Create a `todo_temp.md` file.
2.  **Detail:** Break down the technical brief into an extremely granular, step-by-step checklist of actions. Each step should be a small, verifiable change.

### Phase 4: Implementation & Verification (Senior Python Developer Persona)
Execute the plan from `todo_temp.md`. This is the hands-on coding phase.
1.  **Setup:** Ensure your environment is ready (virtual environment activated, dependencies installed via `pip install -r requirements.txt` and `requirements-dev.txt`).
2.  **Execute:** Follow your `todo_temp.md` step-by-step. Adhere strictly to the TDD cycle for all code changes.
3.  **Document as you go:** Write `AICODE-` comments to explain your thought process. Update the `todo_temp.md` file by checking off items as you complete them.
4.  **Verify Continuously:** After each significant change, run the relevant quality checks:
    -   **Tests & Coverage:** `coverage run -m pytest && coverage report`
    -   **Code Health:** `ruff check . && mypy . && radon cc . -a -nc`
5.  **Submit:** Once all steps in `todo_temp.md` are complete and all quality gates pass, commit the work. The commit message must include the completed Code Review Scorecard.

### The Code Review Scorecard
This scorecard must be completed and included in the body of every commit message.

```markdown
### Code Review Scorecard

-   [ ] **Workflow Adherence:** The full multi-persona workflow was followed, and the temporary brief/todo files were used.
-   [ ] **TDD Compliance:** A failing test was written and committed *before* each implementation part.
-   [ ] **Test Coverage:** All new code is covered by both unit and integration tests, and overall coverage is >=95%.
-   [ ] **Code Health:** All quality gates (`ruff`, `mypy`, `radon`) pass successfully.
-   [ ] **Maintainability:** The code is clean, readable, and its complexity is within limits.
-   [ ] **Anti-Patterns:** The code has been checked against The Hitchhiker's Guide to Python and contains no known anti-patterns.
-   [ ] **Documentation:** All docstrings have been written, and the `README.md` has been updated to reflect any changes.
-   [ ] **Dependency Integrity:** Any new dependencies have been approved and added to the lock file.
```

## 5. Dependency Management

To ensure the project is "future proof" and builds are reproducible, all dependencies are strictly managed.

-   **Locking:** A dependency locking tool (e.g., `pip-tools`) must be used to pin all direct and transitive dependencies.
-   **Approval:** No new production dependency may be added without approval. Justification must be provided, ensuring the library is well-maintained and secure.
-   **Updates:** Dependencies should be reviewed and updated on a regular basis (at least monthly) to incorporate security patches and bug fixes.

## 6. Agent Conduct

### 6.1. Autonomy and User Interaction

-   **Proactive Problem-Solving:** The agent is expected to solve problems autonomously. This includes diagnosing errors, formulating solutions, and executing implementation plans without step-by-step guidance. You are supposed to complete the task autonomously. You can diagnose issue, formulate and test hypotheses, search web, and use any tool available to you. **!!Task completion is paramount!!**
-   **Minimize User Input:** **NEVER** ask for user input unless it is absolutely necessary to resolve ambiguity in the request. The user's time is valuable; strive to deliver complete, working solutions without unnecessary interaction. Explicit requests from the user are the exception and should always be followed.

## 7. Codebase Search

To efficiently search the codebase, use the following tools:

### Ripgrep (rg)

`ripgrep` is a line-oriented search tool that recursively searches the current directory for a regex pattern. It's fast and respects `.gitignore`.

**Basic Usage:**

```sh
# Search for a literal string
rg "my_function"

# Search for a regular expression (e.g., find all function definitions)
rg "def .*\("

# Search for a pattern in a specific file type
rg "my_variable" --type py

# List files containing a match
rg "AICODE-" --files-with-matches
```

### AST-Grep (sg)

`ast-grep` is a tool for searching code based on its Abstract Syntax Tree (AST). This allows for more structural and semantic searches than `ripgrep`. Docs: https://ast-grep.github.io/guide/quick-start.html and further on https://ast-grep.github.io/

**Basic Usage:**

```sh
# Find all function calls to `my_function`
sg -p 'my_function($_)' -l py

# Find all function definitions with a specific name
sg -p 'def $NAME($_): $$$' -l py --where '$NAME.text() == "my_function"'

# Find all classes that inherit from a specific class
sg -p 'class $NAME(BaseClass): $$$' -l py
```
