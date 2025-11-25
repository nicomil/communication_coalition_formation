# Task List: Chat and Signal Restructuring

This document outlines the steps to restructure the "Simulated Chat" and "Signal Input" phases into a single, unified phase in the `bargaining_tdl_intro` app.

## 1. Modify `bargaining_tdl_intro/__init__.py`

- [ ] **Refactor Page Classes**:
    - Create a new page class `ChatAndSignals` (or rename `SimulatedChat` and merge logic).
    - Define `form_model = 'player'`.
    - Define `form_fields = ['signal_left', 'signal_right', 'draft_history_left', 'draft_history_right']`.
    - Move the `before_next_page` logic from `SignalInput` to this new page to save data to `participant.vars`.

- [ ] **Update Page Sequence**:
    - Replace `[SimulatedChat, SignalInput]` with `[ChatAndSignals]` in `page_sequence`.

## 2. Frontend Implementation (Template)

- [ ] **Design Interface (`ChatAndSignals.html`)**:
    - Use a grid or flexbox to create a **two-column layout**.
        - **Left Column**: "Partner Left"
        - **Right Column**: "Partner Right"
    
    - **Components per Column**:
        1. **Header**: Identify the target partner.
        2. **Signals**: Render `signal_left` (in left col) and `signal_right` (in right col) as radio buttons.
        3. **Message Area**: A large `<textarea>` for entering the message.
           - Remove the previous "chat history" and "send button" mechanism.
           - Bind these textareas to `draft_history_left` and `draft_history_right`.

- [ ] **Navigation**:
    - Single "Next" button at the bottom to submit the form.

## 3. Client-Side Logic & Validation

- [ ] **Empty Message Alert**:
    - Add JavaScript to handle the form submission event or button click.
    - Check if `draft_history_left` or `draft_history_right` is empty (or contains only whitespace).
    - If empty: Display a browser `alert()` or custom modal warning the user.
    - Allow the submission to proceed (e.g., using `confirm()` or just flagging it but not blocking subsequent clicks). The requirement is: "scattare un pop-up... ma sia comunque permesso andare avanti".

## 4. Cleanup

- [ ] Remove `SignalInput` class and template.
- [ ] Remove `SimulatedChat` class (if replaced) or clean up its code.
