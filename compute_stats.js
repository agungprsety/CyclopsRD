const fs = require('fs');
const data = JSON.parse(fs.readFileSync('c:/Users/62823/ExplainMyRoad+/data/jambi_roads.geojson', 'utf8'));

const features = data.features;
const totalLinks = features.length;

let flagged = 0;
let neglected = 0;
let favored = 0;

features.forEach(f => {
    const props = f.properties;
    const score = props.alignment_score || 100;
    const rank = props.rank || 999;
    const allocated = props.is_allocated || 0;
    
    if (score < 75) {
        flagged++;
    }
        
    if (rank <= 150 && allocated !== 1) {
        neglected++;
    }
        
    if (rank > 500 && allocated === 1) {
        favored++;
    }
});

console.log(`Total Links: ${totalLinks}`);
console.log(`Flagged (Score < 75): ${flagged}`);
console.log(`Neglected (Rank <= 150, !Allocated): ${neglected}`);
console.log(`Favored (Rank > 500, Allocated): ${favored}`);
