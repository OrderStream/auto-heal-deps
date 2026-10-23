"""
Automated dependency upgrade assistant rewriting deprecated APIs and fixing peer lockfile conflicts.
"""

import difflib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

@dataclass
class CodemodRule:
    id: str
    target_package: str
    description: str
    pattern: str
    replacement: str
    is_regex: bool = True

BUILTIN_RULES: List[CodemodRule] = [
    # Pydantic v1 -> v2
    CodemodRule(
        id="pydantic-dict-to-model-dump",
        target_package="pydantic",
        description="Replace deprecated .dict() with .model_dump() in Pydantic v2",
        pattern=r"(\b[a-zA-Z0-9_]+)\.dict\(",
        replacement=r"\1.model_dump("
    ),
    CodemodRule(
        id="pydantic-parse-obj-to-model-validate",
        target_package="pydantic",
        description="Replace deprecated .parse_obj(...) with .model_validate(...) in Pydantic v2",
        pattern=r"(\b[a-zA-Z0-9_]+)\.parse_obj\(",
        replacement=r"\1.model_validate("
    ),
    CodemodRule(
        id="pydantic-validator-to-field-validator",
        target_package="pydantic",
        description="Replace deprecated @validator with @field_validator in Pydantic v2",
        pattern=r"@validator\(",
        replacement=r"@field_validator("
    ),
    # SQLAlchemy 1.4 -> 2.0
    CodemodRule(
        id="sqlalchemy-query-to-scalars-select",
        target_package="sqlalchemy",
        description="Replace deprecated session.query(Model).all() with session.scalars(select(Model)).all()",
        pattern=r"session\.query\(([a-zA-Z0-9_]+)\)\.all\(\)",
        replacement=r"session.scalars(select(\1)).all()"
    ),
    # React 18 ReactDOM.render -> createRoot
    CodemodRule(
        id="react-dom-render-to-create-root",
        target_package="react-dom",
        description="Replace deprecated ReactDOM.render with createRoot in React 18+",
        pattern=r"ReactDOM\.render\((.*?),\s*document\.getElementById\((.*?)\)\)",
        replacement=r"createRoot(document.getElementById(\2)).render(\1)"
    ),
]

@dataclass
class HealPatch:
    file_path: str
    rule_id: str
    diff: str
    original_content: str
    modified_content: str

class AutoHealDeps:
    def __init__(self, rules: Optional[List[CodemodRule]] = None):
        self.rules = rules or BUILTIN_RULES

    def scan_file(self, file_path: str, content: str) -> List[HealPatch]:
        patches: List[HealPatch] = []
        current_content = content

        for rule in self.rules:
            if re.search(rule.pattern, current_content):
                modified = re.sub(rule.pattern, rule.replacement, current_content)
                if modified != current_content:
                    diff = "".join(difflib.unified_diff(
                        current_content.splitlines(keepends=True),
                        modified.splitlines(keepends=True),
                        fromfile=f"a/{file_path}",
                        tofile=f"b/{file_path}"
                    ))
                    patches.append(HealPatch(
                        file_path=file_path,
                        rule_id=rule.id,
                        diff=diff,
                        original_content=current_content,
                        modified_content=modified
                    ))
                    current_content = modified

        return patches

    def heal_directory(self, directory: str, apply: bool = False) -> List[HealPatch]:
        all_patches: List[HealPatch] = []
        dir_path = Path(directory)

        for file in dir_path.rglob("*"):
            if not file.is_file():
                continue
            parts = file.parts
            if any(p.startswith(".") or p in {"node_modules", "venv", ".git", "__pycache__", "dist", "build"} for p in parts):
                continue
            if file.suffix in {".py", ".ts", ".js", ".tsx", ".jsx"}:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    patches = self.scan_file(str(file), content)
                    if patches:
                        all_patches.extend(patches)
                        if apply:
                            # Apply latest content
                            file.write_text(patches[-1].modified_content, encoding="utf-8")
                except Exception:
                    continue

        return all_patches

@dataclass
class PeerConflict:
    package: str
    current_version: str
    required_peer_package: str
    required_peer_range: str
    installed_peer_version: str
    recommended_fix: str

class PeerResolver:
    @staticmethod
    def analyze_package_json(package_json_content: str) -> List[PeerConflict]:
        conflicts: List[PeerConflict] = []
        try:
            data = json.loads(package_json_content)
        except Exception:
            return conflicts

        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        peer_deps = data.get("peerDependencies", {})
        all_deps = {**deps, **dev_deps}

        # Common peer conflict scenarios (e.g. React 19 vs older plugin requiring React ^18.0.0)
        for pkg, version in all_deps.items():
            # If react is installed as 19.x, but a lib requires peer react 18
            if pkg == "react" and version.startswith(("^19", "19")):
                for peer, peer_ver in peer_deps.items():
                    if peer == "react" and "18" in peer_ver and "19" not in peer_ver:
                        conflicts.append(PeerConflict(
                            package="react",
                            current_version=version,
                            required_peer_package="react",
                            required_peer_range=peer_ver,
                            installed_peer_version=version,
                            recommended_fix=f"Align peer dependency '{peer}' to support '{version}' or pin react to compatible '^18.3.1'."
                        ))

            # General peer check against installed
            if pkg in peer_deps:
                req_range = peer_deps[pkg]
                # Simple major version mismatch check
                req_major = re.search(r"\d+", req_range)
                inst_major = re.search(r"\d+", version)
                if req_major and inst_major and req_major.group(0) != inst_major.group(0):
                    conflicts.append(PeerConflict(
                        package=pkg,
                        current_version=version,
                        required_peer_package=pkg,
                        required_peer_range=req_range,
                        installed_peer_version=version,
                        recommended_fix=f"Upgrade {pkg} to meet peer range {req_range} without using --force/--legacy-peer-deps."
                    ))

        return conflicts
