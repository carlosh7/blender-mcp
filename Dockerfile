FROM python:3.12-slim

RUN pip install uv
RUN uv tool install blender-mcp

EXPOSE 9876 9877 9879

ENV BLENDER_HOST=localhost
ENV BLENDER_PORT=9876

CMD ["blender-mcp", "--mode", "sse", "--port", "9879"]
