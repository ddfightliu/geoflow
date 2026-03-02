# geoflow
本项目基础功能与vscode类似
项目gui仿照vscode

本项目包括两套gui
1.python+pyside6
2.bun+vue+fastapi，文本编辑器使用monaco-editor

本项目功能包括：
  构建工作区，目录结构如demo_workspace
  工作区的数据文件遵循geojson标准格式

## Web 开发（Python 后端 + Bun 前端）

本仓库包含一个基于 FastAPI 的 Python 后端和一个使用 Vue + Vite 的前端，前端推荐使用 Bun 作为运行时（比 Node 更快）。

快速开始（开发模式）：

1. 安装 Python 依赖：

```bash
python -m pip install -r requirements.txt
```

2. 安装 Bun 并为前端安装依赖（项目根目录）：

```bash
# 请参考 https://bun.sh 获取安装方式
cd geoflow/web/frontend
bun install
```

3. 同时启动后端和前端（在仓库根目录运行）：

```bash
python run_web.py
```

单独运行后端：

```bash
python run_geoflow_web.py
```

单独运行前端（在 `geoflow/web/frontend` 目录）：

```bash
bun run dev
```

更多部署或打包说明请在需要时提出，我可以帮你添加 Dockerfile、Procfile 或 CI 工作流。

## 仓库结构（整理后，前后端分离）

顶层目录现在包含两个方便的开发文件夹：

- `backend/` - FastAPI 应用（可直接通过 `uvicorn backend.main:app` 运行）
- `frontend/` - Vue + Vite 前端（`bun run dev` 在此目录下运行）
- `geoflow/` - 原有 Python 包和 PySide6 桌面实现（保留）

向后兼容：如果你还保留或使用旧的嵌套目录 `geoflow/web/frontend` 和 `geoflow/web/backend`，运行脚本会优先使用顶层 `frontend/` 和 `backend/`，找不到时会回退到旧位置。

如果你希望我把所有前端源代码从 `geoflow/web/frontend/src` 完全移动到顶层 `frontend/src`（并更新所有导入和配置），我可以在下一步进行完整迁移并运行简单的本地构建测试。
