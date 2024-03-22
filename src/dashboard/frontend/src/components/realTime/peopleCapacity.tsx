import React, { useEffect, useState } from "react";
import { Box, Text, Heading, Center } from "@chakra-ui/react";

// The PeopleCapacity component, which shows the current number of people,
function PeopleCapacity() {
  const API_URL = `${process.env.REACT_APP_BACKEND_URL}/current_people`; // The URL of the API to get the current number of people

  const [currentPeople, setCurrentPeople] = useState<Number>();

  // This hook is executed when the component is mounted and when the API_URL changes.
  // It fetches the current number of people from the API and sets the currentPeople state.
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setCurrentPeople(data["count"]);
      } catch (error) {
        setCurrentPeople(0);
      }
    };

    fetchData();
  }, [API_URL]);

  return (
    <Center width={"100%"} height={"66%"}>
      <Box>
        <Heading size="3xl" fontStyle={"italic"} w={"100%"}>
          {currentPeople?.toString()}
        </Heading>
        <Text
          width="100%"
          textAlign={"right"}
          fontFamily={"Times New Roman"}
          fontStyle={"italic"}
          fontSize={"lg"}
        >
          personas
        </Text>
      </Box>
    </Center>
  );
}

export default PeopleCapacity;
