import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppShell } from "./components/AppShell";
import "./styles.css";
const root = document.getElementById("root");
if (!root) throw new Error("IntelAMP root element is missing");
createRoot(root).render(<StrictMode><AppShell /></StrictMode>);
