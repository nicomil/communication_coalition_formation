# Grammar Review & Correction Plan

This plan documents all grammatical errors, stylistic issues, and redundancies found across the experiment's participant-facing HTML files, and proposes specific corrections.

---

## Files in scope

| File | Module |
|---|---|
| [Welcome.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/Welcome.html) | `bargaining_tdl_intro` |
| [InstructionsPart1.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/InstructionsPart1.html) | `bargaining_tdl_intro` |
| [ControlQuestions.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/ControlQuestions.html) | `bargaining_tdl_intro` |
| [Goodbye.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/Goodbye.html) | `bargaining_tdl_intro` |
| [SimulatedChat.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/SimulatedChat.html) | `bargaining_tdl_intro` |
| [ChatAndSignals.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/ChatAndSignals.html) | `bargaining_tdl_intro` |
| [InstructionsPart2.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/InstructionsPart2.html) | `bargaining_tdl_part2` |
| [ExampleScreenPart2.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/ExampleScreenPart2.html) | `bargaining_tdl_part2` |
| [PaymentInstructionPart2.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/PaymentInstructionPart2.html) | `bargaining_tdl_part2` |
| [ControlQuestionsPart2.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/ControlQuestionsPart2.html) | `bargaining_tdl_part2` |
| [MPLIntroFirstPlayer.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/MPLIntroFirstPlayer.html) | `bargaining_tdl_part2` |
| [MPLIntroSecondPlayer.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/MPLIntroSecondPlayer.html) | `bargaining_tdl_part2` |
| [InstructionsPart3.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part3/InstructionsPart3.html) | `bargaining_tdl_part3` |
| [ControlQuestionsPart3.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part3/ControlQuestionsPart3.html) | `bargaining_tdl_part3` |
| [ThankYouPart2.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/ThankYouPart2.html) / [ThankYouPart3.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part3/ThankYouPart3.html) / [Goodbye.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/Goodbye.html) | All modules |
| [ResultsPart3.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part3/ResultsPart3.html) | `bargaining_tdl_part3` |

---

## Proposed Changes

### `bargaining_tdl_intro`

#### [MODIFY] [Welcome.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/Welcome.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 24 | Awkward phrasing | "you can earn an additional $ 5 ($ 0 otherwise) choosing between pairs of options" | "you can earn an additional $ 5 by choosing between pairs of options ($ 0 otherwise)" |
| 2 | 31–34 | Run-on / redundant sentence | "Only one between Part 1 and Part 3, will be randomly selected with equal probability at the end of the experiment." | "Either Part 1 or Part 3 will be randomly selected with equal probability at the end of the experiment to determine your earnings." |

---

#### [MODIFY] [InstructionsPart1.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/InstructionsPart1.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 43–44 | Grammatical error: "the each of" | "received by the each of the other group members" | "received by each of the other group members" |
| 2 | 57 | Wordy / redundant | "I wish to split the $ 12 equally with both the two players." | "I wish to split the $ 12 equally with both players." |
| 3 | 64–65 | Punctuation error: spurious comma after "Revealing" and after "and" | "Revealing your identity to other participants, and using, discriminatory or offensive language, are strictly prohibited." | "Revealing your identity to other participants or using discriminatory or offensive language is strictly prohibited." |
| 4 | 68 | Garbled phrase: "a keeping this polite" | "maintaining a keeping this polite" | "maintaining a respectful and polite environment" |
| 5 | 80–81 | Pronoun mismatch: "its intentions" | "each member of the group chooses its intentions" | "each member of the group chooses their intentions" |
| 6 | 39 | "this Part" has unnecessary capital | "In this Part of the experiment" | "In this part of the experiment" |

---

#### [MODIFY] [ControlQuestions.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/ControlQuestions.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 11–12 | Discontinuous paragraph — `<strong>` tag placed awkwardly outside `<p>` | `</p> <strong>Please note:...</strong><p>` | Move **Please note** inside the preceding `<p>` tag or wrap in its own `<p>` so the HTML structure is consistent |

> [!NOTE]
> The text content itself on line 12 is fine ("After two wrong answers, you will not be able to continue with the experiment."); it is only the HTML tag placement that needs fixing.

---

#### [MODIFY] [InstructionsPart1.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_intro/InstructionsPart1.html) — Chat Instructions paragraph simplification

> [!IMPORTANT]
> The Chat Instructions paragraph (lines 38–45) is verbose and contains a redundancy: it says "you will only see the messages sent by you, and received by the each of the other group members" which is contradictory/confusing. Proposed simplified version:

**Current:**
> "In this Part of the experiment, you will have 3 minutes to communicate freely with the other participants. You will have to write your messages to each of the other two group members. In these messages you can explain to each of them what division you intend to choose, and what division you think they should choose. You can write different messages to the different group members. Messages are private, and you will only see the messages sent by you, and received by the each of the other group members. You will not see the messages sent between the other two group members."

**Proposed:**
> "In this part of the experiment, you will have 3 minutes to communicate freely with the other participants. You may write separate messages to each of the other two group members, explaining your intended division and what you think they should choose. Messages are private: each member can only see the messages they personally sent or received. You will not see the messages exchanged between the other two group members."

---

### `bargaining_tdl_part2`

#### [MODIFY] [InstructionsPart2.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/InstructionsPart2.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 13–15 | Clause ambiguity: "In Part 1 you are matched with…" (wrong tense/context for Part 2 instructions) | "In Part 1 you are matched with the player on the left and the player on the right, we will present to you six questions for each player…" | "Since in Part 1 you were matched with both the player on the left and the player on the right, we will present you with six questions for each player…" |
| 2 | 39 | Doubled phrase | "the random value of random value of the given probability option" | "the random value of the given probability option" |
| 3 | 40–41 | Awkward phrasing | "you will most likely prefer Option 1, as you might win something, as opposed to Option 2, where there is no chance of you to win at all" | "you will most likely prefer Option 1, since you might still win something, whereas Option 2 gives you no chance of winning at all" |

---

#### [MODIFY] [ExampleScreenPart2.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/ExampleScreenPart2.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 12 | Very long, dense paragraph — split into two sentences | The second paragraph is a single very long sentence describing two symmetric cases (clicking Option 2 / clicking Option 1). | Split into two shorter sentences for readability. |
| 2 | 16 | Redundant phrase ("The computer will then automatically indicate all of your choices" — already said in previous paragraph) | Sentence repeated | Remove the redundant opening sentence. |

**Proposed simplified version of paragraph 2 (line 12):**
> "To avoid clicking for each value of p, a single click is sufficient. Click on **Option 2** at the probability value from which you prefer Option 2 for all higher values; Click on **Option 1** at the probability value up to which you prefer Option 1 for all lower values. The program will automatically fill in the remaining choices."

**Proposed simplified version of paragraph 3 (line 16):**
> "In the example shown in the figure, the participant clicked only on the p = 55% button, and the program automatically filled in all other choices: Option 1 for all p ≤ 50%, and Option 2 for all p ≥ 55%. You may change your choices as many times as you wish before clicking the "OK" button to confirm and proceed to the next question. Once you click "OK", you cannot return to a previous question."

---

#### [MODIFY] [PaymentInstructionPart2.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/PaymentInstructionPart2.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 10 | Missing space before "In" | "different levels of p %.In the twelve screens" | "different levels of p%. In the twelve screens" |
| 2 | 11 | Missing space before parenthesis | "in Part 1(left/right) in the first six" | "in Part 1 (left/right) in the first six" |
| 3 | 13 | Missing space before parenthesis | "other participant you interact with(left/right)" | "other participant you interacted with (left/right)" — also wrong tense: "interact" → "interacted" |
| 4 | 36–37 | Redundancy: "ensure you understood" appears twice | "to ensure you understood the payment mechanism for Part 2" (L33) and "Please answer the following questions to ensure you understood the payment mechanism for Part 2." (L37) | Remove the second instance on L37 (or merge the two `<p>` tags into one). |

---

#### [MODIFY] [ControlQuestionsPart2.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/ControlQuestionsPart2.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 97 | Grammar: "Let assume that" | "Let assume that at the end…" | "Assume that at the end…" (or "Let us assume that…") |
| 2 | 80–82 | Missing article | "I would like to divide the $12 equally with player on the right" | "I would like to divide the $12 equally with **the** player on the right" |

---

#### [MODIFY] [MPLIntroSecondPlayer.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part2/MPLIntroSecondPlayer.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 9 | Vague sentence — no verb explaining what the 6 questions are about | "The next 6 questions are associated with **{{ second_player_label }}**." | "The next 6 questions refer to the choices made by **{{ second_player_label }}** in Part 1." |

---

### `bargaining_tdl_part3`

#### [MODIFY] [InstructionsPart3.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part3/InstructionsPart3.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 31–35 | Wordy / clunky sentence | "…then the choice of one of the three group members would be randomly selected and implemented. In each group, each participant has the same probability of being selected to implement the choice made as actual payment for all the members of the group." | "…one group member will be randomly selected with equal probability, and their choice will be implemented as the actual payment for all three members of the group." |

---

#### [MODIFY] [ControlQuestionsPart3.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part3/ControlQuestionsPart3.html)

| # | Line | Issue | Current | Proposed fix |
|---|---|---|---|---|
| 1 | 9–11 | HTML structure issue: `<p>` closed then immediately another `<p></p>` opened | `<strong>...</strong></p><p></p>You have been matched…</p>` | Merge into a single well-formed `<p>` block |
| 2 | 52–55 | Logic error in example text | "that the player on the right chose 'Share with both you and the player on the right'" | Should be "Share with both you and the player on the left" (sharing with yourself doesn't make sense) |

> [!CAUTION]
> Item #2 in ControlQuestionsPart3 may be a **content error** (wrong player direction), not just a grammar issue. Please verify the intended payoff logic before approving the correction.

---

## Verification Plan

### Manual Verification (no automated tests needed)
Since these are text-only changes in HTML templates, verification is visual:

1. After applying changes, run the oTree dev server:
   ```
   python -m otree devserver
   ```
2. Navigate to each modified page in your browser and verify:
   - The text reads correctly
   - No broken HTML tags (no missing `</p>` etc.)
   - The page layout is unchanged
3. Pay particular attention to [ControlQuestionsPart3.html](file:///c:/Users/Donat/comunication_coalition_formation_v12_DP/bargaining_tdl_part3/ControlQuestionsPart3.html) Example 2 to confirm the corrected player direction is logically consistent with the payoff calculation.
