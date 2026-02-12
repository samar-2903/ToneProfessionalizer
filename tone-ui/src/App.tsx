import React from "react";
import { BGPattern } from "@/components/ui/bg-pattern";

const API_BASE = import.meta.env.VITE_API_BASE || "/api";

type Tone = "corporate" | "academic" | "political";
type Theme = "light" | "dark";

export default function App() {
  const [theme, setTheme] = React.useState<Theme>(() => {
    const saved = localStorage.getItem("theme");
    return saved === "dark" ? "dark" : "light";
  });
  const [selectedTone, setSelectedTone] = React.useState<Tone>("corporate");
  const [inputText, setInputText] = React.useState("");
  const [outputText, setOutputText] = React.useState("");
  const [revisionCount, setRevisionCount] = React.useState(0);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");
  const [stateNarrative, setStateNarrative] = React.useState(
    "Select a tone and paste your text to begin."
  );
  const [copyLabel, setCopyLabel] = React.useState("Copy");

  React.useEffect(() => {
    if (theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  const canRefine = outputText.trim().length > 0;
  const canAct = inputText.trim().length > 0;

  async function callAPI(endpoint: string, data: { input_text: string; text_type: Tone }) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return (await response.json()) as { professional_text: string; text_type: Tone };
  }

  async function professionalize() {
    const trimmed = inputText.trim();
    if (!trimmed) {
      setError("Please enter some text to professionalize");
      return;
    }

    setLoading(true);
    setError("");
    setStateNarrative("Professionalizing tone...");

    try {
      const result = await callAPI("/professionalize", {
        input_text: trimmed,
        text_type: selectedTone,
      });
      setOutputText(result.professional_text);
      setRevisionCount(1);
      setStateNarrative("You can refine further or change the tone.");
    } catch {
      setError("Failed to professionalize text. Please try again.");
      setStateNarrative("Select a tone and paste your text to begin.");
    } finally {
      setLoading(false);
    }
  }

  async function refine() {
    if (!canRefine) {
      setError("No text to refine");
      return;
    }

    setLoading(true);
    setError("");
    setStateNarrative("Refining text...");

    try {
      const result = await callAPI("/refine", {
        input_text: outputText,
        text_type: selectedTone,
      });
      setOutputText(result.professional_text);
      setRevisionCount((v) => v + 1);
      setStateNarrative("You can refine further or change the tone.");
    } catch {
      setError("Failed to refine text. Please try again.");
      setStateNarrative("You can refine further or change the tone.");
    } finally {
      setLoading(false);
    }
  }

  function changeTone(tone: Tone) {
    setSelectedTone(tone);
    if (inputText.trim()) {
      void professionalize();
    }
  }

  function newText() {
    setInputText("");
    setOutputText("");
    setRevisionCount(0);
    setError("");
    setStateNarrative("Select a tone and paste your text to begin.");
  }

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(outputText);
      setCopyLabel("Copied.");
      setTimeout(() => setCopyLabel("Copy"), 2000);
    } catch {
      setError("Failed to copy text");
    }
  }

  function handleInputKeydown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.ctrlKey && e.shiftKey && e.key === "Enter") {
      e.preventDefault();
      if (canRefine) void refine();
    } else if (e.ctrlKey && e.key === "Enter") {
      e.preventDefault();
      void professionalize();
    } else if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void professionalize();
    }
  }

  React.useEffect(() => {
    if (inputText.trim()) {
      setStateNarrative("Ready to professionalize your text.");
    } else {
      setStateNarrative("Select a tone and paste your text to begin.");
    }
  }, [inputText]);

  return (
    <div className="app-root">
      <div className="container">
        <div className="theme-toggle">
          <button
            className={`theme-btn ${theme === "light" ? "active" : ""}`}
            onClick={() => setTheme("light")}
          >
            Light
          </button>
          <button
            className={`theme-btn ${theme === "dark" ? "active" : ""}`}
            onClick={() => setTheme("dark")}
          >
            Dark
          </button>
        </div>

        <header className="header">
          <h1 className="title">Tone Professionalizer</h1>
          <p className="subtitle">Transform your text with professional tone adjustments</p>
          <div className="state-narrative">{stateNarrative}</div>
        </header>

        <div className="tabs">
          {(["corporate", "academic", "political"] as Tone[]).map((tone) => (
            <button
              key={tone}
              className={`tab ${selectedTone === tone ? "active" : ""}`}
              onClick={() => changeTone(tone)}
            >
              {tone[0].toUpperCase() + tone.slice(1)}
            </button>
          ))}
        </div>

        <div className="columns">
          <section className="column">
            <div className="column-title">Original Text</div>
            <div className="purpose-hint">
              <span className="purpose-label">Purpose:</span>
              <select className="dropdown" style={{ width: "auto" }} defaultValue="general">
                <option value="general">General</option>
                <option value="email">Email</option>
                <option value="public-statement">Public statement</option>
              </select>
            </div>

            <div className="controls">
              <button
                className="button primary-button"
                onClick={professionalize}
                disabled={loading || !canAct}
              >
                Professionalize
              </button>
              <div className="keyboard-hint">Ctrl + Enter to process</div>
            </div>

            <div className="textarea-container">
              <textarea
                className="textarea"
                placeholder="Please paste your text here"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleInputKeydown}
              />
            </div>
          </section>

          <section className="column">
            <div className="column-title">
              <span>Professionalized Text</span>
              {revisionCount > 0 && (
                <span className="revision-counter">Revision {revisionCount}</span>
              )}
            </div>
            <div className="options">
              <button className="button" onClick={refine} disabled={loading || !canRefine}>
                Refine
              </button>
              <button className="button" onClick={professionalize} disabled={loading || !canAct}>
                Change tone
              </button>
              <button className="button" onClick={newText} disabled={loading}>
                New text
              </button>
              <div className="keyboard-hint">Ctrl + Shift + Enter to refine</div>
            </div>

            <div className="textarea-container">
              <div className="output-wrapper">
                <textarea
                  className="output-textarea"
                  readOnly
                  placeholder="Your professionalized text will appear here..."
                  value={outputText}
                />
                {outputText && (
                  <button className={`copy-button ${copyLabel === "Copied." ? "copied" : ""}`} onClick={copyToClipboard}>
                    {copyLabel}
                  </button>
                )}
              </div>
            </div>
          </section>
        </div>

        {error && <div className="error">{error}</div>}
        {loading && <div className="loading">Processing...</div>}
      </div>

      <div className="pattern-layer">
        <BGPattern variant="grid" mask="fade-edges" />
        <BGPattern
          variant="dots"
          mask="fade-center"
          size={18}
          fill="var(--pattern-color)"
          className="pattern-dots"
        />
        <BGPattern
          variant="diagonal-stripes"
          mask="fade-y"
          size={32}
          fill="var(--pattern-color-strong)"
          className="pattern-stripes"
        />
      </div>
    </div>
  );
}
