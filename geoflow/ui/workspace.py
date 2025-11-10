"""
Workspace state management.

This module contains classes for managing the application's workspace state,
including loading and saving session data.
"""

import json
from pathlib import Path
from typing import Any, Dict


class WorkspaceState:
    def __init__(self, project_path: Path | None = None):
        if project_path is None:
            project_path = Path.cwd()
        self.project_path = project_path
        self.path = project_path / 'workspace.json'
        self.state: Dict[str, Any] = {
            'open_views': [],
            'layout': {},
            'last_opened': None,
        }

    def load(self) -> bool:
        if not self.path.exists():
            return False
        try:
            raw = self.path.read_text(encoding='utf8')
            # allow comments in JSON (// line comments and /* block comments */)
            try:
                text = _strip_json_comments(raw)
            except Exception:
                text = raw
            self.state = json.loads(text)
            return True
        except Exception as e:
            print('Failed to load workspace state:', e)
            return False

    def save(self) -> bool:
        try:
            header = ''
            # if user set a top-level _comment string, render it as // comment lines
            c = self.state.get('_comment')
            if isinstance(c, str) and c.strip():
                for ln in c.splitlines():
                    header += f'// {ln}\n'

            tmp = self.path.with_suffix('.tmp')
            with open(tmp, 'w', encoding='utf8') as f:
                if header:
                    f.write(header)
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            tmp.replace(self.path)
            return True
        except Exception as e:
            print('Failed to save workspace state:', e)
            return False


def _strip_json_comments(s: str) -> str:
    """Strip C/C++ style // line comments and /* ... */ block comments.

    This is a best-effort approach intended for hand-authored comments in
    workspace files. It uses regex and may not be 100% safe for pathological
    inputs (e.g. comment markers inside JSON strings), but is sufficient for
    typical use.
    """
    import re

    # remove block comments
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    # remove line comments
    s = re.sub(r'//.*$', '', s, flags=re.M)
    return s
