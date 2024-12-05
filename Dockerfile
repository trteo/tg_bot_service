# Use the Python 3.11 base image
FROM python:3.11

# Set the working directory (optional)
WORKDIR /app

COPY . .

# Run the 'ls' command during the build stage
RUN ls -al

RUN which python
RUN python -V

ENTRYPOINT ["python", "main.py"]
