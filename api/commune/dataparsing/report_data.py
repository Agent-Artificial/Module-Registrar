import json


def get_report_data_request(table_id, subnet=0):
    if not table_id:
        return {}
    
    with open(f"data/query_maps/table_{table_id}_columns.json", "r") as f:
        columns = json.load(f)
    with open(f"data/query_maps/table_{table_id}_headers.json", "r") as f:
        headers = json.load(f)
        
    row_length = len(columns.keys())
    header_row = ["MinerName"]
    for key in headers.keys():
        header_row.append(key)
        
    

    