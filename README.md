# Gaussian_UMA

**UMA features in Gaussian**

1.  It requires three files.
2.  The UMA run files are named `gauuma` and `gauumastart` [find them in `gau_uma.zip`]. `gauuma` is used for the initial system setup and data processing, while `gauumastart` performs the actual UMA calculation on a GPU using the server-client mode. I placed the UMA scripts under `~/softwares/gau_uma`, and call them through the submission script when needed.
3.  The third file is a specialized submission script that calls UMA through FAIRCHEM and initiates a server on a GPU. This script is called `rung16_uma`.
4.  Attached is a sample Gaussian input file, where `external=('gauuma')` is Gaussian's external call for UMA.
5.  Usage: `rung16_uma <n procs> <mem in GB> <Hrs>`


 


