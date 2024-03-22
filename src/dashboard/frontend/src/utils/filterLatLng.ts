interface DataObject {
  lat: number;
  lon: number;
  taken_at: number;
  id: number | undefined;
}

export function filterByDate(
  data: DataObject[],
  minDateStr: string,
  maxDateStr: string
): DataObject[] {
  // Convert string dates to Unix timestamp in seconds
  const minDate = new Date(minDateStr).getTime();
  const maxDate = new Date(maxDateStr).getTime();
  return data.filter((item) => {
    return item.taken_at >= minDate && item.taken_at <= maxDate;
  });
}
