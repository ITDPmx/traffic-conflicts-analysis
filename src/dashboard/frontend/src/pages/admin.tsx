import {
  Button,
  HStack,
  Heading,
  Icon,
  SimpleGrid,
  Stack,
} from "@chakra-ui/react";
import { useEffect, useRef, useState } from "react";
import { CheckIcon, ChevronLeftIcon, ChevronRightIcon } from "@chakra-ui/icons";
import {
  ImageOverlay,
  LayerGroup,
  LayersControl,
  MapContainer,
  Marker,
  TileLayer,
} from "react-leaflet";
import "leaflet-semicircle";
import "leaflet/dist/leaflet.css";
import {
  LatLngTuple,
  Map,
  icon,
} from "leaflet";
import { SemiCircle } from "react-leaflet-semicircle";
import axios from "axios";

import PointMarker from "../components/calibration/PointMarker";
import MarkersContainer from "../components/calibration/MarkersContainer";
import ImageMapContainer from "../components/calibration/ImageMapContainer";
import { INFO_CAMERAS, ORTHO_BOUNDS, ORTHO_IMAGE } from "../constants";

const cameraIcon = icon({
  iconSize: [30, 30],
  iconAnchor: [15, 28],
  popupAnchor: [0, -25],
  iconUrl: "https://cdn-icons-png.flaticon.com/512/4017/4017956.png",
});
const MIN_NUM_POINTS = 4;

function Admin() {
  const mapRef = useRef<Map>(null);
  const [markers, setMarkers] = useState<LatLngTuple[]>([]);
  const [currentCamera, setCurrentCamera] = useState(0);
  const currentZoom = INFO_CAMERAS[currentCamera].zoom;
  const currentCenter = INFO_CAMERAS[currentCamera].centerView;
  const [zoom, setZoomLevel] = useState(currentZoom);
  const [center, setCenter] = useState(currentCenter);
  const [orthoMarkers, setOrthoMarkers] = useState<LatLngTuple[]>([]);
  const [sampleMarker, setSampleMarker] = useState<LatLngTuple>([0, 0]);
  const [estimatedMarker, setEstimatedMarker] = useState<LatLngTuple>([0, 0]);

  // Get calibration markers from API.
  useEffect(() => {
    async function getMarkers() {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/calibration/${currentCamera}`);
      setMarkers(response.data.source_points);
      setOrthoMarkers(response.data.target_points);
    }
    getMarkers();
  }, [currentCamera]);

  // Test calibration transformation.
  useEffect(() => {
    async function testCalibration() {
      if (
        markers.length >= MIN_NUM_POINTS &&
        markers.length === orthoMarkers.length
      ) {
        const response = await axios.post(
          `${process.env.REACT_APP_BACKEND_URL}/test/calibration`,
          {
            target_points: orthoMarkers,
            source_points: markers,
            sample_points: [sampleMarker],
          }
        );
        console.log(response);
        setEstimatedMarker(response.data.estimate_point[0]);
      }
    }
    testCalibration();
  }, [markers, orthoMarkers, sampleMarker]);

  // Update map view when camera changes.
  useEffect(() => {
    mapRef.current?.setView(currentCenter, currentZoom);
  }, [currentCamera, currentCenter, currentZoom]);

  function saveCalibration() {
    axios.post(`${process.env.REACT_APP_BACKEND_URL}/calibration/${currentCamera}`, {
      source_points: markers,
      target_points: orthoMarkers,
    });
  }

  return (
    <>
      <Heading>Recalibrar camaras</Heading>
      <SimpleGrid columns={2} spacing={5}>
        <MapContainer
          className="Map"
          ref={mapRef}
          zoom={zoom}
          center={center}
          doubleClickZoom={false}
          scrollWheelZoom={true}
          attributionControl={false}
          style={{ minHeight: "70vh", width: "100%" }}
          maxBounds={ORTHO_BOUNDS}
          minZoom={17}
        >
          <TileLayer
            url="https://www.google.cn/maps/vt?lyrs=m@189&gl=cn&x={x}&y={y}&z={z}"
            attribution=""
            maxZoom={24}
          />
          <ImageOverlay url={ORTHO_IMAGE} bounds={ORTHO_BOUNDS} />
          <LayersControl position="topright">
            <LayersControl.Overlay name="Camaras" checked={true}>
              <LayerGroup>
                {INFO_CAMERAS.map((cameraInfo, i) => (
                  <div key={`camera-marker-${i}`}>
                    <Marker
                      position={cameraInfo.position}
                      icon={cameraIcon}
                      eventHandlers={{
                        click: () => {
                          setCurrentCamera(i);
                          mapRef.current?.setView(currentCenter, currentZoom);
                        },
                      }}
                    />
                    <SemiCircle
                      position={cameraInfo.position}
                      radius={cameraInfo.radius}
                      startAngle={cameraInfo.startAngle}
                      stopAngle={cameraInfo.stopAngle}
                    />
                  </div>
                ))}
              </LayerGroup>
            </LayersControl.Overlay>
            <LayersControl.Overlay name="Calibracion" checked={true}>
              <LayerGroup>
                <MarkersContainer
                  markers={orthoMarkers}
                  setMarkers={setOrthoMarkers}
                  setCenter={setCenter}
                  setZoom={setZoomLevel}
                />
              </LayerGroup>
            </LayersControl.Overlay>
            <LayersControl.Overlay name="Pruebas" checked={true}>
              <LayerGroup>
                <PointMarker
                  name="x"
                  color="blue"
                  position={estimatedMarker}
                  setPosition={(x) => null}
                  onDelete={() => null}
                />
              </LayerGroup>
            </LayersControl.Overlay>
          </LayersControl>
        </MapContainer>
        <Stack>
          <HStack>
            <Button
              onClick={() => setCurrentCamera(currentCamera - 1)}
              isDisabled={currentCamera <= 0}
              leftIcon={<Icon as={ChevronLeftIcon} />}
            >
              Anterior
            </Button>
            <Button
              onClick={() => setCurrentCamera(currentCamera + 1)}
              isDisabled={currentCamera >= INFO_CAMERAS.length - 1}
              rightIcon={<Icon as={ChevronRightIcon} />}
            >
              Siguiente
            </Button>
            <Button
              onClick={() => saveCalibration()}
              colorScheme="green"
              leftIcon={<Icon as={CheckIcon} />}
            >
              Guardar Calibración
            </Button>
          </HStack>
          <Heading size="lg">{INFO_CAMERAS[currentCamera].name}</Heading>
          <ImageMapContainer
            url={INFO_CAMERAS[currentCamera].url}
            markers={markers}
            setMarkers={setMarkers}
            sampleMarker={sampleMarker}
            setSampleMarker={setSampleMarker}
          />
        </Stack>
      </SimpleGrid>
    </>
  );
}

export default Admin;
