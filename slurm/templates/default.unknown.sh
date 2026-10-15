#!/bin/bash
## Boilerplate: adjust the resources below to your cluster.
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --job-name={{job_name}}
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time={{time}}
#SBATCH --output={{job_dir}}/stdout.txt
#SBATCH --error={{job_dir}}/stderr.txt
