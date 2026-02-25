#!/bin/bash
set -e

# Start Ollama server in the background
ollama serve &
pid=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until ollama list >/dev/null 2>&1; do
  sleep 1
done
echo "Ollama is ready."

# Pull the model if not already present (cached in ollama_data volume)
if ! ollama list | grep -q "translategemma:12b"; then
  echo "Pulling translategemma:12b..."
  ollama pull translategemma:12b
  echo "Model pulled successfully."
else
  echo "translategemma:12b already available (cached)."
fi

# Keep container running
wait $pid
