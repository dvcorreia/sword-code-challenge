{ python3 }:

python3.pkgs.buildPythonApplication {
  pname = "clinical_recommendations";
  version = "0.0.1";

  format = "pyproject";

  src = ./.;

  propagatedBuildInputs = with python3.pkgs; [
    setuptools
    setuptools-scm

    fastapi
    pydantic
    hypercorn
    httpx
    sqlalchemy
    sqlalchemy.optional-dependencies.asyncio
    aiosqlite
    asyncpg
    psycopg2-binary
    redis
    structlog
    opentelemetry-api
    opentelemetry-sdk
    prometheus-client
    opentelemetry-exporter-prometheus
    opentelemetry-instrumentation-fastapi

    # consumer optional dependencies
    duckdb
  ];

  nativeCheckInputs = with python3.pkgs; [
    black
    coverage
    isort
    mypy
    pytest
    pytest-asyncio
    pytest-sugar
    ruff
  ];

  doCheck = false; # TODO: no tests yet
  checkPhase = ''
    pytest test/
  '';
}
