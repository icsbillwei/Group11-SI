# Test Coverage with `coverage.py`

This instruction is helping you to install coverage.py, run tests with coverage, and generate a coverage report.

## Installation

1. First, ensure that `coverage.py` is installed. You can install it via `pip`:
    ```bash
    pip install coverage
    ```

## Running Tests with Coverage

2. To run tests with coverage.py and measure code coverage, use the following command:
    ```bash
    coverage run -m unittest discover
    ```
This command will:
* Use `coverage` to monitor code coverage.
* Run all test files that match the `test*.py` pattern (default for `unittest discover`).

## Generating Coverage Reports

After running the tests, you can generate reports to view coverage details.

3. **Terminal Report**: To view a summary of code coverage directly in the terminal, use:
    ```bash
    coverage report
    ```
4. **HTML Report**: For a detailed, interactive report, generate an HTML version:
    ```bash
    coverage html
    ```
This will create a directory named `htmlcov` in the project root. You can open `htmlcov/index. html` in a browser to view the coverage report.

## Review the Report

The HTML report will provide insights into which parts of your code are fully covered, partially covered, or not covered at all. Aim to improve coverage by adding tests for untested code paths, especially critical components.