from fastmcp import FastMCP
import subprocess
import shlex

mcp = FastMCP("ecs-workbench")
INSTANCE_ID = "i-j6ciovehigtrrlo4uliy"
CONNECT_CMD = ["workbench", "connect", "--instance-id", INSTANCE_ID]

def run_wb_cmd(cmd: list[str], timeout=30):
    """调用workbench执行远端命令"""
    full = CONNECT_CMD + ["--exec", " ".join(shlex.quote(x) for x in cmd)]
    try:
        res = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
        return {"stdout": res.stdout, "stderr": res.stderr, "returncode": res.returncode}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "timeout", "returncode": -1}

@mcp.tool()
def read_remote_file(path: str) -> str:
    """读取阿里云ECS远端文件
    Args:
        path: 服务器上文件绝对路径，例如 /root/alpha_engine/main.py
    """
    ret = run_wb_cmd(["cat", path])
    if ret["returncode"] != 0:
        return f"读取失败：{ret['stderr']}"
    return ret["stdout"]

@mcp.tool()
def write_remote_file(path: str, content: str) -> str:
    """写入/覆盖远端文件
    Args:
        path: 服务器文件绝对路径
        content: 要写入的全部文本
    """
    cmd = ["tee", path]
    p = subprocess.Popen(CONNECT_CMD + ["--exec", " ".join(cmd)], stdin=subprocess.PIPE, capture_output=True, text=True)
    stdout, stderr = p.communicate(input=content, timeout=30)
    if p.returncode != 0:
        return f"写入失败：{stderr}"
    return "写入成功"

@mcp.tool()
def run_shell(cmd: str) -> str:
    """在远端服务器执行shell命令，危险命令会提示你确认
    Args:
        cmd: shell命令字符串
    """
    danger_keywords = ["rm ", "dd ", "mkfs", "reboot", "halt"]
    if any(k in cmd for k in danger_keywords):
        return f"⚠️高危命令，请手动确认后自己在终端执行：\n{cmd}"
    ret = run_wb_cmd(["bash", "-c", cmd])
    out = f"returncode:{ret['returncode']}\nstdout:\n{ret['stdout']}\nstderr:\n{ret['stderr']}"
    return out

@mcp.tool()
def upload_file(local_path: str, remote_path: str, force: bool = False) -> str:
    """上传本地文件到阿里云ECS远端（经OSS中转）
    Args:
        local_path: 本地文件绝对路径，例如 D:/data/model.bin
        remote_path: 远端目标路径，可以是目录（如 /opt/app/）或完整文件路径（如 /opt/app/app.jar）
        force: 是否强制覆盖远端已存在的同名文件
    """
    cmd = ["workbench", "upload", local_path, remote_path, "--instance-id", INSTANCE_ID]
    if force:
        cmd.append("-f")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "上传超时（大文件可能耗时较长）"
    if res.returncode != 0:
        return f"上传失败：{res.stderr}"
    return f"上传成功：{local_path} -> {remote_path}"

@mcp.tool()
def download_file(remote_path: str, local_path: str = "", force: bool = False) -> str:
    """从阿里云ECS远端下载文件到本地（经OSS中转）
    Args:
        remote_path: 服务器上文件绝对路径，例如 /var/log/app.log
        local_path: 本地保存路径（目录或文件路径）；留空则保存到当前目录
        force: 是否强制覆盖本地已存在的同名文件
    """
    cmd = ["workbench", "download", remote_path, "--instance-id", INSTANCE_ID]
    if local_path:
        cmd.append(local_path)
    if force:
        cmd.append("-f")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "下载超时（大文件可能耗时较长）"
    if res.returncode != 0:
        return f"下载失败：{res.stderr}"
    return f"下载成功：{remote_path} -> {local_path or '当前目录'}"

if __name__ == "__main__":
    mcp.run()
