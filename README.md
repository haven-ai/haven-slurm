# haven-slurm

Modify `slurm_manager.py` and slightly `haven_jobs.py` to run the following scripts.

## Trainval without Slurm
```
{
            "name": "demo",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/trainval.py",
            "console": "integratedTerminal",
            "args":[
                "-sb", "/mnt/public/results/demo/debug",
                "-e", "group1", 
                "-d", "/mnt/public/datasets",
                "-r", "1",
                "-v", "results.ipynb"
        ],
        },
```

## Trainval with Slurm

```
{
            "name": "demo_slurm",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/trainval.py",
            "console": "integratedTerminal",
            "args":[
                "-sb", "/mnt/public/results/demo/slurm",
                "-d", "/mnt/public/datasets",
                "-e", "group1", 
                "-j", "1",
                "-r", "1"
        ],
        },
```