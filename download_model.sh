#! bin/bash
model_name="Llama-3.1-Storm-8B.Q4_K_M.gguf"
wget https://huggingface.co/QuantFactory/Llama-3.1-Storm-8B-GGUF/resolve/main/Llama-3.1-Storm-8B.Q4_K_M.gguf
mkdir models
mv $model_name models
echo "model save to :  models/$model_name"