"""UiPath Coded Agent entry-points.

Each module here exposes a `run(input: dict) -> dict` function — the contract
a UiPath Coded Agent / API Workflow calls. They validate input with the
agent's Pydantic models, invoke the underlying coded agent, and return plain
JSON-serializable dicts the Maestro Case can route between stages.

The UiPath SDK binding (decorators, manifest registration) is added once the
Labs Maestro API surface is mapped; these `run()` functions are the stable
core that binding will wrap.
"""
