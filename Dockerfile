# Base Python image
FROM python:3.10

# Work directory in the container
WORKDIR /app

# Copy local files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the script after running runs container
CMD ["python", "validate_json.py"]