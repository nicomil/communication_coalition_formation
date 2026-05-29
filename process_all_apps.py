import csv
import os
import sys

def process_all_apps(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return

    # Column mapping: target_name -> source_name in CSV
    mapping = {
        'playerid': 'participant.id_in_session',
        'participant_code': 'participant.code',
        'groupid': 'bargaining_tdl_main.1.group.id_in_subsession',
        'inactive': 'participant.inactive_excluded',
        'left_player': 'bargaining_tdl_main.1.player.id_player_on_the_left',
        'right_player': 'bargaining_tdl_main.1.player.id_player_on_the_right',
        'part1_signal_left': 'bargaining_tdl_main.1.player.signal_left',
        'part1_signal_right': 'bargaining_tdl_main.1.player.signal_right',
        'part1_finaldecision': 'bargaining_tdl_main.1.player.decision_choice',
        'Part3_finaldecision': 'bargaining_tdl_part3.1.player.decision',
    }

    # Survey prefix
    survey_prefix = 'bargaining_tdl_survey.1.player.'

    with open(input_file, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline(); f.seek(0)
        delimiter = ';' if ';' in first_line else ','
        reader = csv.DictReader(f, delimiter=delimiter)
        headers = reader.fieldnames
        
        # Identify survey columns
        survey_cols = [h for h in headers if h.startswith(survey_prefix)]
        
        # Create final fieldnames list
        # We'll use the target names for mapped columns and clean names for survey columns
        output_fieldnames = list(mapping.keys())
        
        # Mapping for survey columns to make them cleaner (optional but good)
        survey_mapping = {h: h.replace(survey_prefix, 'survey_') for h in survey_cols}
        output_fieldnames.extend(survey_mapping.values())

        rows_to_write = []
        for row in reader:
            new_row = {}
            # Map main columns
            for target, source in mapping.items():
                new_row[target] = row.get(source, '')
            
            # Map survey columns
            for source, target in survey_mapping.items():
                new_row[target] = row.get(source, '')
            
            rows_to_write.append(new_row)

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_write)

    print(f"Dataset processato con successo! Salvato in: {output_file}")

if __name__ == '__main__':
    input_path = r'docs\all_apps_wide_2026-05-14 (1).csv'
    output_path = r'docs\processed_all_apps_dataset.csv'
    
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
        
    process_all_apps(input_path, output_path)
