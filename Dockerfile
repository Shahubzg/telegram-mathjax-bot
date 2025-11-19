# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install necessary Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire bot project
COPY . .

# Run the bot
CMD ["python", "bot.py"]