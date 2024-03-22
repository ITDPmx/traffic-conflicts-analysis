import React from "react";
import { Stack } from "@chakra-ui/react";
import RealTime from "../components/realTime";
import TimespanData from "../components/timespanData";

// The Dashboard page, which is rendered by ReactDOM when the user visits
// the / route. The Dashboard is divided in two sections:
// -> The RealTime component, which shows the current data
// -> The TimespanData component, which shows the data from the given timespan
function Dashboard() {
  return (
    <Stack
      bg="#FFFBFE"
      minHeight="70vh"
      paddingLeft="10vh"
      paddingRight="10vh"
      spacing={1}
    >
      <RealTime width="100%" height="200px" />
      <TimespanData />
    </Stack>
  );
}

export default Dashboard;
