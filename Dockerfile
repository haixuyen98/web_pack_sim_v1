# Stage 1: Builder
FROM python:3.9 AS builder
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Collect static files
RUN python manage.py compress --force
RUN python manage.py collectstatic --noinput

# Stage 2: Final
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code from the builder stage
COPY --from=builder /app .
COPY --from=builder /app/public/static/public /app/public/static/
COPY --from=builder /app/public/staticfiles /app/public/staticfiles/

# Install Gunicorn
RUN pip install gunicorn

# RUN python manage.py compress --force
# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Remove the default Nginx configuration
# RUN rm /etc/nginx/nginx.conf

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/

# Expose the Nginx port
EXPOSE 80

CMD nginx -t & service nginx start & gunicorn -b 0.0.0.0:8000 core.wsgi:application