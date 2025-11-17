# --- المرحلة 1: البناء ---
# نستخدم صورة كاملة هنا لتثبيت المكتبات
FROM python:3.10 as builder

WORKDIR /app

# تثبيت أداة لتنظيف المكتبات
RUN pip install pip-autoremove

# نسخ ملف المكتبات
COPY requirements.txt .

# تثبيت المكتبات مع خيارات لتقليل الحجم
# --no-cache-dir: لا يخزن الكاش
# --prefer-binary: يفضل الملفات الثنائية المترجمة مسبقًا (أسرع وأصغر)
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# إزالة الملفات غير الضرورية من المكتبات المثبتة
# هذا الأمر سيقوم بتقليص الحجم بشكل كبير
RUN find /usr/local/lib/python3.10/site-packages/ -type d -name '__pycache__' -exec rm -r {} + && \
    find /usr-local/lib/python3.10/site-packages/ -type f -name '*.pyc' -delete && \
    pip-autoremove -y pandas numpy # أزيلي المكتبات الكبيرة التي لا نحتاجها في النسخة النهائية


# --- المرحلة 2: التشغيل ---
# نستخدم صورة "slim" صغيرة جدًا للتشغيل النهائي
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

