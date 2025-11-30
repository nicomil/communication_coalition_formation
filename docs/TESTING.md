# Guida ai Test per l'Esperimento Bargaining TDL

Questa guida spiega come testare l'esperimento con molti partecipanti (9, 12, etc.) per simulare condizioni realistiche prima del deploy in produzione con ~1000 partecipanti.

## 📋 Overview

L'esperimento è composto da 4 app sequenziali:
1. **bargaining_tdl_intro**: Istruzioni, control questions, chat e segnali
2. **bargaining_tdl_main**: Raggruppamento in triadi e decisione
3. **bargaining_tdl_part2**: 12 domande MPL (Matching Probability List)
4. **bargaining_tdl_part3**: Three-Person Dictator Game

Ogni app ha un file `tests.py` con bot che simulano comportamenti umani realistici.

---

## 🚀 Test Rapidi

### Test con 9 partecipanti (3 gruppi)

```bash
otree test bargaining_tdl 9
```

### Test con 12 partecipanti (4 gruppi)

```bash
otree test bargaining_tdl 12
```

### Test con numero personalizzato

```bash
otree test bargaining_tdl <NUMERO>
```

**Nota**: Il numero deve essere multiplo di 3 per formare gruppi completi.

---

## 🎯 Casi di Test Implementati

### bargaining_tdl_intro
- `cooperative`: Partecipante cooperativo (sempre Both)
- `competitive`: Partecipante competitivo (strategia Left/Right)
- `mixed`: Partecipante con strategia mista
- `altruistic`: Partecipante altruista (sempre Both)

### bargaining_tdl_main
- `all_both`: Tutti scelgono Both → payoff 4 per tutti
- `match_12`: P1-P2 match → P1 e P2 vincono (6), P3 perde (0)
- `match_23`: P2-P3 match → P2 e P3 vincono (6), P1 perde (0)
- `match_31`: P3-P1 match → P3 e P1 vincono (6), P2 perde (0)
- `disagreement`: Nessun match → tutti 0
- `mixed_strategy`: Strategia mista per testare vari scenari

### bargaining_tdl_part2
- `risk_averse`: Switching points bassi (0-30) - preferisce Option 1
- `risk_neutral`: Switching points medi (40-60)
- `risk_loving`: Switching points alti (70-100) - preferisce Option 2
- `mixed`: Switching points variabili

### bargaining_tdl_part3
- `share_left`: Condivide solo con left
- `share_right`: Condivide solo con right
- `share_both`: Condivide con entrambi
- `selfish`: Strategia egoista
- `cooperative`: Strategia cooperativa (share_both)

---

## 🔧 Test Avanzati

### Test con Export Dati

Per esportare i risultati dei test in CSV:

```bash
otree test bargaining_tdl 9 --export
```

I dati vengono salvati nella cartella `_tests/` (o nella cartella specificata).

### Test con Browser Bots (Test Visivo)

Per vedere i bot in azione nel browser (più lento ma più visivo):

```bash
otree browser_bots bargaining_tdl 9
```

**Nota**: Richiede Google Chrome installato.

### Test di una Singola App

Per testare solo una singola app:

```bash
otree test bargaining_tdl_intro 3
otree test bargaining_tdl_main 3
otree test bargaining_tdl_part2 3
otree test bargaining_tdl_part3 3
```

---

## 📊 Verifica dei Risultati

Dopo aver eseguito i test, verifica:

1. **Nessun errore**: Tutti i bot devono completare senza errori
2. **Payoff calcolati**: Verifica che i payoff siano stati calcolati correttamente
3. **Dati salvati**: Controlla che i dati siano stati salvati in `participant.vars`
4. **Gruppi formati**: Verifica che i gruppi di 3 siano stati formati correttamente

### Esempio di Output Atteso

```
✓ bargaining_tdl_intro: 9 partecipanti testati con successo
✓ bargaining_tdl_main: 9 partecipanti testati con successo (3 gruppi)
✓ bargaining_tdl_part2: 9 partecipanti testati con successo
✓ bargaining_tdl_part3: 9 partecipanti testati con successo
```

---

## 🐛 Risoluzione Problemi

### Errore: "num_participants deve essere multiplo di 3"

**Causa**: Il numero di partecipanti non è divisibile per 3.

**Soluzione**: Usa un numero multiplo di 3 (3, 6, 9, 12, 15, 18, etc.)

### Errore: "WaitPage timeout"

**Causa**: I bot non arrivano tutti alla wait page contemporaneamente.

**Soluzione**: 
- Verifica che tutti i bot abbiano completato le pagine precedenti
- Controlla che non ci siano errori nei test precedenti
- Aumenta il timeout nelle wait pages se necessario

### Errore: "Part 2 player not found"

**Causa**: I dati della Part 2 non sono stati salvati correttamente.

**Soluzione**:
- Verifica che i test della Part 2 siano stati eseguiti correttamente
- Controlla che `participant.vars` contenga i dati necessari

---

## 📝 Personalizzazione dei Test

### Aggiungere Nuovi Casi di Test

Per aggiungere nuovi casi di test, modifica il file `tests.py` dell'app corrispondente:

```python
class PlayerBot(Bot):
    cases = [
        'existing_case',
        'new_case',  # Aggiungi qui
    ]
    
    def play_round(self):
        case = self.case
        
        if case == 'new_case':
            # Implementa il comportamento per questo caso
            decision = 'Both'
        # ...
```

### Modificare Comportamenti Esistenti

Modifica la logica in `play_round()` per cambiare il comportamento dei bot:

```python
def play_round(self):
    case = self.case
    
    if case == 'cooperative':
        # Modifica qui il comportamento cooperativo
        decision = 'Both'
    # ...
```

---

## 🎓 Best Practices

1. **Testa sempre con multipli di 3**: Assicurati che il numero di partecipanti sia sempre multiplo di 3
2. **Varietà di casi**: Usa diversi casi di test per coprire vari scenari
3. **Verifica payoff**: Controlla sempre che i payoff siano calcolati correttamente
4. **Test incrementali**: Inizia con pochi partecipanti (3, 6) e aumenta gradualmente
5. **Test prima del deploy**: Esegui sempre i test prima di deployare in produzione

---

## 📚 Riferimenti

- [Documentazione oTree - Bots](https://otree.readthedocs.io/en/latest/bots.html)
- [Documentazione oTree - Test Avanzati](https://otree.readthedocs.io/en/latest/misc/bots_advanced.html)
- File di test esistenti: `bargaining_tdl_*/tests.py`

---

## ✅ Checklist Pre-Deploy

Prima di deployare in produzione con ~1000 partecipanti:

- [ ] Test con 9 partecipanti completato senza errori
- [ ] Test con 12 partecipanti completato senza errori
- [ ] Test con 18 partecipanti completato senza errori (opzionale, per testare più gruppi)
- [ ] Verificati tutti i payoff (Part 1, Part 2, Part 3)
- [ ] Verificato il calcolo del payoff finale
- [ ] Verificato il salvataggio dei dati in `participant.vars`
- [ ] Verificato il raggruppamento in triadi
- [ ] Test con export dati per verificare la struttura dei CSV
- [ ] Test con browser bots per verificare l'UI (opzionale)

---

**Nota**: I test sono progettati per essere realistici e coprire vari scenari. Tuttavia, in produzione con ~1000 partecipanti, potrebbero emergere comportamenti non previsti. Monitora sempre i risultati reali e aggiusta i test di conseguenza.

