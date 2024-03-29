import torch

from matching_utils import grid_search
from transformers import AutoTokenizer
import os

from ray import tune
import ray

import sys
sys.path.insert(1, "../")
import data_handler

# Select GPU to run experiments
os.environ["CUDA_VISIBLE_DEVICES"]="3"
device = torch.device(0)

ray.shutdown()
ray.init(num_gpus=1) 

# Load data
df_train, df_val, _ = data_handler.load(path="../dataset/", filename_train="train.csv", filename_dev="dev.csv", sep_char='#')

# Concatenate topics and keypoints, as stated in the paper
df_train = data_handler.concatenate_topics(df_train)
df_val = data_handler.concatenate_topics(df_val)

# Select model to test
model_type = 'bert-base-uncased'

# Load model's tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_type, do_lower_case=True)

# Set max length for tokenization
max_length = 100

# Configuration of hyper-parameters to try during the grid search
params = {
    'tokenizer': tokenizer,
    'max_length': max_length,
    'batch_size': 8,
    'loss': torch.nn.MSELoss(),
    'optimizer': 'sgd',
    'lr': 1e-3,
    'eps': 'null',
    'epochs': 2,
    'warmup_steps': tune.grid_search([1e2]),
    'weight_decay': tune.grid_search([1e-8]),
    'momentum': tune.grid_search([0]),
    'nesterov': False
}

# Perform grid search
results = grid_search(df_train, df_val, model_type, params, ['accuracy', 'precision', 'recall', 'f1'], device)


