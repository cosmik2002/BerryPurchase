export function parseReport(data) {
  const rows = [];
  for(const client in data) {
    const row = {
      name: client
    } ;
    for (const good in data[client]) {
      let key = good.replace(/\(/g,"").replace(/\)/g,"").replace(/'/g, "");
      row[key] = data[client][good];
    }
    rows.push(row)
  }
  return rows;
}
