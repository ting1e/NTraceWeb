# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import AsyncGenerator
import asyncio
import subprocess
import os

app = FastAPI()

# 挂载静态文件目录，用于提供HTML、CSS、JS等文件
# 请确保在与 main.py 相同的目录下创建一个名为 "static" 的文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置 Jinja2 模板，用于渲染HTML文件
# 请确保在与 main.py 相同的目录下创建一个名为 "templates" 的文件夹
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    根路径，渲染前端HTML页面。
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/execute")
async def execute_command(
    ip_address: str = Form(...),
    protocol: str = Form(...),
    ip_version: str = Form(...) # 新增 IP 版本参数
):
    """
    执行命令行命令并实时流式传输输出。
    现在支持 nexttrace 命令，并根据 IP 版本和协议类型传递参数。
    """
    # nexttrace 命令的完整路径
    # 请根据您的实际路径进行修改
    nexttrace_command_path = "./ntrace"

    # 检查 nexttrace 可执行文件是否存在
    if not os.path.exists(nexttrace_command_path):
        return StreamingResponse(
            content=async_generator(f"错误: nexttrace 可执行文件 '{nexttrace_command_path}' 未找到。请检查路径是否正确。\n\n"),
            media_type="text/event-stream"
        )
    
    # 检查文件是否可执行 (在Linux/macOS上很重要)
    if not os.access(nexttrace_command_path, os.X_OK):
        return StreamingResponse(
            content=async_generator(f"错误: nexttrace 可执行文件 '{nexttrace_command_path}' 没有执行权限。请使用 'chmod +x {nexttrace_command_path}' 赋予权限。\n\n"),
            media_type="text/event-stream"
        )


    # command = [nexttrace_command_path,'-M','-d','IPInfo']
    command = [nexttrace_command_path,'-M']

    # 根据 IP 版本添加参数
    if ip_version == "ipv4":
        command.append("-4")
    elif ip_version == "ipv6":
        command.append("-6")

    # 根据协议添加参数
    if protocol == "tcp":
        command.append("-T")
    

    # 最后添加 IP 地址
    command.append(ip_address)

    async def async_generator(text: str) -> AsyncGenerator[str, None]:
        """
        一个异步生成器，用于将文本作为 SSE 事件发送。
        """
        yield f"data: {text}\n\n"

    async def stream_command_output() -> AsyncGenerator[str, None]:
        """
        异步执行命令行命令并实时读取其输出，然后作为 SSE 事件发送。
        """
        process = None
        try:
            # 打印将要执行的完整命令，便于调试
            yield f"data: 正在执行命令: {' '.join(command)}\n\n"

            # 启动子进程，捕获其标准输出和标准错误
            # 注意：如果 nexttrace_linux_amd64 需要在 WSL 环境下运行，
            # 并且 FastAPI 是在 Windows 原生环境运行，可能需要调整命令路径或执行方式。
            # 这里假设 nexttrace_linux_amd64 在 FastAPI 运行的系统环境中是可执行的。
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 实时读取标准输出
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                yield f"data: {line.decode('utf-8', errors='ignore').strip()}\n\n" # 尝试utf-8解码，忽略错误

            # 读取标准错误（如果有的话）
            stderr_output = await process.stderr.read()
            if stderr_output:
                yield f"data: 错误: {stderr_output.decode('utf-8', errors='ignore').strip()}\n\n"

            # 等待进程结束并获取返回码
            await process.wait()
            yield f"data: 命令执行完成，返回码: {process.returncode}\n\n"

        except FileNotFoundError:
            # 如果命令不存在
            yield f"data: 错误: 命令 '{command[0]}' 未找到。请确保它已安装或路径正确。\n\n"
        except Exception as e:
            # 捕获其他可能的异常
            yield f"data: 发生错误: {str(e)}\n\n"
        finally:
            if process and process.returncode is None:
                # 如果进程仍在运行，则终止它
                process.terminate()
                await process.wait()

    # 返回 StreamingResponse，媒体类型设置为 text/event-stream (SSE)
    return StreamingResponse(stream_command_output(), media_type="text/event-stream")


