import React, { useEffect, useState } from "react";
import { Box, Heading, Progress, Stack } from "@chakra-ui/react";

const API_URL =
  "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=25.68&longitude=-100.32&timezone=auto&hourly=pm10";

// This function returns the air quality label based on the pm10 value.
const getAirQualityBasedOnPm10 = (pm_10: number) => {
  if (pm_10 < 20) {
    return "Buena";
  } else if (pm_10 < 40) {
    return "Aceptable";
  } else if (pm_10 < 50) {
    return "Moderada";
  } else if (pm_10 < 100) {
    return "Mala";
  } else if (pm_10 < 150) {
    return "Muy Mala";
  }
  return "Extremely poor";
};

// The AirQuality component, which shows the current air quality, fetched from the API.
function AirQuality() {
  let [isLoading, setIsLoading] = useState(true);
  let [airQualityPm10Value, setAirQualityPm10Value] = useState(0);
  let [airQualityLabel, setAirQualityLabel] = useState("");
  let [airQualityNormalizedValue, setAirQualityNormalizedValue] = useState(0);

  // This hook is executed when the component is mounted. It fetches the current air quality from the API and sets the air quality state.
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const currDate = new Date();
        const hourIndex = parseInt(currDate.getHours().toString());
        const currentPM10 = data["hourly"]["pm10"][hourIndex];
        const airQuality = getAirQualityBasedOnPm10(currentPM10);

        setAirQualityPm10Value(currentPM10);
        setAirQualityNormalizedValue(100 - (currentPM10 / 150) * 100);
        setAirQualityLabel(airQuality);
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
        <Stack>
          <Heading
            size="md"
            fontFamily={"Times New Roman"}
            fontStyle={"italic"}
            paddingLeft={"4"}
          >
            Calidad de Aire ({airQualityPm10Value} PM<sub>10</sub>)
          </Heading>

          <Heading size="xl" fontStyle={"italic"} paddingLeft={"4"} w={"80%"}>
            {airQualityLabel}
          </Heading>

          <Box w={"100%"} h={[70, 100, 140]}>
            {/* Quick CSS hack to make the gradient. */}
            <Progress
              borderRadius={50}
              bgGradient="linear-gradient(90deg, rgba(255,13,13,1) 0%, rgba(255,78,17,1) 20%, rgba(255,142,21,1) 40%, rgba(250,183,51,1) 60%, rgba(172,179,52,1) 80%, rgba(105,179,76,1) 100%);"
              sx={{
                "& > div ": {
                  borderRight: "10px solid #e1e1e1",
                  background: "transparent",
                  borderRadius: "0",
                },
              }}
              hasStripe={true}
              value={airQualityNormalizedValue}
            ></Progress>
          </Box>
        </Stack>
      )}
    </Box>
  );
}

export default AirQuality;
