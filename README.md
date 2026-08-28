# slurm-launcher

Minimal SLURM job launcher. `job.py` submits `train.py` to SLURM.

```bash
chmod +x job.py
./job.py --dry-run                    # print the generated script, submit nothing
./job.py                              # submit for real (cluster autodetected, config=default)
./job.py -C nibi                      # pick the cluster explicitly
./job.py -c bigmem                    # pick a non-default config for that cluster
./job.py -- --lr 3e-4 --steps 10000   # forward arguments to train.py
./job.py -d 12345                     # hold until job 12345 finishes
./job.py -f slurm/templates/mila-default.sbatch   # submit with a specific template file
```

Run `./job.py --help` for the full flag list.

## Adding a cluster or config

Copy a file in `slurm/templates/`, edit the `#SBATCH` lines for the new
site/GPU, save it as `<cluster>-<config>.sbatch`. No code changes needed —
see `job.py` for how templates are resolved and filled in.

Currently bundled: `mila-default` (L40S), `nibi-default` (H100 MIG slice).
