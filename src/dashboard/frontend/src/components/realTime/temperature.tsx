import React, { useEffect, useState } from "react";
import { Box, HStack, Heading, Icon, Stack } from "@chakra-ui/react";
import { BsThermometerHigh } from "react-icons/bs";

const API_URL =
  "https://api.open-meteo.com/v1/forecast?latitude=25.68&longitude=-100.32&current_weather=true";

// The Temperature component, which shows the current temperature, fetched from the API.
function Temperature() {
  const [isLoading, setIsLoading] = useState(true);
  const [temperature, setTemperature] = useState(null);

  // This hook is executed when the component is mounted. It fetches the current temperature from the API and sets the temperature state.
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const current_weather = data["current_weather"];
        setTemperature(current_weather["temperature"]);
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
          <Icon as={BsThermometerHigh} boxSize={10} />
          <Stack>
            <Heading
              size="md"
              fontFamily={"Times New Roman"}
              fontStyle={"italic"}
            >
              Temperatura
            </Heading>

            <Heading size="lg" fontStyle={"italic"}>
              {temperature}°C
            </Heading>
          </Stack>
        </HStack>
      )}
    </Box>
  );
}

export default Temperature;
