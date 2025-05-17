# ---- build stage ----
FROM python:3.11-slim AS build

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-deps -r requirements.txt -w /wheels

# ---- runtime stage ----
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# add wheels then install
COPY --from=build /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*

# copy source
COPY app ./app
COPY logs ./logs      # create if empty
RUN mkdir -p temp_uploads

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]