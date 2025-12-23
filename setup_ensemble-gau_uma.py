#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create multiple input files with different seeds to form an ensemble.

This script can setup input files in two ways:
- from a single input file, corresponding to only one direction, or
- from two input files, one forward and one backward.

The script will also create SLURM submission scripts, unless turned off with
the --no_script flag.
"""

import argparse
from random import randrange

# ---- UMA / Fairchem configuration (edit if your paths change) ----
UMA_DIR = "/home/fslcollab286/softwares/gau_uma"
FAIRCHEM_ENV = "$HOME/orca_6_1_0/orca-external-tools/fairchem/bin/activate"


def main():
    parser = argparse.ArgumentParser(
        description="Make Milo input files for an ensemble of trajectories."
    )

    parser.add_argument(
        "-n",
        "--number_trajectories",
        type=int,
        required=True,
        help="The number of trajectories to make input files for.",
    )
    parser.add_argument(
        "-f",
        "--forward",
        type=argparse.FileType("r"),
        required=True,
        help="A template input file for the forward direction.",
    )
    parser.add_argument(
        "-b",
        "--backward",
        type=argparse.FileType("r"),
        default=None,
        help="A template input file for the backward direction.",
    )
    parser.add_argument(
        "-t",
        "--time",
        default="time_placeholder",
        help="Amount of time the submission script should request for forward "
        "trajectoryies, formatted as HH:MM:SS.",
    )
    parser.add_argument(
        "--time_backward",
        default=None,
        help="Amount of time the submission script should request for backward "
        "trajectories, formatted as HH:MM:SS. If not provided, defaults to same "
        "time as forward trajectories.",
    )
    parser.add_argument(
        "--no_script",
        action="store_true",
        help="Stops submission scripts from being output.",
    )

    args = parser.parse_args()

    gaussian_string = "g16"

    forward_template = []
    in_job_section = False
    random_seed_set = False
    forward_memory = "memory_placeholder"
    forward_procs = "processors_placeholder"

    for line in args.forward:
        if "$job" in line.casefold():
            in_job_section = True
        elif in_job_section and "$end" in line.casefold():
            in_job_section = False
            if not random_seed_set:
                forward_template.append(" random_seed random_seed_placeholder\n")
                random_seed_set = True
        elif in_job_section and "random_seed" in line.casefold():
            line = " random_seed random_seed_placeholder\n"
            random_seed_set = True
        elif in_job_section and "memory" in line.casefold():
            forward_memory = int(line.split()[1]) + 1
        elif in_job_section and "processors" in line.casefold():
            forward_procs = int(line.split()[1])
        elif in_job_section and "program" in line.casefold() and "gaussian09" in line.casefold():
            gaussian_string = "g09"

        forward_template.append(line)

    if not args.no_script and forward_memory == "memory_placeholder":
        print(
            "Warning: Could not find memory specification in forward template file. "
            "Replace 'memory_placeholder' in submission script before submitting jobs."
        )

    if not args.no_script and forward_procs == "processors_placeholder":
        print(
            "Warning: Could not find processors specification in forward template file. "
            "Replace 'processors_placeholder' in submission script before submitting jobs."
        )

    backward_template = None
    backward_memory = None
    backward_procs = None

    if args.backward is not None:
        backward_template = []
        in_job_section = False
        random_seed_set = False
        backward_memory = "memory_placeholder"
        backward_procs = "processors_placeholder"

        for line in args.backward:
            if "$job" in line.casefold():
                in_job_section = True
            elif in_job_section and "$end" in line.casefold():
                in_job_section = False
                if not random_seed_set:
                    backward_template.append(" random_seed random_seed_placeholder\n")
                    random_seed_set = True
            elif in_job_section and "random_seed" in line.casefold():
                line = " random_seed random_seed_placeholder\n"
                random_seed_set = True
            elif in_job_section and "memory" in line.casefold():
                backward_memory = int(line.split()[1]) + 1
            elif in_job_section and "processors" in line.casefold():
                backward_procs = int(line.split()[1])

            backward_template.append(line)

        if not args.no_script and backward_memory == "memory_placeholder":
            print(
                "Warning: Could not find memory specification in backward template file. "
                "Replace 'memory_placeholder' in submission script before submitting jobs."
            )

        if not args.no_script and backward_procs == "processors_placeholder":
            print(
                "Warning: Could not find processors specification in backward template file. "
                "Replace 'processors_placeholder' in submission script before submitting jobs."
            )

    if not args.no_script and args.time == "time_placeholder":
        print(
            "Warning: Time not specified. Replace 'time_placeholder' in submission script "
            "before submitting jobs."
        )

    input_file_basename = args.forward.name.split(".")[0]
    input_file_basename_bwd = args.backward.name.split(".")[0] if args.backward is not None else None

    for _ in range(args.number_trajectories):
        random_seed = randrange(10000000000, 99999999999)

        if args.backward is not None:
            forward_name = f"{input_file_basename}_{random_seed}_fwd.in"
            make_input_file(forward_name, forward_template, random_seed)

            backward_name = f"{input_file_basename_bwd}_{random_seed}_bwd.in"
            make_input_file(backward_name, backward_template, random_seed)

            if not args.no_script:
                make_submission_script(
                    forward_name.replace(".in", ".sh"),
                    args.time,
                    forward_memory,
                    forward_procs,
                    gaussian_string,
                )
                make_submission_script(
                    backward_name.replace(".in", ".sh"),
                    args.time_backward if args.time_backward is not None else args.time,
                    backward_memory,
                    backward_procs,
                    gaussian_string,
                )
        else:
            name = f"{input_file_basename}_{random_seed}.in"
            make_input_file(name, forward_template, random_seed)

            if not args.no_script:
                make_submission_script(
                    name.replace(".in", ".sh"),
                    args.time,
                    forward_memory,
                    forward_procs,
                    gaussian_string,
                )


def make_input_file(file_name, template, random_seed):
    """Make an input file that matches, but with the seed switched."""
    with open(file_name, "w") as file:
        for line in template:
            if "random_seed_placeholder" in line:
                line = line.replace("random_seed_placeholder", str(random_seed))
            file.write(line)


def make_submission_script(file_name, time_string, memory, procs, gaussian_string):
    """Make a submission script given filename and time/job parameters."""
    jobname = file_name.split(".")[0]

    with open(file_name, "w") as file:
        file.write("#!/bin/bash\n")
        file.write(f"#SBATCH --nodes=1 --ntasks=1 --cpus-per-task={procs}\n")
        file.write(f"#SBATCH --mem={memory}G\n")
        file.write(f"#SBATCH -t {time_string}\n")
        file.write("#SBATCH --gpus=1\n")
        file.write('#SBATCH -C "rhel7&avx2"\n')
        file.write("#SBATCH --mail-user=jyothish@byu.edu\n")
        file.write("#SBATCH --mail-type=END\n")
        file.write("#SBATCH --mail-type=FAIL\n")
        file.write(f"#SBATCH --job-name={jobname}\n")
        file.write("##SBATCH --partition=m12,m8,m8n,m9,m11\n")
        file.write("\n")

        file.write(
            "[ `cat /proc/cpuinfo | grep -m 1 vendor_id | awk '{print $3}'` == 'AuthenticAMD' ] "
            "&& export PGI_FASTMATH_CPU=haswell\n"
        )
        file.write("\n")

        file.write("echo start time: `date`\n")
        file.write("echo node: `hostname`\n")
        file.write("echo job id: $SLURM_JOB_ID\n")
        file.write("echo assigned to nodes:\n")
        file.write('scontrol show hostnames "$SLURM_NODELIST"\n')
        file.write("echo submitted from: $SLURM_SUBMIT_DIR\n")
        file.write("\n")

        file.write("export TEMPORARY_DIR=/tmp/$USER/$SLURM_JOB_ID\n")
        file.write('echo temp dir: "$TEMPORARY_DIR"\n')
        file.write('mkdir -p "$TEMPORARY_DIR"\n')
        file.write('cp *.chk "$TEMPORARY_DIR" 2>/dev/null || true\n')
        file.write('cd "$TEMPORARY_DIR"\n')
        file.write("\n")

        file.write('MILO_PYTHON=$(command -v python)\n')
        file.write("\n")

        file.write('UMASERVER_PID=""\n')
        file.write("stop_uma() {\n")
        file.write('  if [ -n "$UMASERVER_PID" ]; then\n')
        file.write('    kill "$UMASERVER_PID" 2>/dev/null\n')
        file.write('    wait "$UMASERVER_PID" 2>/dev/null\n')
        file.write('    UMASERVER_PID=""\n')
        file.write("  fi\n")
        file.write("}\n")
        file.write("\n")

        file.write("function cleanup {\n")
        file.write(' echo "---"\n')
        file.write(' echo "Starting clean up"\n')
        file.write(" stop_uma\n")
        file.write(' for f in "$TEMPORARY_DIR"/*.{out,xyz,txt}; do\n')
        file.write("  [ -e $f ] || continue\n")
        file.write('  cp -vp $f "$SLURM_SUBMIT_DIR"\n')
        file.write(" done\n")
        file.write("\n")
        file.write(' mkdir -p "$SLURM_SUBMIT_DIR/com_log_files"\n')
        file.write(' echo "Archiving .com and .log files"\n')
        file.write(" tar -cf ${SLURM_JOB_NAME}_${SLURM_JOB_ID}.tar *.{com,log,chk} 2>/dev/null || true\n")
        file.write(' cp -v ${SLURM_JOB_NAME}_${SLURM_JOB_ID}.tar "$SLURM_SUBMIT_DIR/com_log_files" 2>/dev/null || true\n')
        file.write("\n")
        file.write(' cd "$SLURM_SUBMIT_DIR"\n')
        file.write(' rm -fr "$TEMPORARY_DIR"\n')
        file.write(' echo "clean up finished at `date`"\n')
        file.write("}\n")
        file.write("\n")

        file.write("export PGI_FASTMATH_CPU=haswell\n")
        file.write("module purge\n")
        file.write(f"module load {gaussian_string}\n")
        file.write("\n")

        file.write(f'UMA_DIR="{UMA_DIR}"\n')
        file.write(f'FAIRCHEM_ENV="{FAIRCHEM_ENV}"\n')
        file.write("\n")

        file.write("# Activate fairchem, but do NOT use its python for Milo\n")
        file.write('source "$FAIRCHEM_ENV"\n')
        file.write('FAIRCHEM_PYTHON=$(command -v python)\n')
        file.write('export PATH="$PATH:$UMA_DIR"\n')
        file.write("export HF_HUB_OFFLINE=1\n")
        file.write("export TRANSFORMERS_OFFLINE=1\n")
        file.write("export HF_DATASETS_OFFLINE=1\n")
        file.write("export HF_HUB_DISABLE_SYMLINKS_WARNING=1\n")
        file.write("\n")

        file.write("pick_port() {\n")
        file.write("python - << 'PY'\n")
        file.write("import random\n")
        file.write("print(random.randint(20000, 59999))\n")
        file.write("PY\n")
        file.write("}\n")
        file.write("\n")

        file.write("UMA_LOG=uma_server.log\n")
        file.write("MAX_TRIES=10\n")
        file.write("TRY=0\n")
        file.write("while true; do\n")
        file.write("  TRY=$((TRY+1))\n")
        file.write("  export UMA_PORT=$(pick_port)\n")
        file.write('  echo "Starting UMA server on port $UMA_PORT (try $TRY/$MAX_TRIES)..."\n')
        file.write('  : > "$UMA_LOG"\n')
        file.write('  "$FAIRCHEM_PYTHON" "$UMA_DIR/gauumastart" > "$UMA_LOG" 2>&1 &\n')
        file.write("  UMASERVER_PID=$!\n")
        file.write("\n")
        file.write("  TIMEOUT=60\n")
        file.write("  ready=0\n")
        file.write("  for i in $(seq 1 $TIMEOUT); do\n")
        file.write('    if grep -q "Listening on port" "$UMA_LOG"; then\n')
        file.write("      ready=1\n")
        file.write("      break\n")
        file.write("    fi\n")
        file.write('    if ! kill -0 "$UMASERVER_PID" 2>/dev/null; then\n')
        file.write("      break\n")
        file.write("    fi\n")
        file.write("    sleep 1\n")
        file.write("  done\n")
        file.write("\n")
        file.write('  if [ "$ready" -eq 1 ]; then\n')
        file.write('    echo "UMA server ready on port $UMA_PORT"\n')
        file.write("    break\n")
        file.write("  fi\n")
        file.write("\n")
        file.write('  echo "UMA server failed on port $UMA_PORT. Log:"\n')
        file.write('  cat "$UMA_LOG"\n')
        file.write("  stop_uma\n")
        file.write("\n")
        file.write('  if [ "$TRY" -ge "$MAX_TRIES" ]; then\n')
        file.write('    echo "Giving up after $MAX_TRIES attempts."\n')
        file.write("    exit 1\n")
        file.write("  fi\n")
        file.write("done\n")
        file.write("\n")

        file.write(
            f'"$MILO_PYTHON" -m milo "$SLURM_SUBMIT_DIR/$SLURM_JOB_NAME.in" '
            f'-e {gaussian_string} > "$SLURM_SUBMIT_DIR/${{SLURM_JOB_NAME}}.out" &\n'
        )
        file.write("pid=$!\n")
        file.write("\n")

        file.write('trap "stop_uma; kill $pid 2>/dev/null; cleanup; exit 1" TERM SIGTERM\n')
        file.write("\n")

        file.write("wait $pid\n")
        file.write("milo_status=$?\n")
        file.write("stop_uma\n")
        file.write("cleanup\n")
        file.write("exit $milo_status\n")
        file.write("\n")


if __name__ == "__main__":
    main()

