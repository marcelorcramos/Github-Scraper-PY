"use client";

import { useState } from "react";
import Header from "../components/Header/Header";
import Logs from "../components/Logs/Logs";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faStar } from "@fortawesome/free-solid-svg-icons";

export default function Home() {
  const [language, setLanguage] = useState("");
  const [tool, setTool] = useState("");
  const [minStars, setMinStars] = useState("");
  const [maxStars, setMaxStars] = useState("");
  const [numResults, setNumResults] = useState("");
  const [years, setYears] = useState("");
  const [months, setMonths] = useState("");
  const [logs, setLogs] = useState(null); 
  const [isLoading, setIsLoading] = useState(false); 

  const handleSearch = async () => {
    setIsLoading(true); 
    setLogs(null); 

    const queryParams = {
      language: language || undefined,
      num_results: numResults || undefined,
      min_stars: minStars || undefined,
      max_stars: maxStars || undefined,
      years: years || undefined,
      months: months || undefined,
    };

    const filteredQueryParams = Object.fromEntries(
      Object.entries(queryParams).filter(([_, value]) => value !== undefined && value !== "")
    );

    const queryString = new URLSearchParams(filteredQueryParams).toString();
    const url = `http://localhost:8000/search/?${queryString}`;

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      if (data.length === 0) {
        setLogs("No repositories found with the given criteria.");
      } else {
        setLogs(data);
      }
    } catch (error) {
      console.error("Fetch error:", error);
      setLogs(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#141313] text-[#A5A5A5] p-4">
      <Header />

      <main className="container mx-auto">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="space-y-4 w-1/3">
            <div>
              <label className="block text-lg font-medium mb-1">Language:</label>
              <input
                type="text"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full p-2 bg-[#333131] rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500"
                placeholder="Enter language"
              />
            </div>
            <div>
              <label className="block text-lg font-medium mb-1">Tools:</label>
              <input
                type="text"
                value={tool}
                onChange={(e) => setTool(e.target.value)}
                className="w-full p-2 bg-[#333131] rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500"
                placeholder="Enter tool"
              />
            </div>
            <button
              onClick={handleSearch}
              className="w-full p-2 bg-blue-700 rounded-lg hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-gray-500 text-white"
            >
              Search
            </button>
          </div>

          <div className="flex-1">
            <h3 className="text-lg font-medium mb-2">Specifications:</h3>
            <div className="border border-[#333131] rounded-lg p-4 grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <label className="flex items-center gap-2">
                  <span>Filter by Stars</span>
                  <FontAwesomeIcon icon={faStar} className="text-yellow-400" />
                </label>
                <div className="space-y-2">
                  <input
                    type="number"
                    value={minStars}
                    onChange={(e) => setMinStars(e.target.value)}
                    placeholder="Min Stars"
                    className="w-full p-2 bg-[#333131] rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500"
                  />
                  <input
                    type="number"
                    value={maxStars}
                    onChange={(e) => setMaxStars(e.target.value)}
                    placeholder="Max Stars"
                    className="w-full p-2 bg-[#333131] rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium">Number of Results</label>
                <input
                  type="number"
                  value={numResults}
                  onChange={(e) => setNumResults(e.target.value)}
                  placeholder="Enter number of results"
                  className="w-full p-2 bg-[#333131] rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500"
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium">Filter by Last Commit Date</label>
                <div className="space-y-2">
                  <input
                    type="number"
                    value={years}
                    onChange={(e) => setYears(e.target.value)}
                    placeholder="Years"
                    className="w-full p-2 bg-[#333131] rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500"
                  />
                  <input
                    type="number"
                    value={months}
                    onChange={(e) => setMonths(e.target.value)}
                    placeholder="Months"
                    className="w-full p-2 bg-[#333131] rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <Logs logs={logs} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
}