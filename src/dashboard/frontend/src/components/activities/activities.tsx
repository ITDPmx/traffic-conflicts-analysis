import React from "react";
import { Grid, GridItem, Heading } from "@chakra-ui/react";
import TopActivities from "./topActivities";
import MultipleAxes from "./multipleAxes";

// The Activities component, which shows the data from the last week.
// It is divided in two sections:
// -> TopActivities, which shows the top activities
// -> MultipleAxes, which shows a graph of activities vs. time
function Activities(props: { startDate: string; endDate: string }) {
  const { startDate, endDate } = props;
  return (
    <Grid templateColumns="repeat(3, 1fr)" gap={6} paddingTop="2vh">
      <GridItem colSpan={1}>
        <Heading size="xl" fontStyle={"italic"} p={"2"} w={"100%"}>
          Aforo de personas
        </Heading>
        <TopActivities startDate={startDate} endDate={endDate} />
      </GridItem>
      <GridItem colSpan={2}>
        <MultipleAxes startDate={startDate} endDate={endDate} />
      </GridItem>
    </Grid>
  );
}

export default Activities;
