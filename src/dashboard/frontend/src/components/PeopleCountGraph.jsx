import React, { useState, useEffect } from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import exporting from "highcharts/modules/exporting";
import exportData from "highcharts/modules/export-data";
import { Heading } from "@chakra-ui/react";

// Enable exporting module and data
exporting(Highcharts);
exportData(Highcharts);

// PeopleCountGraph component that fetches data from the backend and displays it
const PeopleCountGraph = ({ startDate, endDate }) => {
  // Convert date to timestamp
  const start_ts = Date.parse(startDate.replace(/-/g, "/")) || 1680000000000;
  const end_ts = Date.parse(endDate.replace(/-/g, "/")) || 1684000000000;
  const API_URL = `${process.env.REACT_APP_BACKEND_URL}/?after=${start_ts}&before=${end_ts}`;
  let [countData, setCountData] = useState([]);

  const options = {
    chart: {
      zoomType: "x",
    },
    title: {
      text: "Crowd count",
    },
    xAxis: {
      type: "datetime",
    },
    yAxis: {
      title: {
        text: "People count",
      },
    },
    series: [
      {
        type: "area",
        name: "People",
        data: countData,
      },
    ],
    // Add exporting options
    exporting: {
      enabled: true,
      buttons: {
        contextButton: {
          menuItems: [
            "downloadPNG",
            "downloadJPEG",
            "downloadPDF",
            "downloadSVG",
            "separator",
            "downloadCSV",
            "downloadXLS",
          ],
        },
      },
    },
  };

  // Fetch data from the backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const parsedData = data["processed_images"].map((row) => [
          row["taken_at"],
          row["people_count"],
        ]);
        parsedData.sort((a, b) => a[0] - b[0]);
        setCountData(parsedData);
      } catch (error) {
        console.error(`There was an error with your fetch operation: ${error}`);
      }
    };

    fetchData();
  }, [API_URL]);

  // Display graph or error message
  return countData.length > 0 ? (
    <HighchartsReact highcharts={Highcharts} options={options} />
  ) : (
    <>
      <Heading size="xl" fontStyle={"italic"} p={"2"} w={"100%"}>
        Grafico de Conteo
      </Heading>
      There is no crowd count data for this timespan
    </>
  );
};

export default PeopleCountGraph;
