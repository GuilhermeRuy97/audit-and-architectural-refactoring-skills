# audit-and-architectural-refactoring-skills

Developing an AI skill that automates the analyzing, auditing, and refactoring any project to the MVC pattern, regardless of the technology.

> Skill Author: GuilhermeRuy97

## The Skill is capable of

* Analyzing a codebase, detecting the current language, framework, and architecture.
* Identifying anti-patterns and code smells, classifying them by severity with exact file and line information.
* Generating a structured audit report with all findings.
* Refactoring the project to the MVC (Model-View-Controller) pattern, eliminating the problems found.
* Validating the result, ensuring that the application continues to function after the changes.

## Classification Scales

### Definition of Severities

The project follows the following classification scale based on MVC and SOLID problems:

- CRITICAL: Critical architecture or security failures that prevent proper functioning, expose sensitive data (e.g. hardcoded credentials, SQL Injection) or violate completely the separation of responsibilities (e.g. "God Class" containing database, complex business logic and routing in the same file).
- HIGH: Strong violations of the MVC pattern or SOLID principles that make maintenance and testing very difficult (e.g. heavy business logic trapped inside Controllers, strong coupling without Dependency Injection, or global mutable state used throughout the application).
- MEDIUM: Problems of standardization, code duplication or moderate performance bottlenecks (e.g. N+1 queries in the database, inappropriate use of middlewares, missing validations in routes).
- LOW: Improvements in readability, bad variable naming, or "magic numbers" scattered throughout the code.

## Use Cases

In this project, we will use 3 projects as a testbed for refactoring.
1. code-smells-project/ (Python/Flask — API de E-commerce)
2. ecommerce-api-legacy/ (Node.js/Express — LMS API com fluxo de checkout)
3. task-manager-api/ (Python/Flask — API de Task Manager)

## Usage Examples on CLI (Command Line Interface)

```
# Execute the skill on the project with problems
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (products, users, orders, order_items)
Architecture:  Monolithic — all in 4 files, no separation of layers
Source files:  4 files analyzed
DB tables:     products, users, orders, order_items
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Single file contains all business logic, SQL queries, validation and formatting for 4 different domains.
Impact: Impossible to test in isolation, any change affects everything.
Recommendation: Separate into models and controllers by domain.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded as 'my-super-secret-key-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refactoring executed ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── product_model.py
│   └── user_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── product_controller.py
│   └── order_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Manual Analysis

> CHANGE ME
### Code Smells Project
[reports\audit-project-1.md](reports/audit-project-1.md)
### Ecommerce API Legacy
[reports\audit-project-2.md](reports/audit-project-2.md)
### Task Manager API
[reports\audit-project-3.md](reports/audit-project-3.md)


Lista dos problemas identificados manualmente em cada projeto
Classificação por severidade
Justificativa de por que cada problema é relevante

## Skill Construction

> CHANGE ME
Decisões de design: como estruturou o SKILL.md e os arquivos de referência
Quais anti-patterns incluiu no catálogo e por quê
Como garantiu que a skill é agnóstica de tecnologia
Desafios encontrados e como resolveu

## Results

> CHANGE ME
Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
Comparação antes/depois da estrutura de cada projeto
Checklist de validação preenchido para cada projeto
Screenshots ou logs mostrando as aplicações rodando após refatoração
Observações sobre como a skill se comportou em stacks diferentes

## How to Execute

> CHANGE ME
Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
Comandos para executar a skill em cada projeto
Como validar que a refatoração funcionou