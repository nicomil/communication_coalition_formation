# Prompt Migliorato per Cursor — Parte 3 dell’Esperimento

## 🎯 Obiettivo
Integrare e implementare la fase finale dell’esperimento (Part 3), mantenendo piena coerenza con:
- il paper originale  
- le istruzioni ai partecipanti  
- il flusso già stabilito nelle Part 1 e Part 2  
- la struttura Summary + Control Questions  

Nessun testo originale va modificato.

---

# 1. Contenuti Originali (da NON modificare)

## 1.1 Testo del Paper

```
In the three-person dictator game, each subject is randomly assigned to a new triad (i.e.,
Participant A1 is grouped with Participant D1 and Participant H1), and is free to divide a
surplus of e12 between themselves and the other subjects in the triad (i. e., each participant
acts as a dictator). Each participant has three predefined options for how to distribute
the surplus: two-way splits with only one participant (unequal allocation), or three-way
splits between all three (equal allocation). Equal allocations redistribute e4 for each triad’s
member. Unequal allocations redistribute e6 to the player in the dictator role and only one
of the two other participants. Each triad member’s decision was equally likely to be selected
for the purpose of calculating payments. If the final payout is determined by the dictator
game, one of the three participants’ choices within the triad will be randomly selected and
implemented, with each having an equal probability of being selected to be the dictator.
Communication was not present in this part, and participants did not learn about each
other’s choices from Part One until the end of the experiment.
```

---

## 1.2 Istruzioni Ufficiali

```
In this part of the experiment, you and the other participants will be matched in groups of
three. You and the other two members of your group will choose how each of you would like
to divide $ 12 between the three of you.
Please note that in Part 3 of the experiment, each participant will be matched
with other group members than those they were matched with in Part 1.
Each player has three options: to share the money equally with the player on the left,
with the player on the right, or with both players. For example:
• Option 1: Share only with the player on the left. Both you and the player on the left
earn $ 6, while the player on the right earns $ 0.
• Option 2: Share only with the player on the right. Both you and the player on the
right earn $ 6, while the player on the left earns $ 0.
• Option 3: Share with both the player on the left and the player on the right. All
three of you earn $ 4.
If Part 3 is randomly selected to determine the payoff of the experiment, then the choice
of one of the three group members would be randomly selected and implemented. In each
group, each participant has an equal probability of being selected as the actual decision
maker in Part 3.
```

---

## 1.3 Summary della Part 3

```
In summary, Part 3 will proceed as follows:
1. Group members make their decisions.
2. The decision maker is randomly determined.
3. Payments are determined.
```

---

## 1.4 Control Questions della Part 3

```
Control questions for Part 3
You have been matched with the player on the left and the player on the right for Part 3,
consider the following three examples:
Example 1: Imagine that you chose “Share only with the player on the left”, that the
player on the left chose “Share only with you”, and that the player on the right chose ”Share
with both the player on the left and the player on the right”. At the end of the experiment,
the player on the right is selected as the actual decision maker for Part 3.
What would your earning be for Part 3 in this case? ($ 4)
What would the earnings for the player on the left be for Part 3 in this case? ($ 4)
What would the earnings for the player on the right be for Part 3 in this case? ($ 4)

Example 2: Imagine that you chose “Share with both the player on the left and the
player on the right”, that the player on the left chose “Share only with the player on the
right”, and that the player on the right chose “Share with both you and the player on the
right”. At the end of the experiment, the player on the left is selected as the actual decision
maker for Part 3.
What would your earnings be for Part 3 in this case? ($ 0)
What would the earnings for the player on the left be for Part 3 in this case? ($ 6)
What would the earnings for the player on the right be for Part 3 in this case? ($ 6)

Excluding the participation fee of $ 2, how will your total payoff be determined in this
experiment?
• I will only get paid for one of the following parts: Part 1, Part 2, or Part 3.
• I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings
in either Part 1 or Part 3. (Correct answer)
• I will be paid an amount equal to the sum of the earnings achieved in each part of the
experiment.
• I don’t know.
```

---

# 2. Istruzioni per Cursor (Implementative)

## 2.1 Flusso Completo della Part 3

1. Instructions for Part 3  
2. Summary  
3. Control Questions  
   - tutte corrette → continua  
   - risposta sbagliata → Thank You Page  
4. Decision Screen  
5. Thank You Page  

---

## 2.2 Regole Implementative

- Non modificare nessun testo originale.  
- Il flusso deve essere coerente con Part 1 e Part 2.  
- Le Control Questions funzionano come nelle parti precedenti.  
- La triade è nuova, con nuovo mapping left/right.  
- **Nota importante**: Questo è un task individuale per l'utente. A posteriori sarà lo sperimentatore a creare il gruppo con una nuova triade.  

---

## 2.3 Schermata Decisionale

Mostrare tre opzioni:

- Share only with left  
- Share only with right  
- Share with both  

La scelta deve essere salvata per il calcolo finale del payoff.

---

# 3. Obiettivi Finali per Cursor

Cursor deve:

- preservare i testi originali  
- costruire il flusso completo della Part 3  
- validare correttamente le Control Questions  
- registrare la scelta del soggetto  
- concludere l’esperimento correttamente  

---

