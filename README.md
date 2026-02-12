# Gaussian_UMA

**UMA features in Gaussian**

1. It requires three files.
2. The UMA run files are named `gauuma` and `gauumastart` [find them in the `gau_uma.zip`]. `gauuma` is used for the initial system setup and data processing, whereas `gauumastart` takes care of the actual UMA calculation on a GPU using the server-client mode.
   I placed uma scripts under `~/softwares/gau_uma`, and call it through the submission script whenever required.
4. The third one is a specialized submission script that can call UMA through FAIRCHEM, and initiate a server on a GPU. This script is called `rung16_uma`.
5. Attached is a sample Gaussian input file (), where `external=('gauuma')` is Gaussian's external call for UMA
6. Usage: `rung16_uma <n procs> <mem in GB> <Hrs>`


 


