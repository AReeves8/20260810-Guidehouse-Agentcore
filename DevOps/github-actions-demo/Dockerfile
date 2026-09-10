# Multi-stage build. Two FROM lines, and only the second one ships.
#
# WHY BOTHER: installing Python packages needs a compiler toolchain and pip's
# entire download cache. Running them needs neither. A single-stage image
# carries all of that to production forever -- every pull, every scale-out,
# every node in the cluster. The builder stage below does the messy work and
# is then discarded; only the installed site-packages cross the boundary.
#
# Measure it live rather than asserting it:
#     docker build -t fieldnotes:multi .
#     docker build -t fieldnotes:single --target builder .
#     docker images | grep fieldnotes

# ---------------------------------------------------------------------------
# Stage 1 -- builder. Everything expensive and disposable happens here.
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# A virtualenv inside the image is the trick that makes the copy easy: one
# self-contained directory holds every dependency, so the final stage copies a
# single path instead of hunting through system site-packages.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Dependency metadata is copied BEFORE the source. Docker caches each layer
# and invalidates everything after the first change -- so with this order,
# editing a route re-runs only the last COPY. Reverse these two and every
# one-line code change reinstalls every dependency from scratch.
COPY pyproject.toml .
COPY fieldnotes/__init__.py fieldnotes/
RUN pip install --no-cache-dir .

COPY fieldnotes/ fieldnotes/
COPY migrations/ migrations/
RUN pip install --no-cache-dir --no-deps .

# ---------------------------------------------------------------------------
# Stage 2 -- runtime. Only what is needed to serve a request.
# ---------------------------------------------------------------------------
FROM python:3.11-slim

# A non-root user. Containers run as root by default, which means a process
# escape starts with root inside the container -- an unnecessary head start
# for an attacker when the app never needs to write outside its own directory.
RUN useradd --create-home --shell /bin/false appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/fieldnotes /app/fieldnotes
COPY --from=builder /build/migrations /app/migrations

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# PYTHONUNBUFFERED matters more than it looks. Without it, Python buffers
# stdout when it is not a terminal -- so your logs sit in a buffer instead of
# reaching CloudWatch, and a container that crashes takes its last and most
# useful log lines with it.

USER appuser
EXPOSE 8000

# gunicorn, not `flask run`. The development server is single-threaded, warns
# that it is not for production, and has no process supervision. gunicorn
# forks workers, restarts them when they die, and is what every platform in
# this course expects to find behind port 8000.
#
# 2 workers is sized for the small instances used today. The usual starting
# point is (2 x CPU cores) + 1 -- worth stating so nobody treats 2 as magic.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", \
     "--access-logfile", "-", "fieldnotes.app:app"]
