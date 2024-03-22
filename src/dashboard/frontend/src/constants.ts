import { LatLngBounds, LatLngExpression, LatLngTuple } from "leaflet";

export const IMG_NE_BOUND = [25.654195, -100.28383];
export const IMG_SW_BOUND = [25.650468, -100.288154];
export const ORTHO_BOUNDS = new LatLngBounds(
  [IMG_SW_BOUND[0], IMG_SW_BOUND[1]],
  [IMG_NE_BOUND[0], IMG_NE_BOUND[1]]
);

export const ORTHO_CENTER: LatLngTuple = [25.652983, -100.286419];
export const ORTHO_IMAGE =
  "https://firebasestorage.googleapis.com/v0/b/twreloaded-cc2cf.appspot.com/o/small.png?alt=media&token=66887936-87b9-414e-8487-59124f37c27f";

interface CameraInfo {
  name: string;
  url: string;
  position: LatLngExpression;
  radius: number;
  startAngle: number;
  stopAngle: number;
  centerView: LatLngExpression;
  zoom: number;
}
export const INFO_CAMERAS: CameraInfo[] = [
  {
    name: "Camara 1",
    // TODO: Load camera images from an external url.
    url: "./cam1.png",
    position: [25.652271, -100.287164],
    radius: 30,
    startAngle: -40,
    stopAngle: 50,
    centerView: [25.652385, -100.28708],
    zoom: 22,
  },
  {
    name: "Camara 2",
    url: "./cam2.png",
    position: [25.652064, -100.287233],
    radius: 30,
    startAngle: -32,
    stopAngle: 58,
    centerView: [25.652176, -100.287207],
    zoom: 22,
  },
];
