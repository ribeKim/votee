import React from "react";
import ReactDOM from "react-dom/client";
import packageJson from "../package.json";

import App from "./App";
import "./styles.css";

const appVersion = import.meta.env.VITE_APP_VERSION || packageJson.version;

console.info(`[Votee] frontend version ${appVersion}`);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
