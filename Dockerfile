# Use the Python 3.11 base image
FROM python:3.11

# Set the working directory (optional)
WORKDIR /app

COPY . .

RUN ls -al

RUN pip install --no-cache-dir -r requirements.txt

# Run the 'ls' command during the build stage

RUN which python
RUN python -V

ENTRYPOINT ["python", "main.py"]
