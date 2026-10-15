#!/bin/bash
#SBATCH --account=def-bengioy
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --job-name={{job_name}}
#SBATCH --gpus=h100_3g.40gb:1
#SBATCH --mem=140G
#SBATCH --cpus-per-task=6
#SBATCH --time={{time}}
#SBATCH --output={{job_dir}}/stdout.txt
#SBATCH --error={{job_dir}}/stderr.txt
