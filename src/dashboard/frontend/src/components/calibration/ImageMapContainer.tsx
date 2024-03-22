import { CRS, LatLngExpression, LatLngTuple, Map } from "leaflet";
import {
  Dispatch,
  SetStateAction,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { ImageOverlay, MapContainer } from "react-leaflet";
import MarkersContainer from "./MarkersContainer";
import PointMarker from "./PointMarker";
import { ORTHO_CENTER } from "../../constants";


interface ImageMapContainerProps {
  url: string;
  markers: LatLngTuple[];
  setMarkers: Dispatch<SetStateAction<LatLngTuple[]>>;
  sampleMarker: LatLngTuple;
  setSampleMarker: Dispatch<SetStateAction<LatLngTuple>>;
}
function ImageMapContainer(props: ImageMapContainerProps) {
  const { url, markers, setMarkers, sampleMarker, setSampleMarker } = props;
  const mapRef = useRef<Map>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [zoom, setZoom] = useState(1);
  const [center, setCenter] = useState<LatLngExpression>(ORTHO_CENTER);
  const [imageDim, setImageDim] = useState<[number, number]>([1424, 2540]);
  const [width, setWidth] = useState(0);
  const height = imageDim ? (imageDim[0] / imageDim[1]) * width : 0;
  const maxBounds: LatLngTuple[] = [
    [0, width / 2],
    [height / 2, 0],
  ];
  const displayMarkers: LatLngTuple[] = useMemo(
    () =>
      markers.map(
        (marker) => [marker[0] * height / 2, marker[1] * width / 2] as LatLngTuple
      ),
    [markers, height, width]
  );

  useEffect(() => {
    const img = new window.Image();
    img.src = url;
    img.onload = function () {
      setImageDim([(this as any).height, (this as any).width]);
    };
  }, [url]);

  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        setWidth(containerRef.current.offsetWidth);
      }
      if (mapRef.current) {
        setCenter(mapRef.current.getCenter());
        setZoom(mapRef.current.getZoom());
      }
    };
    handleResize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  function updateMarkers(settingMarkets: any) {
    const newMarkers = settingMarkets(displayMarkers);
    setMarkers(
      newMarkers.map((marker: any) => [marker[0] * 2 / height, marker[1] * 2 / width])
    );
  }

  return (
    <div ref={containerRef} style={{ width: "100%" }}>
      <MapContainer
        ref={mapRef}
        zoom={zoom}
        center={center}
        crs={CRS.Simple}
        maxBounds={maxBounds}
        minZoom={1}
        zoomControl={false}
        doubleClickZoom={false}
        attributionControl={false}
        style={{ height: `${height}px`, width: "100%" }}
        key={Math.random()}
      >
        <ImageOverlay
          url={url}
          bounds={[
            [height / 2, 0],
            [0, width / 2],
          ]}
        />
        <MarkersContainer
          markers={displayMarkers}
          setMarkers={updateMarkers}
          setCenter={setCenter}
          setZoom={setZoom}
        />
        <PointMarker
          name="x"
          color="blue"
          position={[sampleMarker[0] * height / 2, sampleMarker[1] * width / 2]}
          setPosition={(x) => {
            if (mapRef.current) {
              setCenter(mapRef.current.getCenter());
              setZoom(mapRef.current.getZoom());
            }
            setSampleMarker([x.lat * 2 / height, x.lng * 2 / width]);
          }}
        />
      </MapContainer>
    </div>
  );
}

export default ImageMapContainer;
