import React from "react";
import { Input } from "@chakra-ui/react";
import { Grid, GridItem, Heading } from "@chakra-ui/react";

// The TimespanData component, which shows the data from the given timespan.
function DateSelector(props: {
  setStartDate: React.Dispatch<React.SetStateAction<string>>;
  setEndDate: React.Dispatch<React.SetStateAction<string>>;
  startDate: string;
  endDate: string;
}) {
  const { setStartDate, setEndDate, startDate } = props;

  const [maxEndDate, setMaxEndDate] = React.useState("");

  // Convert a Date object to a string in the format YYYY-MM-DD
  function convertDate(date: Date) {
    return date.toISOString().substring(0, 10);
  }

  // Handle the change of the date in the calendar and update the start and end date
  function handleDateChange(calendarValue: any, start: boolean) {
    const date = new Date(calendarValue);
    if (start) {
      setStartDate(calendarValue);
      const endDate = convertDate(
        new Date(date.getFullYear(), date.getMonth(), date.getDate() + 30)
      );
      setMaxEndDate(endDate);
      setEndDate(endDate);
    } else {
      setEndDate(calendarValue);
      setMaxEndDate(calendarValue);
    }
  }

  return (
    <Grid
      templateColumns="repeat(2, 1fr)"
      templateAreas={`"header header"
                  "nav main"
                  "nav footer"`}
      gap={6}
    >
      <GridItem colSpan={1}>
        <Heading size="md" fontStyle={"italic"} p={"2"} w={"100%"}>
          Inicio
        </Heading>
        <Input
          placeholder="Señala el inicio de la semana"
          size="md"
          type="date"
          onChange={(event: any) => handleDateChange(event.target.value, true)}
        />
      </GridItem>
      <GridItem colSpan={1}>
        <Heading size="md" fontStyle={"italic"} p={"2"} w={"100%"}>
          Final
        </Heading>
        <Input
          id="endDate"
          placeholder="Señala el final de la semana"
          size="md"
          type="date"
          onChange={(event: any) => handleDateChange(event.target.value, false)}
          min={startDate}
          max={maxEndDate}
          value={maxEndDate}
        />
      </GridItem>
    </Grid>
  );
}

export default DateSelector;
