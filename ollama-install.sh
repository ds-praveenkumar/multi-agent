curl https://ollama.ai/install.sh | sh

ollama pull llama3.1

sudo service ollama stop

nohup env OLLAMA_HOST=0.0.0.0:11434 ollama serve

