import { useState } from "react";

function App() {
  const [analysis, setAnalysis] = useState("");
  const [result, setResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [imagePreview, setImagePreview] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState("");
  const [chatReply, setChatReply] = useState("");
  const [soilMoisture, setSoilMoisture] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "30px",
        background: "#f0fdf4",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          textAlign: "center",
          marginBottom: "20px",
        }}
      >
        <h1
          style={{
            color: "#166534",
            margin: 0,
            fontSize: "42px",
            lineHeight: "1.2",
          }}
        >
          🌱 KrishiMitra AI
        </h1>

        <p
          style={{
            margin: "10px 0 0",
            color: "#64748b",
            fontSize: "18px",
          }}
        >
          Your Smart Farming Companion
        </p>
      </div>

      {/* Dashboard Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "20px",
          marginTop: "30px",
        }}
      >
        {/* Crop Health */}
        <div style={cardStyle}>
          <h2>🌿 Crop Disease</h2>

          <p
            style={{
              ...valueStyle,
              fontSize: "22px",
              lineHeight: "1.2",
              overflowWrap: "anywhere",
            }}
          >
            {result ? result.analysis.replaceAll("___", " ") : "--"}
          </p>

          <p>
            {result
              ? `Confidence: ${(result.confidence * 100).toFixed(2)}%`
              : "Analyze your crop to detect disease."}
          </p>
        </div>

        {/* Soil Moisture */}
        <div style={cardStyle}>
          <h2>💧 Soil Moisture</h2>

          <p style={valueStyle}>{result ? `${result.soil_moisture}%` : "--"}</p>

          <p>
            {result
              ? "Current soil moisture from your analysis."
              : "Analyze your crop to see soil moisture."}
          </p>
        </div>

        {/* Temperature */}
        <div style={cardStyle}>
          <h2>🌡️ Temperature</h2>

          <p style={valueStyle}>Unavailable</p>

          <p>Live weather data is currently unavailable.</p>
        </div>

        {/* Overall Risk */}
        <div style={cardStyle}>
          <h2>⚠️ Overall Risk</h2>

          <p style={valueStyle}>{result?.risk?.overall_risk ?? "--"}</p>

          <p>
            {result
              ? "Risk calculated from current crop conditions."
              : "Analyze your crop to see risk."}
          </p>
        </div>

        {/* Satellite NDVI */}
        <div style={cardStyle}>
          <h2>🛰️ Satellite NDVI</h2>

          <p style={valueStyle}>
            {result?.satellite?.available
              ? result.satellite.ndvi_mean.toFixed(2)
              : "--"}
          </p>

          <p>
            {result?.satellite?.available
              ? `Observed: ${result.satellite.observation_date}`
              : "Satellite data unavailable."}
          </p>
        </div>

        {/* Irrigation */}
        <div style={cardStyle}>
          <h2>🚰 Irrigation</h2>

          <p style={valueStyle}>{result ? result.irrigation : "--"}</p>

          <p>
            {result
              ? "Based on current soil moisture."
              : "Analyze your crop to get irrigation advice."}
          </p>
        </div>
      </div>

      {/* Crop Image Upload */}
      <div
        style={{
          marginTop: "30px",
          padding: "24px",
          background: "white",
          borderRadius: "16px",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
        }}
      >
        <h2>📷 Upload Crop Image</h2>

        <input
          type="file"
          accept="image/*"
          onChange={(event) => {
            const file = event.target.files[0];

            if (file) {
              setSelectedFile(file);
              setImagePreview(URL.createObjectURL(file));
              setAnalysis(
                `Image "${file.name}" selected. Click Analyze Crop to continue.`,
              );
            }
          }}
          style={{
            display: "block",
            marginTop: "15px",
          }}
        />

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "15px",
            marginTop: "20px",
          }}
        >
          <div>
            <label>Soil Moisture (%)</label>
            <input
              type="number"
              min="0"
              max="100"
              value={soilMoisture}
              onChange={(event) => setSoilMoisture(event.target.value)}
              placeholder="e.g. 62"
              style={inputStyle}
            />
          </div>

          <div>
            <label>Latitude</label>
            <input
              type="number"
              step="any"
              value={latitude}
              onChange={(event) => setLatitude(event.target.value)}
              placeholder="e.g. 24.5854"
              style={inputStyle}
            />
          </div>

          <div>
            <label>Longitude</label>
            <input
              type="number"
              step="any"
              value={longitude}
              onChange={(event) => setLongitude(event.target.value)}
              placeholder="e.g. 73.7125"
              style={inputStyle}
            />
          </div>
        </div>

        {imagePreview && (
          <img
            src={imagePreview}
            alt="Selected crop"
            style={{
              width: "100%",
              maxWidth: "400px",
              marginTop: "20px",
              borderRadius: "12px",
            }}
          />
        )}

        {/* Analyze Button */}
        <button
          onClick={async () => {
            if (!selectedFile) {
              setAnalysis("Please select a crop image first.");
              return;
            }

            setAnalysis("Analyzing crop image...");
            setIsAnalyzing(true);

            const formData = new FormData();

            formData.append("file", selectedFile);
            formData.append("soil_moisture", soilMoisture);
            formData.append("latitude", latitude);
            formData.append("longitude", longitude);

            try {
              const response = await fetch(`${API_URL}/analyze`, {
                method: "POST",
                body: formData,
              });

              if (!response.ok) {
                throw new Error(`Analysis failed: ${response.status}`);
              }

              const data = await response.json();

              setResult(data);

              setAnalysis(
                `Disease: ${data.analysis} | Confidence: ${(data.confidence * 100).toFixed(2)}% | Soil Moisture: ${data.soil_moisture}% | Irrigation: ${data.irrigation}`,
              );
            } catch (error) {
              console.error("Analyze error:", error);
              setAnalysis("Backend se connection nahi ho pa raha.");
            } finally {
              setIsAnalyzing(false);
            }
          }}
          disabled={isAnalyzing}
          style={{
            display: "block",
            marginTop: "25px",
            padding: "12px 24px",
            background: "#15803d",
            color: "white",
            border: "none",
            borderRadius: "10px",
            fontSize: "16px",
            opacity: isAnalyzing ? 0.6 : 1,
            cursor: isAnalyzing ? "not-allowed" : "pointer",
          }}
        >
          {isAnalyzing ? "Analyzing..." : "Analyze Crop"}
        </button>

        {/* Status Message */}
        {analysis && !result && (
          <div
            style={{
              marginTop: "20px",
              padding: "15px",
              background: "#f0fdf4",
              color: "#166534",
              borderRadius: "12px",
            }}
          >
            <p style={{ margin: 0 }}>{analysis}</p>
          </div>
        )}
      </div>

      {/* AI Agricultural Advisory + Crop Recommendations */}
      {result && (
        <div
          style={{
            marginTop: "25px",
            padding: "24px",
            background: "white",
            borderRadius: "16px",
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
          }}
        >
          <h2
            style={{
              color: "#166534",
              marginTop: 0,
            }}
          >
            🤖 AI Agricultural Advisory
          </h2>

          <div
            style={{
              padding: "20px",
              background: "#f0fdf4",
              borderRadius: "12px",
              color: "#166534",
              lineHeight: "1.7",
              whiteSpace: "pre-wrap",
            }}
          >
            {result.advisory || "AI advisory is currently unavailable."}
          </div>

          <h2
            style={{
              color: "#166534",
              marginTop: "30px",
            }}
          >
            🌾 Recommended Crops
          </h2>

          {result.crop_recommendations?.recommendations?.length > 0 ? (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "15px",
              }}
            >
              {result.crop_recommendations.recommendations.map(
                (crop, index) => (
                  <div
                    key={index}
                    style={{
                      padding: "18px",
                      background: "#f0fdf4",
                      borderRadius: "12px",
                      color: "#166534",
                    }}
                  >
                    <h3 style={{ marginTop: 0 }}>🌱 {crop.crop}</h3>

                    <p>
                      <strong>Suitability:</strong> {crop.suitability}
                    </p>

                    <p>
                      <strong>Score:</strong> {crop.score}
                    </p>

                    {crop.reason && (
                      <p>
                        <strong>Reason:</strong> {crop.reason}
                      </p>
                    )}
                  </div>
                ),
              )}
            </div>
          ) : (
            <p>No crop recommendations are currently available.</p>
          )}

          {result.crop_recommendations?.limitations?.length > 0 && (
            <div
              style={{
                marginTop: "20px",
                padding: "15px",
                background: "#fffbeb",
                borderRadius: "10px",
                color: "#92400e",
              }}
            >
              <strong>⚠️ Data Limitations</strong>

              <ul>
                {result.crop_recommendations.limitations.map(
                  (limitation, index) => (
                    <li key={index}>{limitation}</li>
                  ),
                )}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Farmer AI Chat */}
      <div
        style={{
          marginTop: "30px",
          padding: "24px",
          background: "white",
          borderRadius: "16px",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
        }}
      >
        <h2>🤖 Ask KrishiMitra AI</h2>

        <input
          type="text"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask about your crop..."
          style={{
            width: "100%",
            padding: "12px",
            marginTop: "10px",
            border: "1px solid #bbf7d0",
            borderRadius: "8px",
            boxSizing: "border-box",
          }}
        />

        <button
          onClick={async () => {
            if (!message.trim()) {
              setChatReply("Please enter a question first.");
              return;
            }

            setChatReply("Thinking...");

            try {
              const response = await fetch(`${API_URL}/chat`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  message: message,
                }),
              });

              if (!response.ok) {
                throw new Error(`Chat failed: ${response.status}`);
              }

              const data = await response.json();

              setChatReply(data.reply);
            } catch (error) {
              console.error("Chat error:", error);
              setChatReply("KrishiMitra AI se connection nahi ho pa raha.");
            }
          }}
          style={{
            marginTop: "15px",
            padding: "12px 20px",
            background: "#15803d",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
          }}
        >
          Ask AI
        </button>

        {chatReply && (
          <p
            style={{
              marginTop: "15px",
              padding: "15px",
              background: "#f0fdf4",
              color: "#166534",
              borderRadius: "8px",
              whiteSpace: "pre-wrap",
            }}
          >
            {chatReply}
          </p>
        )}
      </div>
    </div>
  );
}

const cardStyle = {
  background: "white",
  padding: "24px",
  borderRadius: "16px",
  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
};

const valueStyle = {
  fontSize: "28px",
  fontWeight: "bold",
  color: "#15803d",
};

const resultBoxStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
  padding: "16px",
  background: "#f0fdf4",
  borderRadius: "12px",
  color: "#166534",
};

const inputStyle = {
  width: "100%",
  padding: "10px",
  marginTop: "6px",
  border: "1px solid #bbf7d0",
  borderRadius: "8px",
  boxSizing: "border-box",
  fontSize: "15px",
};

export default App;
