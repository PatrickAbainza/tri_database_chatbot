# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.cargo/bin/uv /usr/local/bin/uv

# Copy the requirements file into the container at /app
# Copy pyproject.toml and uv.lock (if it exists)
COPY pyproject.toml uv.lock* ./

# Install any needed dependencies specified in pyproject.toml
# Using --system to install in the global environment within the container
RUN uv sync --dev --system

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 8000 available to the world outside this container (if needed for a web app)
# EXPOSE 8000

# Define environment variable
# ENV NAME World

# Run main.py when the container launches (example)
# CMD ["python", "src/main.py"]
# Or provide a default command like bash
CMD ["bash"]