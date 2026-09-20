import { useState } from "react";

function App() {
  const [analysis, setAnalysis] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [imagePreview, setImagePreview] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState("");
  const [chatReply, setChatReply] = useState("");

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "30px",
        background: "#f0fdf4",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1 style={{ color: "#166534" }}>🌱 KrishiMitra AI</h1>
      <p>Your Smart Farming Companion</p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "20px",
          marginTop: "30px",
        }}
      >
        <div style={cardStyle}>
          <h2>🌿 Crop Health</h2>
          <p style={valueStyle}>Healthy</p>
          <p>Crop condition is good.</p>
        </div>

        <div style={cardStyle}>
          <h2>💧 Soil Moisture</h2>
          <p style={valueStyle}>62%</p>
          <p>Moisture level is suitable.</p>
        </div>

        <div style={cardStyle}>
          <h2>🌡️ Temperature</h2>
          <p style={valueStyle}>28°C</p>
          <p>Current field temperature.</p>
        </div>

        <div style={cardStyle}>
          <h2>🚰 Irrigation</h2>
          <p style={valueStyle}>Not Required</p>
          <p>Next check after 6 hours.</p>
        </div>
      </div>

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
          marginTop: "25px",
          marginBottom: "15px",
        }}
      />

      {imagePreview && (
        <img
          src={imagePreview}
          alt="Selected crop"
          style={{
            width: "100%",
            maxWidth: "400px",
            marginTop: "15px",
            borderRadius: "12px",
          }}
        />
      )}

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
          formData.append("soil_moisture", "62");

          try {
            const response = await fetch(
              `${import.meta.env.VITE_API_URL}/analyze`,
              {
                method: "POST",
                body: formData,
              },
            );

            if (!response.ok) {
              throw new Error(`Analysis failed: ${response.status}`);
            }

            const result = await response.json();

            setAnalysis(
              `Disease: ${result.analysis} | Confidence: ${(result.confidence * 100).toFixed(2)}% | Soil Moisture: ${result.soil_moisture}% | Irrigation: ${result.irrigation}`,
            );
          } catch (error) {
            setAnalysis("Backend se connection nahi ho pa raha.");
          } finally {
            setIsAnalyzing(false);
          }
        }}
        disabled={isAnalyzing}
        style={{
          display: "block",
          marginTop: "30px",
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

      {analysis && (
        <div
          style={{
            marginTop: "20px",
            padding: "18px",
            background: "#dcfce7",
            color: "#166534",
            borderRadius: "12px",
          }}
        >
          <h3>AI Analysis Result</h3>
          <p>{analysis}</p>
        </div>
      )}
      <div
        style={{
          marginTop: "30px",
          padding: "20px",
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
              const response = await fetch("http://127.0.0.1:8000/chat", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  message: message,
                }),
              });

              const result = await response.json();
              setChatReply(result.reply);
            } catch (error) {
              setChatReply("Gemma se connection nahi ho pa raha.");
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

export default App;
