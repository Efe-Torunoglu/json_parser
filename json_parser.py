import json
import sys
from datetime import datetime
def read_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data['leads']
    except FileNotFoundError:
        print('File Not Found')
        return None
def parse_date(date_string):
    return datetime.fromisoformat(date_string.replace('Z', '+00:00'))

def get_field_changes(old_record, new_record):
    changes = []
    for key in old_record:
        if old_record[key] != new_record[key]:
            changes.append(f"    {key}: '{old_record[key]}' → '{new_record[key]}'")
    return changes

def parse_leads(leads):
    newest_by_id = {}
    newest_by_email = {}

    for record in leads:
        record_id = record['_id']
        email = record['email']
        date = parse_date(record['entryDate'])

        # Update by Id
        if record_id in newest_by_id:
            old_record = newest_by_id[record_id]
            old_date = parse_date(old_record['entryDate'])
            print(f"\nFound duplicate ID: {record_id}")
            print(f"Source record: {old_record}")
            print(f"Newer record: {record}")
            if date >= old_date:
                changes = get_field_changes(old_record, record)
                if changes:
                    print("Fields changed:")
                    print("\n".join(changes))
                newest_by_id[record_id] = record  # Update with our newer version
        else:
            newest_by_id[record_id] = record

        # Update by Email
        if email in newest_by_email:
            old_record = newest_by_email[email]
            old_date = parse_date(old_record['entryDate'])
            print(f"\nFound duplicate email: {email}")
            print(f"Source record: {old_record}")
            print(f"Newer record: {record}")
            if date >= old_date:
                changes = get_field_changes(old_record, record)
                if changes:
                    print("Fields changed:")
                    print("\n".join(changes))
                newest_by_email[email] = record  # Update with our newer version
        else:
            newest_by_email[email] = record

    # Combine
    clean_records = list({r['_id']: r for r in {**newest_by_id, **newest_by_email}.values()}.values())
    return clean_records
def main():
    if len(sys.argv) != 2:
        print("Error, 1 Arg required")
        sys.exit(1)

    input_file = sys.argv[1]
    leads = read_json(input_file)
    unique_leads = parse_leads(leads)

    output_file = 'leads_cleaned.json'
    with open(output_file, 'w') as f:
        json.dump({'leads': unique_leads}, f, indent=2)

    print(f"Output saved to: {output_file}")
if __name__ == "__main__":
    main()
