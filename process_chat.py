import csv
import sys
import os

def process_chat(input_file, output_file):
    # Leggiamo il dataset originale
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        channel = row['channel']
        # Il channel ha il formato: {id_sessione}-bargaining_tdl_main-{group_id}_{idA}_{idB}
        # Dividiamo per '-' per isolare l'ultima parte
        parts = channel.split('-')
        if len(parts) >= 3:
            group_parts = parts[-1].split('_')
            if len(group_parts) == 3:
                group_id = int(group_parts[0])
                idA = int(group_parts[1])
                idB = int(group_parts[2])
                
                nickname = row['nickname']
                sender_id = None
                receiver_id = None
                
                # Topologia fissa: 1(Red) -> Left=3(Blue), Right=2(Green)
                # La channel usa sempre id in ordine crescente (min_max)
                # Il Nickname nella chat è "LeftPartner" o "RightPartner" ed è sempre opposto alla label di chi manda.
                if (idA, idB) == (1, 2):
                    sender_id = 1 if nickname == "LeftPartner" else 2
                    receiver_id = 2 if nickname == "LeftPartner" else 1
                elif (idA, idB) == (2, 3):
                    sender_id = 2 if nickname == "LeftPartner" else 3
                    receiver_id = 3 if nickname == "LeftPartner" else 2
                elif (idA, idB) == (1, 3):
                    # In 1_3: P3 manda usando il box RightPartner -> nick='LeftPartner'.
                    # P1 manda usando il box LeftPartner -> nick='RightPartner'.
                    sender_id = 3 if nickname == "LeftPartner" else 1
                    receiver_id = 1 if nickname == "LeftPartner" else 3
                
                colors = {1: 'Red', 2: 'Green', 3: 'Blue'}
                
                row['group_id'] = group_id
                row['From'] = colors.get(sender_id, "Unknown")
                row['To'] = colors.get(receiver_id, "Unknown")
            else:
                row['group_id'] = ""
                row['From'] = ""
                row['To'] = ""
        else:
            row['group_id'] = ""
            row['From'] = ""
            row['To'] = ""
            
    # Ordiniamo per sessione, gruppo e timestamp
    def sort_key(r):
        return (r['session_code'], r['group_id'], float(r['timestamp']))
        
    rows.sort(key=sort_key)
    
    # Assegniamo il chat_id incrementale per ogni gruppo
    current_group = None
    chat_id = 0
    for row in rows:
        group_key = (row['session_code'], row['group_id'])
        if group_key != current_group:
            current_group = group_key
            chat_id = 1
        else:
            chat_id += 1
        row['chat_id'] = chat_id
        
    # Scriviamo il nuovo CSV
    # Ordine delle colonne per una migliore leggibilità
    fieldnames = ['session_code', 'group_id', 'chat_id', 'From', 'To', 'body', 'timestamp', 'nickname', 'participant_code', 'channel']
    
    # Creiamo una lista pulita con solo i campi che ci interessano
    clean_rows = []
    for row in rows:
        clean_row = {k: row.get(k, '') for k in fieldnames}
        clean_rows.append(clean_row)

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)
        
    print(f"Dataset processato con successo! Salvato in: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python process_chat.py <input.csv> <output.csv>")
    else:
        process_chat(sys.argv[1], sys.argv[2])
