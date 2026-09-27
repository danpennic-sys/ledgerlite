#!/usr/bin/env python3
"""
LedgerLite — lightweight invoice generator by Operator Pages.
Generate professional invoices from YAML/JSON or CLI flags.
License: proprietary commercial (see LICENSE).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


TWOPLACES = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


@dataclass
class LineItem:
    description: str
    qty: Decimal
    unit_price: Decimal
    tax_rate: Decimal = Decimal("0")

    @property
    def subtotal(self) -> Decimal:
        return money(self.qty * self.unit_price)

    @property
    def tax(self) -> Decimal:
        return money(self.subtotal * self.tax_rate)

    @property
    def total(self) -> Decimal:
        return money(self.subtotal + self.tax)


@dataclass
class Invoice:
    number: str
    issued: date
    due: date
    seller_name: str
    seller_email: str
    seller_address: str
    buyer_name: str
    buyer_email: str
    buyer_address: str
    currency: str = "USD"
    notes: str = "Thank you for your business."
    items: list[LineItem] = field(default_factory=list)

    @property
    def subtotal(self) -> Decimal:
        return money(sum((i.subtotal for i in self.items), Decimal("0")))

    @property
    def tax(self) -> Decimal:
        return money(sum((i.tax for i in self.items), Decimal("0")))

    @property
    def total(self) -> Decimal:
        return money(self.subtotal + self.tax)

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "issued": self.issued.isoformat(),
            "due": self.due.isoformat(),
            "seller": {
                "name": self.seller_name,
                "email": self.seller_email,
                "address": self.seller_address,
            },
            "buyer": {
                "name": self.buyer_name,
                "email": self.buyer_email,
                "address": self.buyer_address,
            },
            "currency": self.currency,
            "notes": self.notes,
            "items": [
                {
                    "description": i.description,
                    "qty": float(i.qty),
                    "unit_price": float(i.unit_price),
                    "tax_rate": float(i.tax_rate),
                    "subtotal": float(i.subtotal),
                    "tax": float(i.tax),
                    "total": float(i.total),
                }
                for i in self.items
            ],
            "subtotal": float(self.subtotal),
            "tax": float(self.tax),
            "total": float(self.total),
        }


def load_from_json(path: Path) -> Invoice:
    data = json.loads(path.read_text())
    items = [
        LineItem(
            description=row["description"],
            qty=money(row.get("qty", 1)),
            unit_price=money(row["unit_price"]),
            tax_rate=Decimal(str(row.get("tax_rate", 0))),
        )
        for row in data["items"]
    ]
    issued = date.fromisoformat(data.get("issued", date.today().isoformat()))
    due_days = int(data.get("due_days", 14))
    due = date.fromisoformat(data["due"]) if "due" in data else issued + timedelta(days=due_days)
    s, b = data["seller"], data["buyer"]
    return Invoice(
        number=data["number"],
        issued=issued,
        due=due,
        seller_name=s["name"],
        seller_email=s["email"],
        seller_address=s["address"],
        buyer_name=b["name"],
        buyer_email=b["email"],
        buyer_address=b["address"],
        currency=data.get("currency", "USD"),
        notes=data.get("notes", "Thank you for your business."),
        items=items,
    )


def render_text(inv: Invoice) -> str:
    lines = [
        "LEDGERLITE INVOICE",
        f"Invoice #{inv.number}",
        f"Issued: {inv.issued.isoformat()}    Due: {inv.due.isoformat()}",
        "",
        f"From: {inv.seller_name}  <{inv.seller_email}>",
        f"      {inv.seller_address}",
        f"To:   {inv.buyer_name}  <{inv.buyer_email}>",
        f"      {inv.buyer_address}",
        "",
        f"{'Description':40} {'Qty':>8} {'Unit':>12} {'Tax':>10} {'Total':>12}",
        "-" * 86,
    ]
    for i in inv.items:
        lines.append(
            f"{i.description[:40]:40} {i.qty:>8} {i.unit_price:>12} {i.tax:>10} {i.total:>12}"
        )
    lines += [
        "-" * 86,
        f"{'Subtotal':>72} {inv.subtotal:>12}",
        f"{'Tax':>72} {inv.tax:>12}",
        f"{'TOTAL ' + inv.currency:>72} {inv.total:>12}",
        "",
        inv.notes,
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="ledgerlite", description="Generate invoices from JSON or CSV.")
    p.add_argument("--json", type=Path, help="Invoice JSON file")
    p.add_argument("--out", type=Path, help="Write text invoice to this path")
    p.add_argument("--dump-json", type=Path, help="Write computed invoice JSON")
    args = p.parse_args(argv)

    if not args.json:
        p.print_help()
        return 2

    inv = load_from_json(args.json)
    text = render_text(inv)
    if args.out:
        args.out.write_text(text + "\n")
    else:
        print(text)
    if args.dump_json:
        args.dump_json.write_text(json.dumps(inv.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
