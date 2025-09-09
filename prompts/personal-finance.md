## Prompt Identification
- **Name**: Personal Finance Project default prompt
- **Version**: 0.1
- **Created By**: MauGx3
- **Last Modified**: 2025-09-08
- **Category**: Web and desktop app

## Purpose and Goals
- **Primary Goal**: Create a basic web and desktop app using Python, Django and Docker, primarily focused on functionality, that contains the features stated on the SCAFF structure below.
- **Use Cases**: web development, software development, finance, investing
- **Expected Output**: A simple GUI that has functional modules to be further developed and debugged.

## Technical Configuration
- **Target Model**: GitHub Copilot
- **Parameters**:
  * Temperature: 0.5
  * Token Limit: 5 tokens
  * Top-K: N/A
  * Top-P: N/A

## S.C.A.F.F. Structure

### Situation
This code uses Django as the web framework. The code depends on many dependencies, but the finance packages are essential, such as `yfinance`, `stockdex` etc that need to work properly and have fallbacks to guarantee best functionality for the app.
### Challenge
Create a complete personal finance/investing platform complete with portfolio tracking, asset data visualization, charts, quantitative analysis, backtesting etc.

### Audience
Keep the code accessible to junior developers where possible, but don't let it be a constraint for making better code if a more complex approach would lead to better performance, security etc. Use comments where needed to explain code for a junior dev, in that case.

### Format
Code should follow Pythonic foundations. Use Google documentation guidelines for the Python code. This project was started by using the [cookiecutter-django] template. Formatter is `ruff`, `uv` should be preferred over `pip` when available. 
### Foundations
This code will be mostly deployed as a Docker container, so there should be a focus on maintain security and performance for a Docker app. For my personal use, I will run the app on a QNAP NAS running QTS 5. A large amount of data will be expected to be used as the app develops and the user collects more data, so consider best practices for following Big Data performance.
## Usage Guidelines
- **For Security-Critical Components**:
  - Set temperature: 0.0-0.2
  - Include explicit security requirements
  - Request detailed documentation of security measures

- **For Performance-Sensitive Components**:
  - Specify performance constraints
  - Request optimization techniques
  - Require complexity analysis

- **For UI Components**:
  - Include accessibility requirements
  - Specify responsive design needs
  - Reference design system patterns

## Effectiveness Metrics
- **Success Rate**: 85% usable on first attempt
- **Iteration Count**: Usually 3 to 5 iterations
- **Issues Found**: None so far
- **Time Savings**: Approximately 5 to 7 hours per implementation

## Documentation
- **Related Components**: [Links to related components]
- **Security Review**: Codebase verified by Snyk
- **Notes and Insights**: This prompt was created based on the Vibe Coding Framework and follows the S.C.A.F.F. Prompt Structure. Refer to this docs regarding AI coding: https://docs.vibe-coding-framework.com/
- **Improvement History**: 
	- 0.1: initial prompt
