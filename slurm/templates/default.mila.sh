#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --job-name={{job_name}}
#SBATCH --gres=gpu:l40s:1
#SBATCH --mem-per-gpu=256G
#SBATCH --cpus-per-gpu=12
#SBATCH --time={{time}}
#SBATCH --output={{job_dir}}/stdout.txt
#SBATCH --error={{job_dir}}/stderr.txt
