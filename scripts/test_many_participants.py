#!/usr/bin/env python
"""
Script helper per testare l'esperimento con molti partecipanti.

NOTA: Questo script è un wrapper. Per testare, usa direttamente:
    otree test bargaining_tdl 9
    otree test bargaining_tdl 12

Questo script fornisce informazioni utili e verifica la configurazione.
"""

import os
import sys
import argparse


def print_test_info(num_participants):
    """Stampa informazioni utili per i test."""
    print(f"\n{'='*60}")
    print(f"Test con {num_participants} partecipanti ({num_participants // 3} gruppi)")
    print(f"{'='*60}\n")

    if num_participants % 3 != 0:
        print(f"⚠️  ATTENZIONE: num_participants deve essere multiplo di 3!")
        print(f"   Ricevuto: {num_participants}")
        print(f"   Suggerito: {((num_participants // 3) + 1) * 3}")
        return

    print("📋 Comandi per eseguire i test:")
    print(f"\n   # Test standard")
    print(f"   otree test bargaining_tdl {num_participants}")
    print(f"\n   # Test con export dati")
    print(f"   otree test bargaining_tdl {num_participants} --export")
    print(f"\n   # Test con browser bots (visivo)")
    print(f"   otree browser_bots bargaining_tdl {num_participants}")

    print(f"\n📊 Casi di test disponibili:")
    print(f"   - mutual_12")
    print(f"   - disagreement")
    print(f"   - no_dwl_star")

    print(f"\n✅ Checklist pre-test:")
    print(f"   [ ] Database resettato (otree resetdb)")
    print(f"   [ ] Numero partecipanti multiplo di 3")
    print(f"   [ ] Tutte le app nella sequenza corretta")
    print(f"   [ ] File tests.py presenti in tutte le app")

    print(f"\n📚 Per maggiori informazioni, vedi: docs/TESTING.md\n")


def main():
    """Funzione principale."""
    parser = argparse.ArgumentParser(
        description='Helper per testare l\'esperimento con molti partecipanti',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python scripts/test_many_participants.py 9
  python scripts/test_many_participants.py 12

Per eseguire i test, usa:
  otree test bargaining_tdl 9
  otree test bargaining_tdl 12
        """
    )
    parser.add_argument(
        'num_participants',
        type=int,
        nargs='?',
        default=9,
        help='Numero di partecipanti (default: 9)'
    )

    args = parser.parse_args()

    print_test_info(args.num_participants)


if __name__ == '__main__':
    main()
