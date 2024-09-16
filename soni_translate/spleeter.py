import subprocess
import os


def run_spleeter(input_file, output_dir):
    # Get the path to the conda executable
    conda_path = os.path.join(
        os.path.dirname(os.path.dirname(os.environ["CONDA_EXE"])), "condabin", "conda"
    )

    # Construct the command (exc_path run -n env_name command)
    command = f"{conda_path} run -n spleeter spleeter separate -p spleeter:2stems -o {output_dir} {input_file}"

    # Run the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error running Spleeter: {result.stderr}")
    else:
        print(f"Spleeter output: {result.stdout}")


# Use the function
# run_spleeter("./audio.wav", "./spleeter/")
