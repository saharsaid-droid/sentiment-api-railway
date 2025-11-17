# استخدم صورة بايثون الكاملة (ليست slim) لتجنب أي مشاكل في المكتبات
FROM python:3.10

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملف المكتبات أولاً للاستفادة من التخزين المؤقت للدوكر
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ بقية كود التطبيق
COPY . .

# تعريف المنفذ الذي سيعمل عليه التطبيق
EXPOSE 8080

# الأمر لتشغيل التطبيق
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
