import React from "react";
import Activities from "./activities/activities";
import DateSelector from "./dateSelector";
import PeopleCountGraph from "./PeopleCountGraph";
import HeatMap from "./HeatMap";
import RawDataButton from "./rawData";
import moment from 'moment';

// The TimespanData component, which shows the data from a given timespan. It is divided in five sections:
// -> DateSelector, which allows the user to select the start and end date of the timespan
// -> HeatMap, which shows the heatmap of the timespan
// -> Activities, which shows the activities of the timespan
// -> PeopleCountGraph, which shows the number of people in the timespan
// -> RawData, button which allows the user to download the raw data of the timespan
function TimespanData() {
  const tomorrow = moment().add(2, 'days');
  const [startDate, setStartDate] = React.useState("2023-05-01");
  const [endDate, setEndDate] = React.useState(tomorrow.format('YYYY-MM-DD'));

  return (
    <>
      <DateSelector
        setStartDate={setStartDate}
        setEndDate={setEndDate}
        startDate={startDate}
        endDate={endDate}
      />
      <HeatMap startDate={startDate} endDate={endDate} />
      <Activities startDate={startDate} endDate={endDate} />
      <PeopleCountGraph startDate={startDate} endDate={endDate} />
      <RawDataButton startDate={startDate} endDate={endDate} />
    </>
  );
}

export default TimespanData;
