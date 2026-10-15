# slurm-launcher

Minimal SLURM job launcher. `job.py` submits `train.py`.

`job.py` builds the job script using an SBATCH header from `slurm/templates/<config>.<cluster>.sh`.

* The `<cluster>` is automatically detected at Mila and DRAC clusters but may be overridden using `--cluster`.
  Templates are included for Mila and Nibi; for other DRAC clusters, add `default.<cluster>.sh`
  (see [Running on another cluster](#running-on-another-cluster)).
* The `<config>` uses `default` but may be overridden using `--config`.

```bash
chmod +x job.py
./job.py --dry-run                    # print the generated script, submit nothing
./job.py                              # submit a job with slurm/templates/default.<cluster>.sh
./job.py -c h100                      # use slurm/templates/h100.<cluster>.sh (included for Mila)
./job.py -- --lr 3e-4 --steps 10000   # pass through args to run "train.py --lr 3e-4 --steps 10000"
./job.py -s                           # run from a copy of the code, so later edits don't affect the queued job
./job.py -d 12345                     # start after job 12345 finishes, even if it failed (--dependency)
./job.py -f my-template.sh            # submit with a specific sbatch template file
```

Full flag list (`-C` is autodetected and the `-j`/`-f` defaults depend on where the repo lives and on `$SCRATCH`, so they vary by machine):

```
usage: job.py [-h] [-j JOBS_DIR] [-f TEMPLATE] [-C CLUSTER] [-c CONFIG]
              [-T TIME] [-d DEPENDENCY] [-s] [--dry-run]
              [extra_args ...]

Submit a job to SLURM.

positional arguments:
  extra_args            Arguments forwarded to script, e.g. `-- --lr 3e-4
                        --steps 10000` (default: None)

options:
  -h, --help            show this help message and exit
  -j, --jobs-dir JOBS_DIR
                        Directory for job logs and script snapshot (default:
                        $SCRATCH/slurm-launcher/jobs, or /path/to/slurm-
                        launcher/slurm/jobs without $SCRATCH)
  -f, --template TEMPLATE
                        Path to the sbatch template; {config} and {cluster}
                        are replaced automatically. (default: /path/to/slurm-
                        launcher/slurm/templates/{config}.{cluster}.sh)
  -C, --cluster CLUSTER
                        Override the cluster instead of using the autodetected
                        name (default: mila)
  -c, --config CONFIG   Selects the matching template file name via
                        <config>.<cluster>.sh (default: default)
  -T, --time TIME       The sbatch job time limit (HH:MM:SS) (default:
                        3:00:00)
  -d, --dependency DEPENDENCY
                        Schedule the job after the specified job ID finishes
                        (default: None)
  -s, --snapshot        Copy and run code from <jobs-dir>/<job_id>/code when
                        submitting (default: False)
  --dry-run             Print the generated script without submitting
                        (default: False)
```

## Jobs directory layout

```
$SCRATCH/<project-name>/jobs/
├── 1234567/            # ./job.py -s
│   ├── job.sh          # submitted script, plus git commit and command line
│   ├── stdout.txt
│   ├── stderr.txt
│   └── code/           # repo copy the job runs from (minus .gitignore'd, *.md, tests/)
└── 1234568/            # ./job.py (runs from the repo itself)
    ├── job.sh
    ├── stdout.txt
    └── stderr.txt
```

`<job_id>/` is renamed into place right after `sbatch` returns. If Slurm starts the job
before then, it fails immediately with no logs (unlikely in practice; just resubmit).

### Snapshots and virtual environments

Once the project has a `pyproject.toml`, `uv run` inside each `code/` copy creates its own
`.venv`, which can mean thousands of files per job, using quota. To avoid this, one venv may
be shared and rebuilt when the project changes. To do so, add the first four lines below to
the script `job.py` generates (in `main`, right after its `cd` line), and change its
`uv run` to `uv run --no-sync`:

```bash
venv="$SCRATCH/<project-name>/venvs/$(cat uv.lock .python-version | sha256sum | cut -c1-16)"
mkdir -p "$(dirname "$venv")"
export UV_PROJECT_ENVIRONMENT="$venv" UV_CACHE_DIR="$SCRATCH/<project-name>/uv-cache"
flock "$venv.lock" uv sync          # first job builds it; later jobs find it already up to date
uv run --no-sync train.py           # --no-sync: never modify the shared venv mid-run
```

## Running on another cluster

Autodetection only recognizes Mila and DRAC's national clusters. Anywhere else it falls
back to `unknown`, so edit `slurm/templates/default.unknown.sh` with your cluster's
configuration. For a detected DRAC cluster without a template (e.g. Narval), add
`slurm/templates/default.<cluster>.sh` instead.
