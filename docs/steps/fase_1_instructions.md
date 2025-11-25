# Specifiche Tecniche – Esperimento “From Words to Coalitions”
## Scenario programmato:
- **Communication Protocol:** PRIVATE TREATMENT  
- **Disagreement Payoff:** TDL (Total Deadweight Loss)

---

# 1. Welcome Page

### Contenuto da mostrare a schermo  
**Usa il wording esatto del PDF Instruction senza modifiche.**

**Testo (letterale da Instruction.pdf, pag. 2):**

> **Instructions**  
> **General Instructions**  
> **Welcome!**  
>
> In this experiment, you and the other participants will make a series of decisions that  
> will directly affect your monetary rewards. Your earnings will depend on both your own  
> choices and those made by the other participants. Similarly, your decisions will play a role  
> in determining the earnings of others.  
>
> At the beginning of the experiment, you will be assigned a fictitious identity consisting of  
> a letter and a number (such as Participant B3 or Participant F2), and you will be known as  
> such to the other participants. The other participants will never find out your real identity,  
> and you will never find out theirs.  
>
> The experiment consists of three parts: in Part 1, you can earn between £MIN (£0  
> in TDL treatment, £2 in NDL treatment) and £MAX (£6 in TDL treatment, £8 in NDL  
> treatment). In Part 2, you can earn an additional £5 (£0 otherwise). Finally, in Part 3,  
> you can earn between £0 and £6. Note, you will only be paid for either Part 1 or Part 3.  
>
> At the end of the experiment, you will be informed, privately on your screen, of your  
> earnings. Please remember that your earnings will be equal to a participation fee plus a  
> bonus up to £5 plus your earnings from Part 1 or Part 3. Only one between Part 1 and Part  
> 3, will be randomly selected with equal probability at the end of the experiment.

### Logica tecnica
- Assegnare un `participant.label` o `participant.vars['fict_id']` univoco.

---

# 2. Part 1 Instructions

### Contenuto da mostrare (pagg. 2–3 Instruction.pdf)  
**Usa il wording esatto del PDF Instruction senza modifiche.**  
**IGNORA la versione NDL.**

> **Instructions for Part 1**  
> In this part of the experiment, you and the other participants will be randomly matched in  
> groups of three. You and the other two members of your group will choose how each of you  
> would like to divide £12 between the three of you.  
>
> Each player has three options: to share the money equally with the player on the left,  
> with the player on the right, or with both players. For example:  
> • Option 1: Share only with the player on the left. Both you and the player on the left  
> earn £6, while the player on the right earns £0.  
> • Option 2: Share only with the player on the right. Both you and the player on the  
> right earn £6, while the player on the left earns £0.  
> • Option 3: Share with both players. All three of you earn £4.  
>
> **TDL treatment version:** “If two, or all of you, agree on how the money will be  
> divided, the money will be paid out accordingly.  
> If, however, no two group members choose the same division, each of you will receive  
> £0.”  
>
> **Chat Instructions**  
> Before making your decision, you will have 6 minutes to write two messages, one to each  
> of the other two group members. In this message you can explain to each of them what  
> division you intend to choose, and what division you think they should choose. You can  
> write different messages to the different group members.  
>
> Please note: Revealing your identity to other participants, and using, discriminatory  
> or offensive language, are strictly prohibited. Conversations will be analyzed after the end  
> of the experimental session and before payments are finalized. If it is found that the above  
> conditions have been violated, your payment for this experiment will be completely forfeited.  
> We expect and appreciate your cooperation in maintaining a keeping this polite.  
> • **Private communication Treatment:** Messages are private, and you will only see  
> the messages sent by you, and received by the each of the other group members. You  
> will not see the messages sent between the other two group members.

### Interfaccia
- Pulsante **Next**.

---

# 3. Chat Stage — PRIVATE TREATMENT

### Timer
- 6 minuti (`timeout_seconds = 360`)

### Layout split-screen
- Sinistra → chat con *Left*  
- Destra → chat con *Right*  

### Logica Private Treatment (critica)
- Ogni player vede **solo** chat bilaterali che lo coinvolgono.
- Nessuna possibilità di vedere/inferire B–C.

### Struttura dati
ChatMessage(sender, receiver, text, timestamp, channel)


---

# 4. Signaling Stage — PRIVATE TREATMENT

### Ogni player invia:
- `signal_to_left`
- `signal_to_right`

### Opzioni (dal Paper pag.6)
- “I wish to split the payoff equally with Participant B1 only.”  
- “I wish to split the payoff equally with Participant C1 only.”  
- “I wish to split the payoff equally with both of the other participants.”  
- “I do not wish to communicate my intentions.”

### Logica Private Treatment
- Ogni signal è **diadico**: mittente → destinatario.
- Un player vede solo i signal destinati a lui.
- Nessun accesso a B→C o C→B.

### Storage consigliato
signal_to_left
signal_to_right
signal_to_left_receiver_id
signal_to_right_receiver_id


---

# 5. WaitPage & Group Logic

- Gruppi da 3 fissi  
- WaitPage obbligatoria dopo i signal  
- Attendere che tutti abbiano finito chat + signal

---

# 6. Decision Stage — PRIVATE + TDL

### Mostrare
- `signal_from_left_to_me`
- `signal_from_right_to_me`

### Private enforcement
- Passare in template **solo** i signal diretti al giocatore.

### Scelta
- Share Left  
- Share Right  
- Share Both  

### Maggioranza
- Se ≥ 2 scegli la stessa → implementata
- Se no majority → payoff = 0 per tutti (TDL)

### Payoff TDL
- Share Left → (6,6,0)  
- Share Right → (6,0,6)  
- Share Both → (4,4,4)  
- No majority → (0,0,0)

---

# FINE FILE
