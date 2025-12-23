# Gaussian_UMA

**Procedure to implement UMA features in Gaussian**

1. It requires two files named `gauuma` and `gauumastart`.
2. A specialized submission script that can call UMA through FAIRCHEM, and initiate a server on a GPU. This script is called `rung16_uma`

3. Also, we generated another script to run Milo using the UMA capabilities of Gaussian. This will be useful for the equilibration.
4. Since UMA doesn't have any charge information, it can only do Mechanical Embedding in ONIOM. Mechanical embedding is the default in Gaussian.
   Use the keyword `ONIOM=EmbedCharge` in Gaussian to activate the effect of MM charges from the real system in the QM calculations on the model system.

5. If mechanical embedding is okay for our purpose, we can even use UMA to run trajectories. After all we are using solvents as a cage to trap the active species.
6. 
7. 


