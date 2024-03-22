import React from "react";
import { Outlet } from "react-router-dom";
import Header from "./Header";

// The root of the app, which is rendered by ReactDOM
export default function Root() {
  // The Header is always rendered, regardless of the route
  return (
    <>
      <Header /> 
      <div id="detail">
        <Outlet />
      </div>
    </>
  );
}
