#!/bin/bash
#SBATCH --partition=short-unkillable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --job-name={{job_name}}
#SBATCH --gres=gpu:h100:4
#SBATCH --cpus-per-gpu=24
#SBATCH --mem-per-gpu=256G
#SBATCH --time={{time}}
#SBATCH --output={{job_dir}}/stdout.txt
#SBATCH --error={{job_dir}}/stderr.txt
