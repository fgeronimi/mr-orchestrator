"""CLI `mro`. Squelette : chaque commande sera livrée par un ticket du MVP."""

import argparse
import sys

PLANNED = {
    "labels": "synchroniser les labels dans les repos (mro labels sync)",
    "sync": "synchroniser les issues GitHub vers le board",
    "board": "lancer le Kanban web",
    "start": "lancer un agent dans un workspace cmux (mro start 12 --role dev)",
    "approve": "approuver une validation (mro approve 12)",
    "reject": "rejeter une validation (mro reject 12 \"raison\")",
    "run": "gérer un run de rejeu (mro run new|close|purge)",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mro", description="MrOrchestrator")
    sub = parser.add_subparsers(dest="command", metavar="<commande>")
    for name, help_text in PLANNED.items():
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("args", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    if ns.command is None:
        parser.print_help()
        return 0
    print(f"mro {ns.command} : pas encore implémenté (voir docs/brief.md).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
