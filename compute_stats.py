import json

with open(r'c:\Users\62823\ExplainMyRoad+\data\jambi_roads.geojson', 'r') as f:
    data = json.load(f)

features = data['features']
total_links = len(features)

flagged = 0
neglected = 0
favored = 0

for f in features:
    props = f['properties']
    score = props.get('alignment_score', 100)
    rank = props.get('rank', 999)
    allocated = props.get('is_allocated', 0)
    
    if score < 75:
        flagged += 1
        
    if rank <= 150 and allocated != 1:
        neglected += 1
        
    if rank > 500 and allocated == 1:
        favored += 1

print(f"Total Links: {total_links}")
print(f"Flagged (Score < 75): {flagged}")
print(f"Neglected (Rank <= 150, !Allocated): {neglected}")
print(f"Favored (Rank > 500, Allocated): {favored}")
