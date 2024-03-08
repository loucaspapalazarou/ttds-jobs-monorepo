# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

RUN apt-get update && apt-get install -y

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
# RUN pip install Cython

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/src

# CMD ["python", "main.py"]
CMD ["python", "main.py", "-s"]
