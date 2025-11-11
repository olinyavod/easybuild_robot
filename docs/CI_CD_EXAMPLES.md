# Пример конфигурации для CI/CD
# Этот файл можно использовать как основу для GitHub Actions, GitLab CI, и т.д.

# ═══════════════════════════════════════════════════════════
# GITHUB ACTIONS (.github/workflows/lint.yml)
# ═══════════════════════════════════════════════════════════

name: Lint and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint-python:
    name: Lint Python Code
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd python
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run Ruff Linter
        run: |
          cd python
          ruff check .

      - name: Check Ruff Formatting
        run: |
          cd python
          ruff format --check .

      - name: Run MyPy Type Checking
        run: |
          cd python
          mypy src/
        continue-on-error: true  # Пока типы не все добавлены

  lint-dart:
    name: Lint Dart Code
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Dart
        uses: dart-lang/setup-dart@v1
        with:
          sdk: stable

      - name: Install dependencies
        run: |
          cd dart
          dart pub get

      - name: Run Dart Analyzer
        run: |
          cd dart
          dart analyze

      - name: Check Dart Formatting
        run: |
          cd dart
          dart format --output=none --set-exit-if-changed .

# ═══════════════════════════════════════════════════════════
# GITLAB CI (.gitlab-ci.yml)
# ═══════════════════════════════════════════════════════════

stages:
  - lint
  - test

lint:python:
  stage: lint
  image: python:3.9
  script:
    - cd python
    - pip install -r requirements.txt -r requirements-dev.txt
    - ruff check .
    - ruff format --check .
    - mypy src/ || true
  only:
    - merge_requests
    - main
    - develop

lint:dart:
  stage: lint
  image: dart:stable
  script:
    - cd dart
    - dart pub get
    - dart analyze
    - dart format --output=none --set-exit-if-changed .
  only:
    - merge_requests
    - main
    - develop

# ═══════════════════════════════════════════════════════════
# JENKINS (Jenkinsfile)
# ═══════════════════════════════════════════════════════════

pipeline {
    agent any

    stages {
        stage('Lint Python') {
            steps {
                dir('python') {
                    sh 'pip install -r requirements.txt -r requirements-dev.txt'
                    sh 'ruff check .'
                    sh 'ruff format --check .'
                    sh 'mypy src/ || true'
                }
            }
        }

        stage('Lint Dart') {
            steps {
                dir('dart') {
                    sh 'dart pub get'
                    sh 'dart analyze'
                    sh 'dart format --output=none --set-exit-if-changed .'
                }
            }
        }
    }
}

# ═══════════════════════════════════════════════════════════
# AZURE PIPELINES (azure-pipelines.yml)
# ═══════════════════════════════════════════════════════════

trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

jobs:
- job: LintPython
  displayName: 'Lint Python Code'
  steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.9'

  - script: |
      cd python
      pip install -r requirements.txt -r requirements-dev.txt
      ruff check .
      ruff format --check .
      mypy src/
    displayName: 'Run Python Linters'

- job: LintDart
  displayName: 'Lint Dart Code'
  steps:
  - script: |
      cd dart
      dart pub get
      dart analyze
      dart format --output=none --set-exit-if-changed .
    displayName: 'Run Dart Linters'




