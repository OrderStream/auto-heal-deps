"""
Unit and integration tests for auto-heal-deps.
"""

import json
import pytest
from pathlib import Path
from auto_heal_deps.core import AutoHealDeps, PeerResolver, CodemodRule
from auto_heal_deps.monetization import LicenseManager
from auto_heal_deps.cli import main

def test_license_manager():
    comm = LicenseManager.get_tier(None)
    assert comm["tier"] == "community"

    ent = LicenseManager.get_tier("ord_ent_autoheal")
    assert ent["tier"] == "enterprise"

    banner = LicenseManager.get_banner("auto-heal-deps")
    assert "GABFQIK63R2NETJM7T673EAMZN4RJLLGP3OFUEJU5ZVTGWUKULZJNL6" in banner

def test_pydantic_v2_codemods(tmp_path):
    engine = AutoHealDeps()
    code = """
from pydantic import BaseModel, validator

class User(BaseModel):
    name: str

    @validator('name')
    def validate_name(cls, v):
        return v

user = User.parse_obj({'name': 'Alice'})
data = user.dict()
"""
    f = tmp_path / "model.py"
    f.write_text(code, encoding="utf-8")

    patches = engine.heal_directory(str(tmp_path), apply=True)
    assert len(patches) >= 3

    updated = f.read_text(encoding="utf-8")
    assert ".model_dump()" in updated
    assert ".model_validate(" in updated
    assert "@field_validator(" in updated
    assert ".dict()" not in updated

def test_sqlalchemy_codemods(tmp_path):
    engine = AutoHealDeps()
    code = "rows = session.query(User).all()\n"
    f = tmp_path / "db.py"
    f.write_text(code, encoding="utf-8")

    patches = engine.heal_directory(str(tmp_path), apply=True)
    assert len(patches) == 1
    updated = f.read_text(encoding="utf-8")
    assert "session.scalars(select(User)).all()" in updated

def test_peer_conflict_resolver():
    package_json = """
{
  "name": "my-app",
  "dependencies": {
    "react": "^19.0.0"
  },
  "peerDependencies": {
    "react": "^18.2.0"
  }
}
"""
    conflicts = PeerResolver.analyze_package_json(package_json)
    assert len(conflicts) > 0
    assert conflicts[0].package == "react"

def test_cli_execution(tmp_path):
    f = tmp_path / "sample.py"
    f.write_text("item.dict()\n", encoding="utf-8")

    # scan dry-run
    exit_scan = main(["scan", "--path", str(tmp_path)])
    assert exit_scan == 0

    # fix
    exit_fix = main(["fix", "--path", str(tmp_path)])
    assert exit_fix == 0
    assert "item.model_dump()" in f.read_text(encoding="utf-8")

    # license
    exit_lic = main(["license"])
    assert exit_lic == 0
