import subprocess
import tempfile
import os

def launch_antigravity(task_prompt, workspace_dir):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
        f.write(task_prompt)
        temp_path = f.name

    cmd = 'antigravity.cmd chat -m agent -r -'

    print("🔧 CMD:", cmd)

    with open(temp_path, "r", encoding="utf-8") as prompt_file:
        result = subprocess.run(
            cmd,
            cwd=workspace_dir,
            shell=True,
            stdin=prompt_file,
            capture_output=True,
            text=True,
            timeout=300
        )

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    print("Return Code:", result.returncode)

    os.unlink(temp_path)

    return result
