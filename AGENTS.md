# AGENTS.md

## Project Overview
This project analyzes an e-commerce dataset using Power BI.

The goal is to build an end-to-end analytics project covering:
- Data profiling
- Data cleaning and transformation
- Data modeling
- DAX measures
- Dashboard development
- Business insights

## Project Structure

- `data/raw/` - Original datasets. Never modify these files.
- `data/processed/` - Cleaned or transformed datasets.
- `docs/` - Project documentation.
- `powerbi/` - Power BI project files.
- `scripts/data-cleaning/` - Data cleaning or preprocessing scripts.

## Git Rules

- Never commit directly to `main` after project initialization.
- Use a dedicated feature branch for each logical unit of work. If the current branch already matches the task scope, continue working on the current branch instead of creating another branch.
- Never create or switch branches without explicit user approval.
- Keep commits small and focused.
- Use Conventional Commits.
- Review `git status` and `git diff` before committing.
- Never commit credentials or secrets.
- Do not rewrite Git history unless explicitly requested.

Examples:

- `feat: add sales dashboard`
- `feat: create revenue measures`
- `fix: correct customer relationship`
- `docs: add data dictionary`
- `refactor: simplify data transformation`

## Data Rules

- Never modify files inside `data/raw/`.
- Store generated or transformed datasets in `data/processed/`.
- Document important transformations.
- Do not commit large raw datasets.

## Power BI Rules

- Prefer Power BI Project (`.pbip`) format.
- Prefer star schema for the analytical model.
- Create a dedicated Date dimension.
- Prefer explicit DAX measures.
- Use clear and consistent table, column, and measure names.
- Avoid unnecessary calculated columns when a measure can be used.

## Documentation Rules

Update documentation when making significant changes.

Important documentation:
- `README.md` - Project overview and usage
- `docs/data-dictionary.md` - Dataset and column descriptions
- `docs/data-model.md` - Data model and relationships
- `docs/insights.md` - Business findings

## Before Completing a Task

1. Check `git status`.
2. Review `git diff`.
3. Ensure raw data was not modified.
4. Ensure no secrets are included.
5. Summarize the changes.
6. Suggest an appropriate Conventional Commit message.