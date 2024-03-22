import React, { useState, useEffect } from "react";
import { Heading, Stack } from "@chakra-ui/react";
import { getTopActivitiesByCount } from "../../utils/sortData";

// The TopActivities component, which shows the top activities of the given timespan.
function TopActivities(props: { startDate: string; endDate: string }) {
  const { startDate, endDate } = props;
  const [trends, setTrends] = useState<Array<[string, number]>>([]);
  const API_URL = `${process.env.REACT_APP_BACKEND_URL}/top_activities?after=${startDate}&before=${endDate}`;

  // Fetch the data from the API and sort it by count, then set the state
  // of the component to the sorted data.
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const dataSorted = Object.keys(data).map((key) => [
          key,
          data[key],
        ]) as Array<[string, number]>;

        setTrends(dataSorted.sort((a, b) => b[1] - a[1]));
      } catch (error) {
        console.error(`There was an error with your fetch operation: ${error}`);
      }
    };

    fetchData();
  }, [API_URL, startDate, endDate]);

  let restOfActivitiesCounter = 1;

  // Render the top activities and the rest of the activities.
  return (
    <Stack spacing={4} m={1}>
      {trends[0] ? (
        <Heading size="lg" color="yellow.500">
          Tendencia #1: {trends[0][0]}
        </Heading>
      ) : (
        <>There are no trends to display in this timespan.</>
      )}
      {trends.slice(1).map((activity) => {
        restOfActivitiesCounter += 1;
        return (
          <Heading size="sm" key={activity[0]}>
            {restOfActivitiesCounter}.- {activity[0]}
          </Heading>
        );
      })}
    </Stack>
  );
}

export default TopActivities;
