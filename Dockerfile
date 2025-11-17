# المرحلة الأولى: مرحلة البناء (لتنزيل الموديل)
FROM python:3.10-slim as builder

WORKDIR /app

# نسخ ملف المكتبات وتثبيتها (فقط ما نحتاجه للتنزيل)
COPY requirements.txt .
RUN pip install --no-cache-dir azure-storage-blob python-dotenv

# نسخ سكربت التنزيل
COPY download_model.py .

# تشغيل سكربت التنزيل (سيقرأ متغير البيئة من أمر البناء)
# تشغيل سكربت التنزيل (سيقرأ متغير البيئة من أمر البناء)
# هذه هي الطريقة الصحيحة لتمرير الأسرار
ARG AZURE_STORAGE_CONNECTION_STRING
RUN --mount=type=bind,source=download_model.py,target=download_model.py \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install --no-cache-dir azure-storage-blob python-dotenv && \
    python download_model.py



# المرحلة الثانية: مرحلة التشغيل النهائية
FROM python:3.10-slim

WORKDIR /app

# نسخ المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الموديل الذي تم تنزيله من مرحلة البناء
COPY --from=builder /app/model /app/model

# نسخ كود التطبيق
COPY main.py .

# تعريف المنفذ الذي سيعمل عليه التطبيق
EXPOSE 8080

# الأمر لتشغيل التطبيق
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
