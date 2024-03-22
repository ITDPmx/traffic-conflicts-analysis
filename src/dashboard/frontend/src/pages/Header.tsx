import React from "react";
import {
  Box,
  Flex,
  Text,
  useColorModeValue,
  useBreakpointValue,
  Image,
} from "@chakra-ui/react";
import distritoTec from "../stock/distritotec.png";
import tec from "../stock/tec.png";

export const useDate = () => {
  const locale = "en";
  const [today, setDate] = React.useState(new Date()); // Save the current date to be able to trigger an update

  React.useEffect(() => {
    const timer = setInterval(() => {
      // Creates an interval which will update the current data every minute
      // This will trigger a rerender every component that uses the useDate hook.
      setDate(new Date());
    }, 1 * 1000);
    return () => {
      clearInterval(timer); // Return a function to clear the timer so that it will stop being called on unmount
    };
  }, []);

  // const day = today.toLocaleDateString(locale, { weekday: "long" });
  const date = `\${day}, \${today.getDate()} \${today.toLocaleDateString(locale, { month: 'long' })}\n\n`;

  const hour = today.getHours();
  const wish = `Good ${
    (hour < 12 && "Morning") || (hour < 17 && "Afternoon") || "Evening"
  }, `;

  const time = today.toLocaleTimeString(locale, {
    hour: "numeric",
    hour12: true,
    minute: "numeric",
    second: "numeric",
  });

  return {
    date,
    time,
    wish,
  };
};

// Header with subnavigation, leaves the door open for future expansion
export default function WithSubnavigation() {
  return (
    <Box>
      <Flex
        bg={useColorModeValue("white", "gray.800")}
        color={useColorModeValue("gray.600", "white")}
        minH={"60px"}
        py={{ base: 2 }}
        px={{ base: 4 }}
        borderBottom={1}
        borderStyle={"solid"}
        borderColor={useColorModeValue("gray.200", "gray.900")}
        align={"center"}
      >
        <Flex flex={{ base: 1 }} justify={{ base: "center", md: "start" }}>
          <Text
            textAlign={useBreakpointValue({ base: "center", md: "left" })}
            fontFamily={"heading"}
            color={useColorModeValue("gray.800", "white")}
          >
            <Image src={distritoTec} alt="DistritoTec" h={7} /> 
          </Text>

          <Box display={{ base: "flex", md: "flex" }} ml={5} />

          <Text
            textAlign={useBreakpointValue({ base: "center", md: "left" })}
            fontFamily={"heading"}
            color={useColorModeValue("gray.800", "white")}
          >
            <Image src={tec} alt="Tec" h={7} />
          </Text>
          
          <Box display={{ base: "flex", md: "flex" }} ml={5} />

          <Flex
            flex={{ base: "none", md: 1 }}
            justify={{ base: "center", md: "right" }}
          >
            <Text
              textAlign={useBreakpointValue({ base: "center", md: "left" })}
              fontFamily={"heading"}
              color={useColorModeValue("gray.800", "white")}
            >
              Hora Actual: {useDate().time}
            </Text>
          </Flex>
        </Flex>
      </Flex>
    </Box>
  );
}
