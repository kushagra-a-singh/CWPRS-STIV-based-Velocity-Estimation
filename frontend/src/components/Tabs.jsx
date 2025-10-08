import { useState } from "react";
import { Bolt, Server, Upload } from "lucide-react"; // example icons (replace with your images if needed)

export default function Tabs() {
  const [active, setActive] = useState("analysis");

  const tabs = [
    { id: "analysis", label: "Analysis", icon: <Bolt className="w-4 h-4" /> },
    { id: "backend", label: "Backend Processes", icon: <Server className="w-4 h-4" /> },
    { id: "upload", label: "Upload & Process", icon: <Upload className="w-4 h-4" /> },
  ];

  return (
    <div className="flex justify-center">
      <div className="flex p-1 bg-gray-800 rounded-lg">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActive(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition ${
              active === tab.id ? "bg-gray-700 text-yellow-400" : "text-gray-300"
            }`}
          >
            {tab.icon}
            <span className="text-sm">{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
