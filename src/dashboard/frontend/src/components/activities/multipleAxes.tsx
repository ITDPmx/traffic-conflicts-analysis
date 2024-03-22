import { Box, Heading } from "@chakra-ui/react";
import React, { useState, useEffect } from "react";
import { AxisOptions, Chart } from "react-charts";

import {
  ActivityDataByDay,
} from "../../utils/sortData";

const activities = ["playing", "walking", "running", "reading"];
const colorsMap: { [key: string]: string } = {
  playing: "#1f77b4",
  walking: "#ff7f0e",
  running: "#d44401",
  reading: "#2ca02c",
};

// The ActivityGraph component, it processes the data and shows the graph
function ActivityGraph(props: {
  activityDataPerDay: ActivityDataByDay | undefined;
}) {
  const { activityDataPerDay } = props;
  const data = activityDataPerDay
    ? activities.map((activity) => ({
        label: activity,
        data:
          activityDataPerDay && activityDataPerDay[activity] ?
          activityDataPerDay[activity].map((activity) => ({
            primary: new Date(activity.date),
            secondary: activity.count,
          })) : [],
        color: colorsMap[activity],
      }))
    : [];

  const primaryAxis = {
    getValue: (datum: any) => datum.primary as unknown as Date,
    // Pad the automatically detected time scale with half of the band-size
    padBandRange: true,
  };

  const secondaryAxes: AxisOptions<(typeof data)[number]["data"][number]>[] = [
    {
      getValue: (datum) => datum.secondary,
      elementType: "line",
      // stacked: true,
    },
    {
      id: "2",
      getValue: (datum) => datum.secondary,
      elementType: "line",
    },
  ];
  return (
    <Chart
      options={{
        data,
        primaryAxis,
        secondaryAxes,
        defaultColors: ["#00ccff", "#008800", "#ddaacc", "#1f77b4"],
      }}
    />
  );
}

// The MultipleAxes component, which shows a graph of activities vs. time
export default function MultipleAxes(props: {
  startDate: string;
  endDate: string;
}) {
  const { startDate, endDate } = props;
  const API_URL = `${process.env.REACT_APP_BACKEND_URL}/activities_by_date?after=${startDate}&before=${endDate}`;

  const [activityDataPerDay, setActivityDataPerDay] =
    useState<ActivityDataByDay>({});


  // Fetch the data from the backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setActivityDataPerDay(data);
      } catch (error) {
        console.error(`There was an error with your fetch operation: ${error}`);
      }
    };
    fetchData();
  }, [API_URL, startDate, endDate]);

  return (
    <Box h={"400px"}>
      {Object.keys(activityDataPerDay).length === 0 &&
      activityDataPerDay.constructor === Object ? (
        <>
          <Heading size="xl" fontStyle={"italic"} p={"2"} w={"100%"}>
            Grafico de tendencias
          </Heading>
          There are no trends to display in this timespan.
        </>
      ) : (
        <ActivityGraph activityDataPerDay={activityDataPerDay} />
      )}
    </Box>
  );
}
