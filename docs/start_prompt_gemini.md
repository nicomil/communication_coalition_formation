# Technical Specifications: oTree Bargaining Game (Async Flow + TDL)

**Role:** You are an expert oTree (Python/Django) developer.
**Goal:** Implement a multiplayer experiment where participants perform tasks individually first (Instructions -> Simulated Chat -> Signals) and are only grouped into Triads at the end to determine outcomes based on their previous inputs.
**Knowledge base** su cui basarti:
1.  @docs/DPPT__22_11_25_Instruction.pdf (Istruzioni Fase 1 - **Fonte Primaria per terminologia e regole**)
2.  @docs/DPPT_10_11_25_Paper.pdf (Sezione 3.1 e Pagina 5/6 - **Fonte per dettagli tecnici su segnali e chat**)

**Treatment:** `Private Communication` + `TDL` (Total Deadweight Loss).

---

## 1. Models & Data Structure (`models.py`)

### Constants
* `PLAYERS_PER_GROUP = 3`
* `NUM_ROUNDS = 1`
* `PAYOFF_MAX = 6`
* `PAYOFF_SPLIT = 4`
* `PAYOFF_DISAGREEMENT = 0` (TDL Logic)
* `TIMER_CHAT = 360` (6 minutes) 

### Player Class (Fields for Async Storage)
Since groups do not exist during the chat phase, Players must store their "intended" messages in temporary fields.
* `draft_history_left` = LongStringField (Stores the chat log intended for the "Left" partner).
* `draft_history_right` = LongStringField (Stores the chat log intended for the "Right" partner).
* `signal_left` = StringField (Selected signal for Left partner).
* `signal_right` = StringField (Selected signal for Right partner).
* `decision_choice` = StringField (Choices: 'Left', 'Right', 'Both').

* **Mapping Fields (Populated AFTER grouping):**
    * `received_history_left` = LongStringField (The chat text *actually* written by the partner who ends up on the Left).
    * `received_history_right` = LongStringField (The chat text *actually* written by the partner who ends up on the Right).
    * `received_signal_left` = StringField.
    * `received_signal_right` = StringField.

---

## 2. Page Flow & Content

### Step 1: Page `Welcome`
**Logic:** Individual page. No grouping yet.
**Content (Verbatim from Instruction.pdf p.1-2):**
Render exactly this text:

> ## General Instructions
>
> **Welcome!**
>
> In this experiment, you and the other participants will make a series of decisions that will directly affect your monetary rewards. Your earnings will depend on both your own choices and those made by the other participants. Similarly, your decisions will play a role in determining the earnings of others.
>
> At the beginning of the experiment, you will be assigned a fictitious identity consisting of a letter and a number (such as Participant B3 or Participant F2), and you will be known as such to the other participants. The other participants will never find out your real identity, and you will never find out theirs.
>
> The experiment consists of three parts: in Part 1, you can earn between £0 and £6. In Part 2, you can earn an additional £5 (£0 otherwise). Finally, in Part 3, you can earn between £0 and £6. Note, you will only be paid for either Part 1 or Part 3. At the end of the experiment, you will be informed, privately on your screen, of your earnings.
>
> Please remember that your earnings will be equal to a participation fee plus a bonus up to £5 plus your earnings from Part 1 or Part 3. Only one between Part 1 and Part 3, will be randomly selected with equal probability at the end of the experiment. 

---

### Step 2: Page `InstructionsPart1`
**Logic:** Individual page.
**Content (Verbatim from Instruction.pdf p.2-3):**

> ## Instructions for Part 1
>
> In this part of the experiment, you and the other participants will be randomly matched in groups of three. You and the other two members of your group will choose how each of you would like to divide £12 between the three of you.
>
> Each player has three options: to share the money equally with the player on the left, with the player on the right, or with both players.
>
> For example:
> * Option 1: Share only with the player on the left. Both you and the player on the left earn £6, while the player on the right earns £0.
> * Option 2: Share only with the player on the right. Both you and the player on the right earn £6, while the player on the left earns £0.
> * Option 3: Share with both players. All three of you earn £4.
>
> If two, or all of you, agree on how the money will be divided, the money will be paid out accordingly. If, however, no two group members choose the same division, each of you will receive £0. 
>
> **Chat Instructions**
>
> Before making your decision, you will have 6 minutes to write two messages, one to each of the other two group members. In this message you can explain to each of them what division you intend to choose, and what division you think they should choose. You can write different messages to the different group members.
>
> Please note: Revealing your identity to other participants, and using, discriminatory or offensive language, are strictly prohibited. Conversations will be analyzed after the end of the experimental session and before payments are finalized. If it is found that the above conditions have been violated, your payment for this experiment will be completely forfeited. We expect and appreciate your cooperation in maintaining a keeping this polite.
>
> * **Private communication Treatment:** Messages are private, and you will only see the messages sent by you, and received by the each of the other group members. You will not see the messages sent between the other two group members. 
>
> **Summary**
>
> In summary, Part 1 will proceed as follows:
> 1. Should be the signal before
> 2. Group members send messages to each other.
> 3. Messages are read by the recipients.
> 4. Group members make their final decisions.
> 5. Payments are determined. 

---

### Step 3: Page `SimulatedChat` (Custom JavaScript Implementation)
**Constraint:** Do **NOT** use `otree.chat` (because groups don't exist yet).
**Logic:**
* Display a Split Screen interface (Left Column / Right Column) .
* **Timer:** 6 minutes (`timeout_seconds = 360`).
* **Functionality:**
    * Two standard HTML input boxes + "Send" buttons (one for Left partner, one for Right partner).
    * When user clicks "Send", use JavaScript to append the text to a visual log (div) so it *looks* like a chat history.
    * Store the full text log in a hidden input field linked to `player.draft_history_left` and `player.draft_history_right`.
    * *Note:* The user receives NO replies (as there is no partner yet). It is a "monologue" or "message composition" phase.

---

### Step 4: Page `SignalInput`
**Logic:** User selects a formal signal for each future partner.
**Form Fields:** Two inputs (dropdowns or radio), one for `signal_left` and one for `signal_right`.
**Options (Exact text from Paper p.6):**
1.  `"I wish to split the payoff equally with Participant [Left/Right] only."` (Dynamically adjust label).
2.  `"I wish to split the payoff equally with Participant [Other] only."`
3.  `"I wish to split the payoff equally with both of the other participants."`
4.  `"I do not wish to communicate my intentions."`


---

### Step 5: `WaitPage` (Crucial Grouping & Data Mapping)
**Configuration:** `group_by_arrival_time = True`.
**Logic in `after_all_players_arrive`:**
1.  **Form Triad:** The first 3 players are grouped. Assign IDs 1, 2, 3.
2.  **Define Topology:**
    * Player 1: Left Neighbor is P3, Right Neighbor is P2.
    * Player 2: Left Neighbor is P1, Right Neighbor is P3.
    * Player 3: Left Neighbor is P2, Right Neighbor is P1.
3.  **Map Data (The "Postman" Logic):**
    * Take the `draft_history_...` and `signal_...` from the sender.
    * Copy it into the `received_...` fields of the recipient.
    * *Example for Player 1:*
        * `p1.received_history_left` = `p3.draft_history_right` (Because P3's right neighbor is P1).
        * `p1.received_history_right` = `p2.draft_history_left` (Because P2's left neighbor is P1).
    * Repeat logic for P2 and P3.

---

### Step 6: Page `Decision`
**Display:**
* Show the **Private Chat History** (Read-Only).
    * "Messages from Left Participant": Display content of `player.received_history_left`.
    * "Messages from Right Participant": Display content of `player.received_history_right`.
    * *Constraint:* User sees ONLY messages involved in their dyads. (Private Treatment).
* Show the **Signals** (`received_signal_left`, `received_signal_right`).

**Form Input:**
* `decision_choice`: Radio button.
    1.  "Share only with the player on the left"
    2.  "Share only with the player on the right"
    3.  "Share with both players"

---

### Step 7: Results Calculation (Logic)
**TDL Payoff Matrix ():**
* If P1 chooses Left (P3) AND P3 chooses Right (P1) -> Match! Both get 6. P2 gets 0.
* If P1 chooses Right (P2) AND P2 chooses Left (P1) -> Match! Both get 6. P3 gets 0.
* If P1, P2, P3 ALL choose "Share with Both" -> Match! All get 4.
* **Else (Disagreement/TDL):** Everyone gets 0.
    * *Note:* Strict majority rule applies.
    * *Clarification from Table 2 :*
        * AB + BA + (C anything) = (6,6,0).
        * ABC + ABC + (C anything) = (4,4,4).
        * Essentially: If any 2 players form a compatible link, that link is implemented.
        * If no links form (e.g. A->B, B->C, C->A), payoff is (0,0,0).