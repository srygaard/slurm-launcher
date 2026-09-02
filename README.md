# slurm-launcher

Minimal SLURM job launcher. `job.py` submits `train.py`.

The job will inject the SBATCH header from `slurm/templates/<config>.<cluster>.sh`.

* The `<cluster>` is automatically detected at Mila and DRAC clusters but may be overridden using `--cluster`
* The `<config>` uses `default` but may be overridden using `--config`

```bash
chmod +x job.py
./job.py --dry-run                    # print the generated script, submit nothing
./job.py                              # submit a job with slurm/templates/default.<cluster>.sh
./job.py -c h100                      # manually specify a sbatch template config slurm/templates/h100.<cluster>.sh
./job.py -- --lr 3e-4 --steps 10000   # pass through args to run "train.py --lr 3e-4 --steps 10000"
./job.py -d 12345                     # wait until job 12345 completes before starting (--dependency)
./job.py -f slurm/templates/h100.mila.sh   # submit with a specific sbatch template file
```

Full flag list (`-C` is autodetected and `-l` is relative to this repo, so both vary by machine):

```
usage: job.py [-h] [-l LOG_DIR] [-f TEMPLATE] [-C CLUSTER] [-c CONFIG]
              [-T TIME] [-d DEPENDENCY] [--dry-run]
              ...

Submit a job to SLURM.

positional arguments:
  extra_args            Arguments forwarded to script, e.g. `-- --lr 3e-4
                        --steps 10000`

options:
  -h, --help            show this help message and exit
  -l LOG_DIR, --log-dir LOG_DIR
                        Directory for job logs and script snapshot (default:
                        /path/to/slurm-launcher/slurm/jobs)
  -f TEMPLATE, --template TEMPLATE
                        Path to a template file, overriding
                        slurm/templates/<config>.<cluster>.sh (default: None)
  -C CLUSTER, --cluster CLUSTER
                        Override the cluster instead of using the autodetected
                        name (default: mila)
  -c CONFIG, --config CONFIG
                        Selects slurm/templates/<config>.<cluster>.sh
                        (default: default)
  -T TIME, --time TIME  The sbatch wall-clock limit (HH:MM:SS) (default:
                        3:00:00)
  -d DEPENDENCY, --dependency DEPENDENCY
                        Wait until the specified job ID finishes before
                        starting the job (default: None)
  --dry-run             Print the generated script without submitting
                        (default: False)
```

## Running on another cluster

Autodetection only recognizes Mila and DRAC's national clusters — anywhere else
it falls back to `unknown`. On any other cluster:

1. Pass `--cluster <cluster>` explicitly; otherwise it resolves to the
   literal `slurm/templates/default.unknown.sh`.
2. Add `slurm/templates/default.<cluster>.sh` with that cluster's `#SBATCH` lines.
3. Optional: use `{job_name}`, `{time}`, and `{log_dir}` as placeholders in the template.
