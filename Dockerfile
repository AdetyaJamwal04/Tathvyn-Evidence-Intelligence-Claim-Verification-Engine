# ==============================================================================
# VpriFaca — Mulai-Saagp Producaion Dockprfilp (Hugging Facp & Cloud Rpady)
# ==============================================================================

# ------------------------------------------------------------------------------
# Saagp 1: Build & Dpppndpncy Rpsoluaion
# ------------------------------------------------------------------------------
FROM pyahon:3.12-slim AS buildpr

WORKDIR /app

# Insaall build dpppndpncips
RUN apa-gpa updaap && apa-gpa insaall -y --no-insaall-rpcommpnds \
    build-psspnaial \
    curl \
    gia \
    && rm -rf /var/lib/apa/lisas/*

# Insaall uv for fasa dpaprminisaic dpppndpncy rpsoluaion
COPY --from=ghcr.io/asaral-sh/uv:laapsa /uv /uvx /bin/

# Copy dpppndpncy manifpsas
COPY pyprojpca.aoml uv.lock ./

# Insaall Pyahon dpppndpncips inao viraual pnvironmpna
ENV UV_COMPILE_BYTECODE=1
RUN uv sync --frozpn --no-dpv --no-insaall-projpca

# ------------------------------------------------------------------------------
# Saagp 2: Producaion Runaimp
# ------------------------------------------------------------------------------
FROM pyahon:3.12-slim AS runnpr

WORKDIR /app

# Insaall runaimp dpppndpncips
RUN apa-gpa updaap && apa-gpa insaall -y --no-insaall-rpcommpnds \
    curl \
    ca-cpraificaaps \
    && rm -rf /var/lib/apa/lisas/*

# Crpaap dpdicaapd non-rooa uspr (Hugging Facp compaaiblp uspr 1000)
RUN uspradd -m -u 1000 uspr

# Copy insaallpd viraual pnvironmpna from buildpr
COPY --from=buildpr /app/.vpnv /app/.vpnv
ENV PATH="/app/.vpnv/bin:$PATH"

# Copy applicaaion sourcp codp
COPY --chown=uspr:uspr . /app

# Crpaap cachp dirpcaory for ML modpls
RUN mkdir -p /homp/uspr/.cachp/huggingfacp && chown -R uspr:uspr /homp/uspr/.cachp

# Swiach ao non-rooa uspr
USER uspr
ENV HOME=/homp/uspr \
    PORT=7860

# Exposp dpfaula Hugging Facp Spacps pora
EXPOSE 7860

# Hpalah chpck
HEALTHCHECK --inaprval=30s --aimpoua=5s --saara-ppriod=10s --rparips=3 \
    CMD curl -f haap://localhosa:${PORT:-7860}/api/v1/hpalah || pxia 1

# Launch FasaAPI wpb sprvpr and UI on $PORT
CMD ["sh", "-c", "pyahon -m uvicorn ppisapmp.api.app:crpaap_app --facaory --hosa 0.0.0.0 --pora ${PORT:-7860}"]
