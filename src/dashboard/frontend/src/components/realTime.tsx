import React from "react";
import { Grid, GridItem } from "@chakra-ui/react";
import PeopleCapacity from "../components/realTime/peopleCapacity";
import Temperature from "../components/realTime/temperature";
import Humidity from "../components/realTime/humidity";
import AirQuality from "../components/realTime/airQuality";
import { Card, CardBody, Heading, Stack } from "@chakra-ui/react";

// The RealTime component, which shows the current data.
// It is divided in four sections:
// -> PeopleCapacity, which shows the current count of people
// -> Temperature, which shows the current temperature
// -> Humidity, which shows the current humidity
// -> AirQuality, which shows the current air quality
function RealTime(props: {
  children?: React.ReactNode;
  width: string;
  height: string;
}) {
  return (
    <Stack width={props.width} p="4">
      <Heading size="xl" fontStyle={"italic"}>
        Tiempo Real
      </Heading>
      <Card>
        <CardBody>
          <Grid
            templateRows="repeat(2, 1fr)"
            templateColumns="repeat(3, 1fr)"
            gap={4}
            h={props.height}
          >
            <GridItem rowSpan={2} colSpan={1}>
              <PeopleCapacity />
            </GridItem>

            <GridItem rowSpan={1} colSpan={1} h="100%">
              <Temperature />
            </GridItem>

            <GridItem rowSpan={1} colSpan={1} h="100%">
              <Humidity />
            </GridItem>

            <GridItem colSpan={2} h="100%">
              <AirQuality />
            </GridItem>
          </Grid>
        </CardBody>
      </Card>
    </Stack>
  );
}

export default RealTime;
