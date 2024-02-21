FROM python:3.8-slim

# Install system dependencies required for PyODBC and the ODBC Driver for SQL Server
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    g++ \
    unixodbc-dev \
    curl

# # Download the Microsoft repository GPG keys
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# # Register the Microsoft SQL Server Ubuntu repository for SQL Server 2019
# RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# # Install SQL Server drivers and tools
# RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# # Clean up the apt cache to reduce image size
# RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install ODBC Driver 18 for SQL Server and necessary tools
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc \
    # Optional clean up
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Enable ODBC tracing
RUN echo "[ODBC]\n\
Trace = Yes\n\
TraceFile = /var/log/odbc.log\n" >> /etc/odbcinst.ini

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . .

# Command to run the application
CMD ["python", "app.py"]
