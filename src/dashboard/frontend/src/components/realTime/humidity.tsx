import React, { useEffect, useState } from "react";
import { Box, HStack, Heading, Icon, Stack } from "@chakra-ui/react";
import { WiHumidity } from "react-icons/wi";

const API_URL =
  "https://api.open-meteo.com/v1/forecast?latitude=25.68&longitude=-100.32&current_weather=true&hourly=relativehumidity_2m&timezone=auto";

// The Humidity component, which shows the current humidity, fetched from the API.
function Humidity() {
  const [isLoading, setIsLoading] = useState(true);
  const [humidity, setHumidity] = useState(null);

  // This hook is executed when the component is mounted. It fetches the current humidity from the API and sets the humidity state.
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const currHumidity = data["hourly"]["relativehumidity_2m"];

        const currDate = new Date();
        const currHour = parseInt(currDate.getHours().toString());

        const hourlyHumidity = currHumidity[currHour];

        setHumidity(hourlyHumidity);
        setIsLoading(false);
      } catch (error) {
        console.error(`There was an error with your fetch operation: ${error}`);
      }
    };

    fetchData();
  }, []);
  return (
    <Box>
      {isLoading ? (
        <Heading size="md">Cargando...</Heading>
      ) : (
        <HStack>
          <Icon as={WiHumidity} boxSize={10} />
          <Stack>
            <Heading
              size="md"
              fontFamily={"Times New Roman"}
              fontStyle={"italic"}
            >
              Humedad
            </Heading>
            <Heading size="lg" fontStyle={"italic"}>
              {humidity}%
            </Heading>
          </Stack>
        </HStack>
      )}
    </Box>
  );
}

export default Humidity;
