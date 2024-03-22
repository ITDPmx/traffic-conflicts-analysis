import { Dispatch, SetStateAction } from "react";
import { useMap, useMapEvents } from "react-leaflet";
import { LatLngExpression, LatLngLiteral, LatLngTuple } from "leaflet";

import PointMarker from "./PointMarker";

interface MarkersContainerProps {
  markers: LatLngTuple[];
  setMarkers: Dispatch<SetStateAction<LatLngTuple[]>>;
  setCenter: Dispatch<SetStateAction<LatLngExpression>>;
  setZoom: Dispatch<SetStateAction<number>>;
}
function MarkersContainer(props: MarkersContainerProps) {
  const { markers, setMarkers, setCenter, setZoom } = props;
  const map = useMap();

  function updatePosition(newPosition: LatLngLiteral, index: number) {
    map.setView(map.getCenter(), map.getZoom());
    setMarkers((prevMarkers) =>
      prevMarkers.map((marker, i) =>
        i === index ? [newPosition.lat, newPosition.lng] : marker
      )
    );
    setZoom(map.getZoom());
    setCenter(map.getCenter());
  }
  function deleteMarker(index: number) {
    setMarkers((prevMarkers) => prevMarkers.filter((_, i) => i !== index));
    setZoom(map.getZoom());
    setCenter(map.getCenter());
  }

  function AddMarker() {
    useMapEvents({
      click: (event) => {
        const { lat, lng } = event.latlng;
        setMarkers((prevMarkers) => [...prevMarkers, [lat, lng]]);
        setZoom(map.getZoom());
        setCenter(map.getCenter());
      },
      zoomlevelschange: () => {
        setZoom(map.getZoom());
      },
    });
    return null;
  }
  return (
    <>
      {markers.map((position, index) => (
        <PointMarker
          key={`marker-${index}`}
          name={(index + 1).toString()}
          color="#8b0000"
          position={position}
          setPosition={(x) => updatePosition(x, index)}
          onDelete={() => deleteMarker(index)}
        />
      ))}
      <AddMarker />
    </>
  );
}

export default MarkersContainer;
