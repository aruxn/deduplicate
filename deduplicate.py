import json
from datetime import datetime

def deduplicate_leads(input_file):
    with open(input_file, 'r') as f:
        leads = json.load(f)['leads']

    id_map = {}
    email_map = {}
    log = []

    for curr_lead in leads:
        curr_id = curr_lead['_id']
        curr_email = curr_lead['email']
        curr_date = datetime.fromisoformat(curr_lead['entryDate'])

        dup_id = curr_id in id_map
        dup_email = curr_email in email_map

        if not dup_id and not dup_email:
            # No conflicts, just add it
            id_map[curr_id] = curr_lead
            email_map[curr_email] = curr_lead
        else:
            # Got a conflict, find the older lead
            prev_lead = id_map[curr_id] if dup_id else email_map[curr_email]
            prev_date = datetime.fromisoformat(prev_lead['entryDate'])

            # If current lead is newer or same time but appears later, replace
            if curr_date >= prev_date:
                changes = {
                    f: {'from': prev_lead.get(f), 'to': curr_lead.get(f)}
                    for f in set(prev_lead.keys()).union(curr_lead.keys())
                    if prev_lead.get(f) != curr_lead.get(f)
                }

                log.append({
                    'source_record': prev_lead,
                    'output_record': curr_lead,
                    'field_changes': changes
                })

                # Clean up old lead and add the new one
                old_id = prev_lead['_id']
                old_email = prev_lead['email']

                if old_id in id_map:
                    del id_map[old_id]
                if old_email in email_map:
                    del email_map[old_email]

                id_map[curr_id] = curr_lead
                email_map[curr_email] = curr_lead
            else:
                # Keep old, log no changes
                log.append({
                    'source_record': curr_lead,
                    'output_record': prev_lead,
                    'field_changes': {}
                })

    return list(id_map.values()), log

def main():
    input_file = 'leads.json'
    output_file = 'leads_output.json'
    log_file = 'leads_output_logs.json'

    deduped, dedup_log = deduplicate_leads(input_file)

    with open(output_file, 'w') as f:
        json.dump({"leads": deduped}, f, indent=2)
    print(f"Output file: {output_file}")

    with open(log_file, 'w') as f:
        json.dump(dedup_log, f, indent=2)
    print(f"Output logs: {log_file}")

if __name__ == '__main__':
    main()
