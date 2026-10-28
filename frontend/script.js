
const form = document.getElementById("research-form");
const topicInput = document.getElementById("topic");
const submitBtn = document.getElementById("submit-btn");
const buttonLabel = document.getElementById("button-label");
const charCount = document.getElementById("char-count");

const progress = document.getElementById("progress");
const progressTitle = document.getElementById("progress-title");
const progressText = document.getElementById("progress-text");
const errorPanel = document.getElementById("error-panel");
const errorMessage = document.getElementById("error-message");
const results = document.getElementById("results");

const reportContent = document.getElementById("report-content");
const copyButton = document.getElementById("copy-report");

let latestReport = "";

topicInput.addEventListener("input", () => {
  charCount.textContent = `${topicInput.value.length} / 500`;
});

function showError(message) {
  errorMessage.textContent = message;
  errorPanel.classList.remove("hidden");
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  buttonLabel.textContent = isLoading
    ? "Researching..."
    : "Start Research";

  progress.classList.toggle("hidden", !isLoading);

  if (isLoading) {
    progressTitle.textContent = "Research in progress...";
    progressText.textContent =
      "Searching the web, reading sources and preparing your report.";
  }
}

function displayText(elementId, value) {
  document.getElementById(elementId).textContent =
    typeof value === "string" ? value : "";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const topic = topicInput.value.trim();

  if (topic.length < 3) {
    showError("Please enter a research topic with at least 3 characters.");
    return;
  }

  errorPanel.classList.add("hidden");
  results.classList.add("hidden");
  setLoading(true);

  try {

    const response = await fetch("/api/research", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ topic }),
    });

    const rawResponse = await response.text();

    if (!rawResponse.trim()) {
      throw new Error(
        `Backend returned an empty response (HTTP ${response.status}). Check the FastAPI terminal.`
      );
    }

    let data;

    try {
      data = JSON.parse(rawResponse);
    } catch {
      console.error("Invalid backend response:", rawResponse);

      throw new Error(
        `Backend returned invalid JSON (HTTP ${response.status}). Check the FastAPI terminal.`
      );
    }

    if (!response.ok) {
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : `Backend error: HTTP ${response.status}`
      );
    }


    if (!response.ok) {
      throw new Error(
        data.detail || `Request failed (${response.status})`
      );
    }

    if (!data.success) {
      throw new Error("The research pipeline did not complete.");
    }

    document.getElementById("result-topic").textContent = data.topic;

    // Use textContent: model output is treated as text, not executable HTML.
    latestReport = data.report || "";
    reportContent.textContent = latestReport;

    displayText("search-content", data.search_results);
    displayText("scraped-content", data.scraped_content);
    displayText("feedback-content", data.feedback);

    progressTitle.textContent = "Research completed";
    progressText.textContent = "Your report is ready.";

    results.classList.remove("hidden");
    results.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

  } catch (error) {
    showError(
      error.message ||
      "Could not connect to the research backend. Check the server."
    );
  } finally {
    setLoading(false);
  }
});

copyButton.addEventListener("click", async () => {
  if (!latestReport) {
    showError("There is no report to copy yet.");
    return;
  }

  try {
    await navigator.clipboard.writeText(latestReport);
    copyButton.textContent = "Copied!";
    setTimeout(() => {
      copyButton.textContent = "Copy report";
    }, 1500);
  } catch {
    showError(
      "Clipboard access failed. Select and copy the report manually."
    );
  }
});
