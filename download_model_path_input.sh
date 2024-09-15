#! bin/bash
echo "Enter model url: "
read model_url
echo "enter model name: "
read model_name
# model_name="Llama-3.1-Storm-8B.Q4_K_M.gguf"
wget $model_url
mkdir models
mv $model_name models
echo "model save to :  models/$model_name"