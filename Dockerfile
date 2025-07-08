# Usage:
#   Ex.
#    docker run -v ~/.aws:/root/.aws:ro aws-ec2-utils python3 ec2_start.py --region ca-central-1 --tag-key env --tag-value dev --dry-run
#    docker run -v ~/.aws:/root/.aws:ro aws-ec2-utils python3 ec2_shutdown.py --region ca-central-1 --tag-key env --tag-value dev --dry-run
#    docker run -v ~/.aws:/root/.aws:ro aws-ec2-utils python3 ec2_metadata.py --region ca-central-1 --tag-key env --tag-value dev --dry-run


FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all source code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default entrypoint (optional)
CMD ["python3", "ec2_shutdown.py", "--help"]
