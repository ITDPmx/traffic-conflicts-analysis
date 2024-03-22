import { useEffect, useState } from "react";
import { Parser } from "@json2csv/plainjs";
import { Center, Button } from "@chakra-ui/react";

// The RawDataButton component, which downloads the raw data of a given timespan as a CSV file.
function RawDataButton(props: { startDate: string; endDate: string }) {
  const { startDate, endDate } = props;

  const [responseJson, setResponseJson] = useState([]);

  const startDateTimestamp = new Date(startDate).getTime();
  const endDateTimestamp = new Date(endDate).getTime();

  const API_URL = `${process.env.REACT_APP_BACKEND_URL}/people?after=${startDateTimestamp}&before=${endDateTimestamp}`;

  // Fetch the data from the backend as a JSON object
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setResponseJson(data.points);
      } catch (error) {
        console.error(`There was an error with your fetch operation: ${error}`);
      }
    };
    fetchData();
  }, [API_URL]);

  // Parse the JSON and download it as a CSV file.
  const handleDownload = () => {
    try {
      const parser = new Parser();
      const csv = parser.parse(responseJson);

      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "archivo";
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Center p={5}>
      {responseJson.length === 0 ? (
        <></>
      ) : (
        <Button onClick={handleDownload}> Descargar Datos</Button>
      )}
    </Center>
  );
}
export default RawDataButton;
