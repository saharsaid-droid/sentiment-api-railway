# --- المرحلة 1: البناء ---
FROM python:3.10 as builder

WORKDIR /app

# تثبيت أداة لتنظيف المكتبات
RUN pip install pip-autoremove

# نسخ ملف المكتبات
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# --- هذا هو المسار الصحيح لمكتبات بايثون في هذه الصورة ---
ARG PYTHON_PACKAGES_PATH=/usr/local/lib/python3.10/site-packages

# إزالة الملفات غير الضرورية من المكتبات المثبتة
RUN find ${PYTHON_PACKAGES_PATH} -type d -name '__pycache__' -exec rm -r {} + && \
    find ${PYTHON_PACKAGES_PATH} -type f -name '*.pyc' -delete && \
    pip-autoremove -y pandas numpy mysql-connector-python pyyaml


# --- المرحلة 2: التشغيل ---
FROM python:3.10-slim

WORKDIR /app

# نسخ المكتبات التي تم تنظيفها من مرحلة البناء
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# نسخ كود التطبيق
COPY main.py .

# تعريف المنفذ
EXPOSE 8080

# الأمر للتشغيل
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
