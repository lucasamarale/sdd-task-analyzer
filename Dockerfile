# Imagem do TaskAnalyzer: empacota o código e o Test Harness num ambiente
# isolado e imutável. O comando padrão roda a suíte completa.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependências primeiro, para o Docker reaproveitar esta camada enquanto
# o requirements.txt não mudar.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pyproject.toml .
COPY src/ src/
COPY tests/ tests/

# Roda sem privilégio de root.
RUN useradd --create-home --uid 1000 analyzer
USER analyzer

CMD ["pytest", "tests/test_harness.py", "-v", "-p", "no:cacheprovider"]
