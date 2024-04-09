export function parseReport(data) {
  const rows = [];
  const columns = [];
  const idxCol = {};
  columns.push({
    name: 'name',
    label: 'name',
    field: 'name',
  });
  for (const client in data) {
    let client_id;// = data[client]["('', 'client_id', '', '', '')"];
    const row = {
      name: {
        client_id: null,
        value: client
      }
    };
    const cli_data = data[client];
    for (const good in cli_data) {
      //убираем скобки и апострофы
      let good_id = 0;
      let key = good.replace(/\(/g, "").replace(/\)/g, "").replace(/'/g, "");
      if (key.includes("client_id")) {
        client_id = cli_data[good]
      } else {
        const split = key.split(",");
        good_id = split[0];
        key = split.slice(1).join(",");
        row[key] = {
          good_id: good_id,
          client_id: client_id,
          value: cli_data[good]
        };
        if (!idxCol[key]) {
          let col = {
            name: key,
            label: key,
            field: key,
            good_id: good_id
          };
          columns.push(col);
          idxCol[key] = true;
        }
      }
    }
    row.name.client_id = client_id;
    rows.push(row)
  }
  return {rows: rows, columns: columns};
}
