FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# ✅ Tambahkan ini untuk benar-benar force upgrade ke versi terbaru
RUN pip install --upgrade pip && pip uninstall -y google-generativeai && pip install --no-cache-dir google-generativeai>=0.3.2 && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/agent/main.py"]
