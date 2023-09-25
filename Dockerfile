FROM python:latest
COPY . /async_fastapi_ui
WORKDIR /async_fastapi_ui
RUN pip install -r requirements.txt
CMD ["python3", "-u", "main.py"]