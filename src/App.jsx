import { useState, useRef } from "react";
import "./App.css";

// -------------------------------------------------------------------
// SVG Icons (Zero external dependencies)
// -------------------------------------------------------------------

function IconLeaf({ size = 20, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
      <path d="M2 21c0-3 1.85-5.36 5.08-6" />
    </svg>
  );
}

function IconUpload({ size = 24, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

function IconCamera({ size = 20, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" />
      <circle cx="12" cy="13" r="3" />
    </svg>
  );
}

function IconDroplet({ size = 18, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
    </svg>
  );
}

function IconSun({ size = 18, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
  );
}

function IconCloudRain({ size = 18, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="16" y1="13" x2="16" y2="21" />
      <line x1="8" y1="13" x2="8" y2="21" />
      <line x1="12" y1="15" x2="12" y2="23" />
      <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25" />
    </svg>
  );
}

function IconSatellite({ size = 18, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M13 7 9 3 5 7l4 4" />
      <path d="m17 11 4 4-4 4-4-4" />
      <path d="m8 12 4 4 6-6-4-4Z" />
      <path d="m16 8 3-3" />
      <path d="M9 21a6 6 0 0 0-6-6" />
    </svg>
  );
}

function IconShield({ size = 18, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

function IconAlertTriangle({ size = 18, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

function IconSparkles({ size = 18, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z" />
    </svg>
  );
}

function IconSend({ size = 16, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

function IconPin({ size = 14, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  );
}

function IconWaterTap({ size = 18, color = "currentColor" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 2h6v3H9z" />
      <path d="M12 5v5" />
      <path d="M4 14h16a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-1a2 2 0 0 1 2-2z" />
      <path d="M12 19v2" />
    </svg>
  );
}

// -------------------------------------------------------------------
// Main Component
// -------------------------------------------------------------------

function App() {
  const [analysis, setAnalysis] = useState("");
  const [result, setResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [imagePreview, setImagePreview] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState("");
  const [chatReply, setChatReply] = useState("");
  const [isChatting, setIsChatting] = useState(false);
  const [chatError, setChatError] = useState("");
  const [language, setLanguage] = useState("hinglish");
  const [soilMoisture, setSoilMoisture] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);

  const fileInputRef = useRef(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  // Handle image selection
  const handleFile = (file) => {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setAnalysis("Please upload an image file (PNG, JPG, JPEG, WEBP).");
      return;
    }
    setSelectedFile(file);
    setImagePreview(URL.createObjectURL(file));
    setAnalysis(`Selected "${file.name}". Click "Analyze Crop" to evaluate.`);
  };

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  // Reset image
  const handleResetImage = (e) => {
    if (e) e.stopPropagation();
    setSelectedFile(null);
    setImagePreview("");
    setAnalysis("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // POST /analyze
  const handleAnalyze = async () => {
    if (!selectedFile) {
      setAnalysis("Please select or upload a crop leaf image first.");
      return;
    }

    setAnalysis("Running Harimitra Disease AI, weather telemetry & Sentinel-2 analysis...");
    setIsAnalyzing(true);

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("soil_moisture", soilMoisture !== "" ? soilMoisture : "62.0");
    formData.append("latitude", latitude !== "" ? latitude : "24.5854");
    formData.append("longitude", longitude !== "" ? longitude : "73.7125");
    formData.append("language", language);

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
        `Analysis complete: ${data.analysis?.replaceAll("___", " ") || "Processed"} | Confidence: ${(data.confidence * 100).toFixed(1)}%`
      );
    } catch (error) {
      console.error("Analyze error:", error);
      setAnalysis("Unable to connect to backend server. Please verify backend status.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // POST /chat
  const handleChat = async (customQuestion) => {
    if (isChatting) return;
    const questionText = (typeof customQuestion === "string" ? customQuestion : message).trim();
    if (!questionText) {
      setChatError("Please enter a question.");
      return;
    }

    setChatError("");
    setChatReply("Thinking...");
    setIsChatting(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: questionText,
          language: language,
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
    } finally {
      setIsChatting(false);
    }
  };

  // Rain probability resolver from Open-Meteo
  const rainProbability =
    result?.weather?.rain_probability != null
      ? result.weather.rain_probability
      : result?.weather?.forecast?.precipitation_probability_max?.[0] != null
        ? result.weather.forecast.precipitation_probability_max[0]
        : null;

  return (
    <div className="km-dashboard">
      {/* ===================================================================
          1. HEADER / HERO
          =================================================================== */}
      <header className="km-hero-card">
        <div className="km-hero-inner">
          <div className="km-hero-brand">
            <div className="km-logo-icon">
              <IconLeaf size={28} color="#ffffff" />
            </div>
            <div className="km-hero-title-group">
              <div className="km-hero-title-row">
                <h1 className="km-hero-title">KrishiMitra AI</h1>
                <span className="km-hero-badge">Your Smart Farming Companion</span>
              </div>
              <p className="km-hero-subtitle">
                AI-powered crop disease detection, soil insights &amp; farm advisory
              </p>
            </div>
          </div>

          {/* Bilingual Switcher */}
          <div className="km-lang-switcher">
            <button
              type="button"
              className={`km-lang-btn ${language === "hinglish" ? "active" : ""}`}
              onClick={() => setLanguage("hinglish")}
            >
              हिंदी / Hinglish
            </button>
            <button
              type="button"
              className={`km-lang-btn ${language === "english" ? "active" : ""}`}
              onClick={() => setLanguage("english")}
            >
              English
            </button>
          </div>
        </div>
      </header>

      {/* ===================================================================
          2. DIAGNOSTICS SECTION (3-column layout)
          =================================================================== */}
      <section className="km-card km-diagnostics-card">
        <div className="km-section-header">
          <div>
            <h2 className="km-section-title">
              <IconCamera size={20} color="#15803d" />
              Crop Disease Diagnostics &amp; Field Telemetry
            </h2>
            <p className="km-section-subtitle">
              Upload a clear leaf photo and provide farm parameters to get AI-powered insights.
            </p>
          </div>
          {selectedFile && (
            <span className="km-badge km-badge-green">
              ✓ Ready ({selectedFile.name} • {(selectedFile.size / 1024).toFixed(1)} KB)
            </span>
          )}
        </div>

        <div className="km-diagnostics-grid">
          {/* LEFT COLUMN: Large drag-and-drop leaf image upload zone */}
          <div
            className={`km-dropzone ${isDragOver ? "drag-active" : ""}`}
            onDragOver={handleDragOver}
            onDragEnter={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFile(e.target.files[0]);
                }
              }}
            />
            <div className="km-dropzone-icon-wrap">
              <IconUpload size={26} color="#15803d" />
            </div>
            <div className="km-dropzone-title">Click or Drag &amp; Drop a Leaf Photo</div>
            <div className="km-dropzone-desc">
              Upload healthy or diseased leaf images for pathology diagnosis
            </div>
            <div className="km-dropzone-specs">
              Supported: JPG, JPEG, PNG, WEBP • Target: 128×128px or higher
            </div>
          </div>

          {/* CENTER COLUMN: Image preview panel */}
          <div className="km-preview-panel">
            {imagePreview ? (
              <div className="km-preview-content">
                <img
                  src={imagePreview}
                  alt="Selected crop leaf preview"
                  className="km-preview-img"
                />
                <div className="km-preview-meta">
                  <div style={{ fontSize: "13px", fontWeight: "700", color: "#14532d" }}>
                    Leaf Image Loaded
                  </div>
                  <div style={{ fontSize: "12px", color: "#64748b", marginTop: "2px" }}>
                    {selectedFile?.name} ({(selectedFile?.size / 1024).toFixed(1)} KB)
                  </div>
                  <button
                    type="button"
                    onClick={handleResetImage}
                    style={{
                      marginTop: "8px",
                      background: "transparent",
                      color: "#dc2626",
                      border: "1px solid #fca5a5",
                      borderRadius: "6px",
                      padding: "4px 10px",
                      fontSize: "12px",
                      fontWeight: "600",
                      cursor: "pointer",
                    }}
                  >
                    Change Photo
                  </button>
                </div>
              </div>
            ) : (
              <div className="km-preview-empty">
                <div className="km-preview-empty-icon">
                  <IconCamera size={26} color="#94a3b8" />
                </div>
                <div style={{ fontSize: "14px", fontWeight: "700", color: "#475569" }}>
                  No image selected
                </div>
                <div style={{ fontSize: "12px", color: "#94a3b8", marginTop: "4px", maxWidth: "200px" }}>
                  Upload a leaf image to begin analysis
                </div>
              </div>
            )}
          </div>

          {/* RIGHT COLUMN: Parameters & Analyze button */}
          <div className="km-params-panel km-diagnostics-col-params">
            <div>
              {/* 3. Small Informational Badge */}
              <div className="km-location-badge">
                <span className="km-location-badge-icon">
                  <IconPin size={15} color="#059669" />
                </span>
                <div>
                  <strong>Default Demo Location:</strong> Udaipur, Rajasthan (24.5854°N, 73.7125°E) • Baseline Moisture: 62%
                </div>
              </div>

              <div className="km-form-group">
                <label className="km-form-label">
                  <IconDroplet size={14} color="#0284c7" />
                  Soil Moisture (%)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  className="km-input"
                  value={soilMoisture}
                  onChange={(e) => setSoilMoisture(e.target.value)}
                  placeholder="e.g. 62"
                />
              </div>

              <div className="km-form-group">
                <label className="km-form-label">
                  <IconPin size={14} color="#16a34a" />
                  Latitude
                </label>
                <input
                  type="number"
                  step="any"
                  className="km-input"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  placeholder="e.g. 24.5854"
                />
              </div>

              <div className="km-form-group">
                <label className="km-form-label">
                  <IconPin size={14} color="#16a34a" />
                  Longitude
                </label>
                <input
                  type="number"
                  step="any"
                  className="km-input"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  placeholder="e.g. 73.7125"
                />
              </div>
            </div>

            <div>
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="km-btn-primary"
              >
                {isAnalyzing ? (
                  <>
                    <span className="km-spinner" />
                    <span>Analyzing Crop...</span>
                  </>
                ) : (
                  <>
                    <IconSparkles size={16} color="#ffffff" />
                    <span>Analyze Crop</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Status / Alert Bar */}
        {analysis && (
          <div
            style={{
              marginTop: "16px",
              padding: "10px 14px",
              borderRadius: "8px",
              background: result ? "#ecfdf5" : "#f0fdf4",
              border: `1px solid ${result ? "#a7f3d0" : "#bbf7d0"}`,
              color: "#166534",
              fontSize: "13px",
              fontWeight: "500",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <span>{result ? "✓" : "ℹ"}</span>
            <span>{analysis}</span>
          </div>
        )}
      </section>

      {/* ===================================================================
          4. UNIFIED TELEMETRY & DIAGNOSTICS OVERVIEW
          =================================================================== */}
      <section className="km-telemetry-section">
        <div className="km-section-header">
          <div>
            <h2 className="km-section-title">
              <IconShield size={20} color="#15803d" />
              Unified Telemetry &amp; Diagnostics Overview
            </h2>
            <p className="km-section-subtitle">
              Integrated multi-modal intelligence across computer vision, in-situ soil records, meteorological forecasts &amp; Sentinel-2 satellite observation.
            </p>
          </div>
          <span className="km-badge km-badge-gray">
            {result ? "Live Telemetry Loaded" : "Awaiting Analysis Input"}
          </span>
        </div>

        {/* FIRST ROW: Detected Crop Condition & Overall Farm Risk */}
        <div className="km-telemetry-row-1">
          {/* Card 1: Detected Crop Condition */}
          <div
            className="km-metric-card"
            style={{
              borderLeft: "5px solid #16a34a",
              background: "#ffffff",
            }}
          >
            <div className="km-metric-header">
              <span className="km-metric-label">
                <IconLeaf size={16} color="#16a34a" />
                Detected Crop Condition
              </span>
              {result && (
                <span className="km-badge km-badge-green">
                  Class #{result.class_index}
                </span>
              )}
            </div>

            <div style={{ margin: "6px 0 4px" }}>
              {result ? (
                <div
                  style={{
                    fontSize: "22px",
                    fontWeight: "800",
                    color: "#14532d",
                    lineHeight: "1.25",
                    wordBreak: "break-word",
                  }}
                >
                  {result.analysis?.replaceAll("___", " ") || "No condition detected"}
                </div>
              ) : (
                <div style={{ fontSize: "16px", fontWeight: "600", color: "#94a3b8" }}>
                  Awaiting analysis
                </div>
              )}
            </div>

            <div className="km-metric-sub">
              {result
                ? `Harimitra Model Confidence: ${(result.confidence * 100).toFixed(2)}%`
                : "Upload a crop leaf photo to run Harimitra AI inference."}
            </div>
          </div>

          {/* Card 2: Overall Farm Risk */}
          <div
            className="km-metric-card"
            style={{
              borderLeft: `5px solid ${getRiskColor(result?.risk?.overall_risk)}`,
              background: "#ffffff",
            }}
          >
            <div className="km-metric-header">
              <span className="km-metric-label">
                <IconAlertTriangle size={16} color={getRiskColor(result?.risk?.overall_risk)} />
                Overall Farm Risk
              </span>
              {result?.risk?.overall_risk && (
                <span
                  className="km-badge"
                  style={{
                    background: getRiskBg(result.risk.overall_risk),
                    color: getRiskColor(result.risk.overall_risk),
                    border: `1px solid ${getRiskColor(result.risk.overall_risk)}33`,
                  }}
                >
                  {result.risk.overall_risk}
                </span>
              )}
            </div>

            <div style={{ margin: "6px 0 4px" }}>
              {result ? (
                <div
                  style={{
                    fontSize: "22px",
                    fontWeight: "800",
                    color: getRiskColor(result.risk.overall_risk),
                    lineHeight: "1.25",
                  }}
                >
                  {result.risk.overall_risk}
                </div>
              ) : (
                <div style={{ fontSize: "16px", fontWeight: "600", color: "#94a3b8" }}>
                  Awaiting analysis
                </div>
              )}
            </div>

            <div className="km-metric-sub">
              {result?.risk
                ? `Disease: ${result.risk.disease_risk} • Moisture: ${result.risk.water_risk} • Weather: ${result.risk.weather_risk}`
                : "Computed from disease severity, moisture & forecast telemetry."}
            </div>
          </div>
        </div>

        {/* SECOND ROW: 5 Metric Cards */}
        <div className="km-telemetry-row-2">
          {/* 1. Soil Moisture */}
          <div className="km-metric-card">
            <div className="km-metric-header">
              <span className="km-metric-label">
                <IconDroplet size={15} color="#0284c7" />
                Soil Moisture
              </span>
            </div>
            <div className="km-metric-value" style={{ color: "#0284c7" }}>
              {result ? `${result.soil_moisture}%` : "—"}
            </div>
            <p className="km-metric-sub">
              {result ? "Root-zone calibrated" : "Awaiting analysis"}
            </p>
          </div>

          {/* 2. Irrigation Advice */}
          <div className="km-metric-card">
            <div className="km-metric-header">
              <span className="km-metric-label">
                <IconWaterTap size={15} color="#059669" />
                Irrigation Advice
              </span>
            </div>
            <div
              style={{
                fontSize: "15px",
                fontWeight: "700",
                color: result?.irrigation?.includes("Not Required") ? "#15803d" : result?.irrigation ? "#d97706" : "#0f172a",
                lineHeight: "1.3",
                margin: "6px 0 4px",
              }}
            >
              {result ? result.irrigation : "—"}
            </div>
            <p className="km-metric-sub">
              {result ? "Automated threshold" : "Awaiting analysis"}
            </p>
          </div>

          {/* 3. Weather & Temperature */}
          <div className="km-metric-card">
            <div className="km-metric-header">
              <span className="km-metric-label">
                <IconSun size={15} color="#ea580c" />
                Weather &amp; Temperature
              </span>
            </div>
            <div className="km-metric-value" style={{ color: "#ea580c" }}>
              {result?.weather?.temperature != null ? `${result.weather.temperature}°C` : "—"}
            </div>
            <p className="km-metric-sub">
              {result?.weather?.humidity != null
                ? `Humidity: ${result.weather.humidity}% (Open-Meteo)`
                : "Awaiting analysis"}
            </p>
          </div>

          {/* 4. Rain Forecast */}
          <div className="km-metric-card">
            <div className="km-metric-header">
              <span className="km-metric-label">
                <IconCloudRain size={15} color="#2563eb" />
                Rain Forecast
              </span>
            </div>
            <div className="km-metric-value" style={{ color: "#2563eb" }}>
              {rainProbability != null ? `${rainProbability}%` : "—"}
            </div>
            <p className="km-metric-sub">
              {result ? "Precipitation probability" : "Awaiting analysis"}
            </p>
          </div>

          {/* 5. SATELLITE NDVI (Sentinel-2 / Google Earth Engine) */}
          <div
            className="km-metric-card"
            style={{
              borderTop: "3px solid #059669",
              background: "#ffffff",
            }}
          >
            <div className="km-metric-header">
              <span className="km-metric-label">
                <IconSatellite size={15} color="#059669" />
                Satellite NDVI
              </span>
              <span className="km-badge km-badge-green" style={{ fontSize: "10px", padding: "1px 6px" }}>
                Sentinel-2
              </span>
            </div>

            <div>
              <div
                style={{
                  fontSize: "22px",
                  fontWeight: "800",
                  color: "#059669",
                  lineHeight: "1.2",
                  margin: "4px 0 2px",
                }}
              >
                {result?.satellite?.available && typeof result.satellite.ndvi_mean === "number"
                  ? result.satellite.ndvi_mean.toFixed(2)
                  : result
                    ? "Unavailable"
                    : "—"}
              </div>
              <div style={{ fontSize: "11px", color: "#64748b" }}>
                Mean vegetation index
              </div>
            </div>

            <div
              style={{
                borderTop: "1px solid #f1f5f9",
                paddingTop: "6px",
                marginTop: "6px",
                fontSize: "11px",
                color: "#475569",
                lineHeight: "1.4",
              }}
            >
              {result?.satellite?.observation_date && (
                <div>
                  <strong>Observation:</strong> {formatObservationDate(result.satellite.observation_date)}
                </div>
              )}
              {result?.satellite?.cloud_percentage != null && (
                <div>
                  <strong>Cloud:</strong> {result.satellite.cloud_percentage.toFixed(1)}%
                </div>
              )}
              <div style={{ color: "#64748b", marginTop: "2px" }}>
                <strong>Source:</strong> {result?.satellite?.source || "Sentinel-2 / Google Earth Engine"}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================
          DEEP INTELLIGENCE PANELS (Conditional on result)
          =================================================================== */}
      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px", marginBottom: "24px" }}>
          {/* 7. AI AGRICULTURAL ADVISORY */}
          <section className="km-card km-advisory-card">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "8px",
                marginBottom: "14px",
                borderBottom: "1px solid #e2e8f0",
                paddingBottom: "10px",
              }}
            >
              <div>
                <h2
                  style={{
                    margin: 0,
                    color: "#14532d",
                    fontSize: "19px",
                    fontWeight: "800",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <IconSparkles size={20} color="#15803d" />
                  AI Agricultural Advisory
                </h2>
                <p style={{ margin: "3px 0 0", color: "#64748b", fontSize: "13px" }}>
                  Agronomic recommendations generated from Harimitra disease alert, soil health card &amp; weather telemetry
                </p>
              </div>
              <span className="km-badge km-badge-green">
                Gemini Primary • OpenRouter Fallback
              </span>
            </div>

            <div className="km-advisory-container">
              {renderFormattedAdvisory(
                language === "hinglish"
                  ? (result.advisory_hi || result.advisory)
                  : (result.advisory_en || result.advisory),
                language
              )}
            </div>
          </section>

          {/* 8. ALTERNATIVE CROP RECOMMENDATIONS */}
          <section className="km-card" style={{ padding: "22px 24px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "8px",
                marginBottom: "14px",
              }}
            >
              <div>
                <h2
                  style={{
                    margin: 0,
                    color: "#166534",
                    fontSize: "19px",
                    fontWeight: "800",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <IconLeaf size={20} color="#166534" />
                  Alternative Crop Recommendations
                </h2>
                <p style={{ margin: "3px 0 0", color: "#64748b", fontSize: "13px" }}>
                  Current Farm Crop:{" "}
                  <strong style={{ color: "#166534" }}>
                    {result.crop_recommendations?.current_crop || "Tomato"}
                  </strong>{" "}
                  • Ranked by deterministic agronomic suitability
                </p>
              </div>
              {result.crop_recommendations?.data_completeness && (
                <span className="km-badge km-badge-green">
                  Completeness: {result.crop_recommendations.data_completeness}
                </span>
              )}
            </div>

            {result.crop_recommendations?.recommendations?.length > 0 ? (
              <div className="km-crops-grid">
                {result.crop_recommendations.recommendations.map((crop, index) => (
                  <div key={index} className="km-crop-card">
                    <div>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          marginBottom: "8px",
                        }}
                      >
                        <h3
                          style={{
                            margin: 0,
                            color: "#14532d",
                            fontSize: "17px",
                            fontWeight: "700",
                          }}
                        >
                          {crop.crop}
                        </h3>
                        <span
                          className={`km-badge ${
                            crop.suitability === "HIGH"
                              ? "km-badge-green"
                              : crop.suitability === "MODERATE"
                                ? "km-badge-amber"
                                : "km-badge-red"
                          }`}
                        >
                          {crop.suitability} {language === "english" ? "SUITABILITY" : "उपयुक्तता"}
                        </span>
                      </div>

                      <div style={{ fontSize: "13px", color: "#475569", marginBottom: "10px" }}>
                        Match Score:{" "}
                        <strong style={{ color: "#166534", fontSize: "15px" }}>
                          {crop.score}/100
                        </strong>
                      </div>

                      {crop.reasons?.length > 0 && (
                        <div>
                          <strong style={{ fontSize: "12px", color: "#334155" }}>
                            {language === "english" ? "Agronomic Rationale:" : "सिफारिश का कारण (Agronomic Rationale):"}
                          </strong>
                          <ul
                            style={{
                              margin: "4px 0 0",
                              paddingLeft: "16px",
                              fontSize: "12px",
                              color: "#4b5563",
                              lineHeight: "1.5",
                            }}
                          >
                            {crop.reasons.map((reason, rIdx) => (
                              <li key={rIdx}>{formatCropReason(reason, language)}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ margin: 0, color: "#64748b", fontSize: "14px" }}>
                {language === "english"
                  ? "No alternative crop recommendations available for current telemetry."
                  : "वर्तमान परिस्थितियों के लिए कोई वैकल्पिक फसल सिफारिश उपलब्ध नहीं है।"}
              </p>
            )}

            {result.crop_recommendations?.limitations?.length > 0 && (
              <div
                style={{
                  marginTop: "16px",
                  padding: "10px 14px",
                  background: "#fffbeb",
                  borderRadius: "8px",
                  border: "1px solid #fde68a",
                  color: "#92400e",
                  fontSize: "12px",
                }}
              >
                <strong>{language === "english" ? "Data Limitations:" : "डेटा सीमाएं (Data Limitations):"}</strong>
                <ul style={{ margin: "4px 0 0", paddingLeft: "16px" }}>
                  {result.crop_recommendations.limitations.map((lim, lIdx) => (
                    <li key={lIdx}>{formatCropLimitation(lim, language)}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          {/* 8. SOIL HEALTH CARD (12 Parameters Grouped) */}
          <section className="km-card" style={{ padding: "22px 24px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "8px",
                marginBottom: "18px",
                borderBottom: "1px solid #e2e8f0",
                paddingBottom: "10px",
              }}
            >
              <div>
                <h2
                  style={{
                    margin: 0,
                    color: "#166534",
                    fontSize: "19px",
                    fontWeight: "800",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <IconDroplet size={20} color="#166534" />
                  Soil Health Card (12 Parameters)
                </h2>
                <p style={{ margin: "3px 0 0", color: "#64748b", fontSize: "13px" }}>
                  National Soil Health Card Scheme benchmark data • Udaipur District, Rajasthan
                </p>
              </div>
              <span className="km-badge km-badge-green">
                12 Parameters Loaded
              </span>
            </div>

            {/* Primary Macronutrients */}
            <div className="km-soil-group">
              <div className="km-soil-group-title">
                <span>🌱</span> Primary Macronutrients
              </div>
              <div className="km-soil-grid-3">
                {[
                  ["Nitrogen (N)", "nitrogen"],
                  ["Phosphorus (P)", "phosphorus"],
                  ["Potassium (K)", "potassium"],
                ].map(([label, key]) => renderSoilCard(label, key, result))}
              </div>
            </div>

            {/* Secondary & Micronutrients */}
            <div className="km-soil-group">
              <div className="km-soil-group-title">
                <span>🔬</span> Secondary &amp; Micronutrients
              </div>
              <div className="km-soil-grid-6">
                {[
                  ["Sulphur (S)", "sulfur"],
                  ["Zinc (Zn)", "zinc"],
                  ["Iron (Fe)", "iron"],
                  ["Copper (Cu)", "copper"],
                  ["Manganese (Mn)", "manganese"],
                  ["Boron (B)", "boron"],
                ].map(([label, key]) => renderSoilCard(label, key, result))}
              </div>
            </div>

            {/* Physical & Chemical */}
            <div className="km-soil-group">
              <div className="km-soil-group-title">
                <span>🧪</span> Physical &amp; Chemical
              </div>
              <div className="km-soil-grid-3">
                {[
                  ["Soil pH", "ph"],
                  ["Electrical Conductivity", "electrical_conductivity"],
                  ["Organic Carbon", "organic_carbon"],
                ].map(([label, key]) => renderSoilCard(label, key, result))}
              </div>
            </div>

            <p style={{ margin: "14px 0 0", fontSize: "11.5px", color: "#64748b" }}>
              Data source: Soil Health Card portal records for Rajasthan state, Udaipur district.
            </p>
          </section>

          {/* 9. AGRISTACK CARD */}
          <section className="km-card km-agristack-card">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "8px",
                marginBottom: "14px",
              }}
            >
              <div>
                <h2
                  style={{
                    margin: 0,
                    color: "#1e3a8a",
                    fontSize: "19px",
                    fontWeight: "800",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <span>🏛️</span>
                  Farm Context (AgriStack Format)
                </h2>
                <p style={{ margin: "3px 0 0", color: "#475569", fontSize: "13px" }}>
                  Digital Public Infrastructure for Agriculture • Farmer &amp; Plot Schema
                </p>
              </div>
              <span className="km-badge km-badge-amber">
                Demo / Synthetic Data
              </span>
            </div>

            <div className="km-agristack-grid">
              {[
                ["Farmer ID", result.agristack?.farmer_id || "KM-FARMER-001"],
                ["Farmer Name", result.agristack?.name],
                [
                  "Location",
                  result.agristack?.district && result.agristack?.state
                    ? `${result.agristack.district}, ${result.agristack.state}`
                    : null,
                ],
                ["Registered Crop", result.agristack?.farm?.crop],
                [
                  "Plot Area",
                  result.agristack?.farm?.area_acres != null
                    ? `${result.agristack.farm.area_acres} acres`
                    : null,
                ],
                ["Season", result.agristack?.farm?.season],
                ["Irrigation", result.agristack?.farm?.irrigation],
                ["Soil Texture", result.agristack?.farm?.soil_type],
              ].map(([label, value]) => (
                <div key={label} className="km-agristack-item">
                  <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "600" }}>
                    {label}
                  </div>
                  <div
                    style={{
                      marginTop: "3px",
                      fontSize: "14px",
                      fontWeight: "700",
                      color: "#1e3a8a",
                    }}
                  >
                    {value ?? "—"}
                  </div>
                </div>
              ))}
            </div>

            <p
              style={{
                margin: "14px 0 0",
                fontSize: "12px",
                color: "#1e40af",
                background: "#dbeafe",
                padding: "8px 12px",
                borderRadius: "8px",
                display: "inline-block",
              }}
            >
              Demo / Synthetic Data — not an official live AgriStack record.
            </p>
          </section>
        </div>
      )}

      {/* ===================================================================
          10. FARMER AI CHAT
          =================================================================== */}
      <section className="km-card km-chat-card">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "8px",
            marginBottom: "14px",
            borderBottom: "1px solid #e2e8f0",
            paddingBottom: "10px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                background: "#dcfce7",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#15803d",
              }}
            >
              <IconSparkles size={20} color="#15803d" />
            </div>
            <div>
              <h2
                style={{
                  margin: 0,
                  color: "#166534",
                  fontSize: "19px",
                  fontWeight: "800",
                }}
              >
                Farmer AI Chat
              </h2>
              <p style={{ margin: "2px 0 0", color: "#64748b", fontSize: "13px" }}>
                Ask agricultural questions in Hindi or English (Symptoms, precautions, fertilizer advice)
              </p>
            </div>
          </div>
          <span className="km-badge km-badge-green">
            {language === "hinglish" ? "Active: हिंदी / Hinglish" : "Active: English"}
          </span>
        </div>

        {/* Suggested Quick Questions */}
        <div className="km-chat-chips">
          {(language === "hinglish"
            ? [
                "टमाटर में पत्ती धब्बा रोग के क्या लक्षण हैं?",
                "ड्रिप सिंचाई में कितनी खाद देनी चाहिए?",
                "मिट्टी में नाइट्रोजन की कमी कैसे पूरी करें?",
              ]
            : [
                "What precautions to take for tomato target spot?",
                "How often should I run drip irrigation?",
                "How to treat nitrogen deficiency in soil?",
              ]
          ).map((chipText, idx) => (
            <button
              key={idx}
              type="button"
              className="km-chat-chip"
              onClick={() => {
                setMessage(chipText);
                if (chatError) setChatError("");
              }}
            >
              {chipText}
            </button>
          ))}
        </div>

        {/* Message Input & Button Bar */}
        <div className="km-chat-bar">
          <input
            type="text"
            className="km-chat-input"
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              if (chatError) setChatError("");
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (!isChatting) {
                  handleChat();
                }
              }
            }}
            placeholder={
              language === "english"
                ? "Ask a farming question (e.g., What precautions should I take for tomato crop?)..."
                : "अपनी फसल के बारे में पूछें (उदा. टमाटर की फसल में क्या सावधानी रखें?)..."
            }
          />
          <button
            type="button"
            onClick={() => handleChat()}
            disabled={isChatting}
            className="km-chat-btn"
          >
            {isChatting ? (
              <>
                <span className="km-spinner" />
                <span>Thinking...</span>
              </>
            ) : (
              <>
                <span>Ask AI</span>
                <IconSend size={15} color="#ffffff" />
              </>
            )}
          </button>
        </div>

        {chatError && (
          <p
            className="km-chat-error"
            style={{
              margin: "6px 0 0",
              color: "#dc2626",
              fontSize: "13px",
              fontWeight: "500",
            }}
          >
            {chatError}
          </p>
        )}

        {/* Assistant Response Bubble */}
        {chatReply && (
          <div className="km-chat-bubble">
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
                fontWeight: "700",
                fontSize: "13px",
                color: "#166534",
              }}
            >
              <IconSparkles size={16} color="#16a34a" />
              <span>KrishiMitra Assistant</span>
            </div>
            <div
              style={{
                color: "#1e293b",
                lineHeight: "1.6",
                fontSize: "14px",
              }}
            >
              {isChatting && chatReply === "Thinking..." ? (
                <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#15803d" }}>
                  <span className="km-spinner" />
                  <span>Thinking...</span>
                </div>
              ) : (
                renderFormattedChatReply(chatReply)
              )}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

// -------------------------------------------------------------------
// Helper Functions & Micro-Components
// -------------------------------------------------------------------

function renderSoilCard(label, key, result) {
  const item = result.soil_profile?.[key];
  const level = typeof item === "object" ? item?.level : item;
  const value = typeof item === "object" ? item?.value : null;

  const badgeClass = getSoilBadgeClass(level);

  return (
    <div key={key} className="km-soil-item">
      <div style={{ fontSize: "12px", color: "#475569", fontWeight: "600" }}>
        {label}
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "6px",
        }}
      >
        <span className={`km-badge ${badgeClass}`}>
          {level ?? "—"}
        </span>
        {value != null && value !== "" && (
          <span style={{ fontSize: "11px", color: "#64748b", fontWeight: "500" }}>
            Val: {value}
          </span>
        )}
      </div>
    </div>
  );
}

function getSoilBadgeClass(level) {
  if (!level || level === "—" || level === "--") {
    return "km-badge-gray";
  }
  const l = String(level).trim().toLowerCase();
  // Sufficient / Neutral / High / Optimal -> green
  if (
    l.includes("sufficient") ||
    l.includes("neutral") ||
    l.includes("high") ||
    l.includes("optimal")
  ) {
    return "km-badge-green";
  }
  // Medium / Moderate -> amber
  if (l.includes("medium") || l.includes("moderate")) {
    return "km-badge-amber";
  }
  // Deficient / Low / Saline / Acidic / Alkaline -> red
  if (
    l.includes("deficient") ||
    l.includes("low") ||
    l.includes("saline") ||
    l.includes("alkaline") ||
    l.includes("acidic")
  ) {
    return "km-badge-red";
  }
  return "km-badge-gray";
}

function getRiskColor(risk) {
  if (!risk) return "#64748b";
  const r = String(risk).toUpperCase();
  if (r === "HIGH") return "#dc2626";
  if (r === "MEDIUM") return "#d97706";
  if (r === "LOW") return "#16a34a";
  return "#64748b";
}

function getRiskBg(risk) {
  if (!risk) return "#f1f5f9";
  const r = String(risk).toUpperCase();
  if (r === "HIGH") return "#fee2e2";
  if (r === "MEDIUM") return "#fef3c7";
  if (r === "LOW") return "#dcfce7";
  return "#f1f5f9";
}

function formatObservationDate(dateStr) {
  if (!dateStr) return "—";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

// Inline Markdown Bold & Text formatter
function formatInlineText(text) {
  if (!text) return "";
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} style={{ color: "#14532d", fontWeight: "700" }}>
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

function formatCropReason(reason, language) {
  if (!reason || language === "english") return reason;

  const r = reason.trim();

  // Soil pH
  if (r === "Soil pH is reported as neutral.") {
    return "मिट्टी का pH सामान्य (neutral) स्तर पर है।";
  }
  if (r === "Soil pH is reported as alkaline.") {
    return "मिट्टी का pH क्षारीय (alkaline) स्तर पर है।";
  }

  // Soil moisture
  if (r === "Current soil moisture is within the crop's broad suitable range.") {
    return "वर्तमान मिट्टी की नमी फसल के उपयुक्त दायरे में है।";
  }
  if (r === "Current soil moisture is slightly outside the broad suitable range.") {
    return "वर्तमान मिट्टी की नमी उपयुक्त दायरे से थोड़ी बाहर है।";
  }
  if (r === "Current soil moisture is outside the broad suitable range.") {
    return "वर्तमान मिट्टी की नमी उपयुक्त दायरे से बाहर है।";
  }

  // Rainfall
  const rainMatch = r.match(/Available rainfall probability data was considered \((\d+)%\)\./);
  if (rainMatch) {
    return `उपलब्ध वर्षा संभावना डेटा (${rainMatch[1]}%) को ध्यान में रखा गया।`;
  }

  // NPK
  if (r === "Available soil NPK values were considered for crop suitability.") {
    return "फसल उपयुक्तता के लिए उपलब्ध मिट्टी NPK मानों को ध्यान में रखा गया।";
  }

  return reason;
}

function formatCropLimitation(limitation, language) {
  if (!limitation || language === "english") return limitation;

  const l = limitation.trim();

  const phUnmappedMatch = l.match(/Soil pH category '(.*?)' is not mapped\./);
  if (phUnmappedMatch) {
    return `मिट्टी pH श्रेणी '${phUnmappedMatch[1]}' मैप नहीं है।`;
  }
  if (l === "Soil pH category is unavailable." || l === "Soil pH is unavailable.") {
    return "मिट्टी का pH उपलब्ध नहीं है।";
  }
  if (l === "Current soil moisture is unavailable.") {
    return "वर्तमान मिट्टी की नमी उपलब्ध नहीं है।";
  }
  if (l === "Weather data is unavailable.") {
    return "मौसम डेटा उपलब्ध नहीं है।";
  }
  if (l === "Soil NPK values are unavailable.") {
    return "मिट्टी NPK मान उपलब्ध नहीं हैं।";
  }

  return limitation;
}

function formatAdvisoryHeader(title, language) {
  if (!title) return title;
  const t = title.trim().toLowerCase();
  if (language === "hinglish") {
    if (t.includes("main risk") || t.includes("agricultural risk") || t.includes("identified risk")) {
      return "मुख्य जोखिम (Main Risk):";
    }
    if (t.includes("why the risk matters") || t.includes("why the risk is higher") || t.includes("risk factor") || t.includes("important factor")) {
      return "जोखिम क्यों महत्वपूर्ण है (Why the Risk Matters):";
    }
    if (t.includes("what to do now") || t.includes("practical action") || t.includes("action step") || t.includes("recommended action")) {
      return "अभी क्या करें (What to Do Now):";
    }
    if (t.includes("more information needed") || t.includes("additional information") || t.includes("more info")) {
      return "अतिरिक्त जानकारी की आवश्यकता (More Info Needed):";
    }
  } else if (language === "english") {
    if (t.includes("मुख्य जोखिम")) {
      return "Main Agricultural Risk:";
    }
    if (t.includes("जोखिम क्यों महत्वपूर्ण है") || t.includes("जोखिम के कारण")) {
      return "Why the Risk Matters:";
    }
    if (t.includes("अभी क्या करें") || t.includes("व्यावहारिक कदम")) {
      return "What to Do Now (Practical Actions):";
    }
    if (t.includes("अतिरिक्त जानकारी")) {
      return "More Information Needed:";
    }
  }
  return title;
}

// Custom Markdown parser for AI Advisory without raw symbols
function renderFormattedAdvisory(text, language = "hinglish") {
  if (!text) return <p>AI advisory is currently unavailable.</p>;

  const lines = text.split("\n");

  return lines.map((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) {
      return <div key={idx} style={{ height: "6px" }} />;
    }

    // Markdown headers (### or ## or #)
    if (trimmed.startsWith("#")) {
      const cleanHeader = trimmed.replace(/^#+\s*/, "").replace(/\*\*/g, "");
      return (
        <h4 key={idx} className="km-advisory-section-heading">
          <span>🌿</span>
          <span>{formatAdvisoryHeader(cleanHeader, language)}</span>
        </h4>
      );
    }

    // Bold section titles like **Main risk:** or **Practical actions:**
    const isSectionHeader =
      (trimmed.startsWith("**") && (trimmed.endsWith("**") || trimmed.endsWith(":**") || trimmed.endsWith("**:"))) ||
      (trimmed.endsWith(":") && !trimmed.startsWith("-") && !trimmed.startsWith("*") && !/^\d+\./.test(trimmed) && trimmed.length < 60);

    if (isSectionHeader) {
      const cleanTitle = trimmed.replace(/\*\*/g, "");
      return (
        <h4 key={idx} className="km-advisory-section-heading">
          <span>📌</span>
          <span>{formatAdvisoryHeader(cleanTitle, language)}</span>
        </h4>
      );
    }

    // Bullet items
    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      const content = trimmed.slice(2);
      return (
        <div key={idx} className="km-advisory-bullet">
          <span style={{ color: "#16a34a", fontWeight: "800", minWidth: "12px" }}>•</span>
          <span>{formatInlineText(content)}</span>
        </div>
      );
    }

    // Numbered items
    const numMatch = trimmed.match(/^(\d+)\.\s*(.*)/);
    if (numMatch) {
      const num = numMatch[1];
      const content = numMatch[2];
      return (
        <div key={idx} className="km-advisory-num-step">
          <span className="km-advisory-num-badge">{num}</span>
          <span>{formatInlineText(content)}</span>
        </div>
      );
    }

    // Regular paragraphs with inline bold parsed
    return (
      <p
        key={idx}
        style={{
          margin: "4px 0",
          fontSize: "13.5px",
          lineHeight: "1.55",
          color: "#334155",
        }}
      >
        {formatInlineText(trimmed)}
      </p>
    );
  });
}

// Formatted Chat Reply
function renderFormattedChatReply(text) {
  if (!text) return null;
  const lines = text.split("\n");

  return lines.map((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) {
      return <div key={idx} style={{ height: "6px" }} />;
    }

    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      return (
        <div key={idx} style={{ display: "flex", gap: "6px", margin: "3px 0", paddingLeft: "4px" }}>
          <span style={{ color: "#16a34a", fontWeight: "700" }}>•</span>
          <span>{formatInlineText(trimmed.slice(2))}</span>
        </div>
      );
    }

    const numMatch = trimmed.match(/^(\d+)\.\s*(.*)/);
    if (numMatch) {
      return (
        <div key={idx} style={{ display: "flex", gap: "6px", margin: "3px 0", paddingLeft: "4px" }}>
          <span style={{ color: "#16a34a", fontWeight: "700", minWidth: "16px" }}>{numMatch[1]}.</span>
          <span>{formatInlineText(numMatch[2])}</span>
        </div>
      );
    }

    return (
      <p key={idx} style={{ margin: "4px 0", lineHeight: "1.55" }}>
        {formatInlineText(trimmed)}
      </p>
    );
  });
}

export default App;
