# Gaussian_UMA

**Procedure to implement UMA features in Gaussian**

1. It requires three files.
2. The UMA run files are named `gauuma` and `gauumastart` [find them in the `gau_uma.zip`]. `gauuma` is used for the initial system setup and data processing, whereas `gauumastart` takes care of the actual UMA calculation on a GPU using the server-client mode.
   I placed uma scripts under `~/softwares/gau_uma`, and call it through the submission script whenever required.
4. The third one is a specialized submission script that can call UMA through FAIRCHEM, and initiate a server on a GPU. This script is called `rung16_uma`.
5. Attached is a sample Gaussian input file (), where `external=('gauuma')` is Gaussian's external call for UMA
6. Usage: `rung16_uma <n procs> <mem in GB> <Hrs>`

**Procedure to run MILO using UMA features through Gaussian**

1. We generated a script called `setup_ensemble-gau_uma.py` to generate a slurm submission script compatible with the UMA run in Milo. This will be very useful for the initial equilibration.

2. Since UMA doesn't have any charge information, it can only do Mechanical Embedding in ONIOM. Mechanical embedding is the default in Gaussian.
   [Use the keyword `ONIOM=EmbedCharge` in Gaussian to activate the effect of MM charges from the real system in the QM calculations on the model system.]

3. If mechanical embedding is okay for our purpose, we can even use UMA to run trajectories. After all, we are using solvents as a cage to trap the active species.
 


