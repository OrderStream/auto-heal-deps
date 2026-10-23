"""
Command line interface for auto-heal-deps.
"""

import argparse
import sys
from pathlib import Path
from auto_heal_deps.core import AutoHealDeps, PeerResolver
from auto_heal_deps.monetization import LicenseManager

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="auto-heal-deps",
        description="Automated dependency upgrade assistant rewriting deprecated API calls and fixing lockfile peer conflicts"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan code for deprecated API calls requiring upgrades")
    scan_parser.add_argument("--path", default=".", help="Directory path to scan")
    scan_parser.add_argument("--license-key", default=None, help="OrderStream license key")

    # fix command
    fix_parser = subparsers.add_parser("fix", help="Automatically rewrite deprecated API calls to match modern versions")
    fix_parser.add_argument("--path", default=".", help="Directory path to fix")
    fix_parser.add_argument("--dry-run", action="store_true", default=False, help="Show diff without applying changes")
    fix_parser.add_argument("--license-key", default=None, help="OrderStream license key")

    # resolve-peers command
    peer_parser = subparsers.add_parser("resolve-peers", help="Scan package.json for peer dependency conflicts")
    peer_parser.add_argument("--file", default="package.json", help="Path to package.json")

    # license / donate command
    subparsers.add_parser("license", help="View license tier and 0% fee crypto donation wallets")

    args = parser.parse_args(argv)

    if not args.command or args.command == "license":
        print(LicenseManager.get_banner("auto-heal-deps"))
        tier = LicenseManager.get_tier(getattr(args, "license_key", None))
        print(f"Active Tier: {tier['name']} ({tier['tier']})")
        print(f"Features: {', '.join(tier['features'])}")
        print(LicenseManager.get_remediation_footer())
        return 0

    if args.command in {"scan", "fix"}:
        print(LicenseManager.get_banner("auto-heal-deps"))
        engine = AutoHealDeps()
        is_apply = (args.command == "fix" and not args.dry_run)
        patches = engine.heal_directory(args.path, apply=is_apply)

        print(f"[AUTO-HEAL-DEPS] Scanned directory: {args.path}")
        print(f"[AUTO-HEAL-DEPS] Total Deprecated Call Sites Found: {len(patches)}")

        for p in patches:
            print(f"\n⚡ Rule Applied: {p.rule_id} on {p.file_path}")
            print(p.diff)

        if is_apply:
            print(f"\n✅ [AUTO-HEAL-DEPS] Successfully rewritten {len(patches)} file(s) in-place!")
        elif patches:
            print(f"\n💡 Run 'auto-heal-deps fix --path {args.path}' to apply these codemods.")

        print(LicenseManager.get_remediation_footer())
        return 0

    elif args.command == "resolve-peers":
        print(LicenseManager.get_banner("auto-heal-deps"))
        p = Path(args.file)
        if not p.exists():
            print(f"Error: {args.file} not found.")
            return 1
        conflicts = PeerResolver.analyze_package_json(p.read_text(encoding="utf-8"))
        print(f"[AUTO-HEAL-DEPS] Peer Conflicts Found: {len(conflicts)}")
        for c in conflicts:
            print(f"  ❌ Conflict in {c.package} (installed: {c.current_version})")
            print(f"     Requires peer {c.required_peer_package} matching {c.required_peer_range}")
            print(f"     👉 Fix: {c.recommended_fix}")
        print(LicenseManager.get_remediation_footer())
        return 0 if not conflicts else 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
