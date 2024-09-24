# Start from the unclecode/crawl4ai:latest image
FROM unclecode/crawl4ai:latest

# Install JupyterLab
RUN pip install jupyterlab sqlalchemy psycopg2-binary pandas colorama

# Create a directory for mounting the local volume
RUN mkdir /workspace

# Set the working directory
WORKDIR /workspace

# Expose the default JupyterLab port
EXPOSE 8888

# Start JupyterLab when the container launches
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
