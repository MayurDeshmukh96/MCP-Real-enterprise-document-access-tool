import subprocess

workspace_dir = r"d:\Mayur\Learning\MCP"
prompt = "This is a test prompt from the standalone script.\n"

cmd = ["antigravity.cmd", "chat", "-", "-m", "agent", "-r"]

print("Executing command:", cmd)

try:
    p = subprocess.Popen(
        cmd,
        cwd=workspace_dir,
        shell=True,   # Important for .cmd files on Windows
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    out, err = p.communicate(input=prompt, timeout=30)

    print("STDOUT:", out)
    print("STDERR:", err)
    print("Return code:", p.returncode)

except Exception as e:
    print("Exception:", e)