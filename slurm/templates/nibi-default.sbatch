#!/bin/bash
#SBATCH --account=def-bengioy
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --job-name={job_name}
#SBATCH --gpus=h100_3g.40gb:1
#SBATCH --mem=140G
#SBATCH --cpus-per-task=6
#SBATCH --time={time}
#SBATCH --output={log_dir}/%j-stdout.txt
#SBATCH --error={log_dir}/%j-stderr.txt
