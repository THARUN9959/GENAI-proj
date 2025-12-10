const inputText = document.getElementById("inputText")
const wordCount = document.getElementById("wordCount")
const charCount = document.getElementById("charCount")
const sentenceCount = document.getElementById("sentenceCount")
const summaryRatio = document.getElementById("summaryRatio")
const ratioValue = document.getElementById("ratioValue")
const summarizeBtn = document.getElementById("summarizeBtn")
const themeToggle = document.getElementById("themeToggle")
const analyticsBtn = document.getElementById("analyticsBtn")
const analyticsModal = document.getElementById("analyticsModal")
const closeAnalyticsBtn = document.getElementById("closeAnalyticsBtn")

const emptyState = document.getElementById("emptyState")
const loadingState = document.getElementById("loadingState")
const errorState = document.getElementById("errorState")
const statsContainer = document.getElementById("statsContainer")
const resultsContent = document.getElementById("resultsContent")
const errorMessage = document.getElementById("errorMessage")
const summaryText = document.getElementById("summaryText")
const methodHint = document.getElementById("methodHint")

let currentMethod = "normal"

function initTheme() {
  const saved = localStorage.getItem("theme")
  if (saved === "dark" || (!saved && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
    document.body.classList.add("dark-mode")
  }
}

initTheme()

themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode")
  const isDark = document.body.classList.contains("dark-mode")
  localStorage.setItem("theme", isDark ? "dark" : "light")
})



// ... existing updateStats and other functions ...

function updateStats() {
  const text = inputText.value
  const words = text
    .trim()
    .split(/\s+/)
    .filter((w) => w.length > 0).length
  const chars = text.length
  const sentences = text.split(/[.!?]+/).filter((s) => s.trim().length > 0).length

  wordCount.textContent = words
  charCount.textContent = chars
  sentenceCount.textContent = sentences
}

inputText.addEventListener("input", updateStats)

summaryRatio.addEventListener("input", function () {
  ratioValue.textContent = this.value + "%"
})

function showState(state) {
  emptyState.classList.add("hidden")
  loadingState.classList.add("hidden")
  errorState.classList.add("hidden")
  statsContainer.classList.add("hidden")
  resultsContent.classList.add("hidden")

  if (state === "empty") emptyState.classList.remove("hidden")
  else if (state === "loading") loadingState.classList.remove("hidden")
  else if (state === "error") errorState.classList.remove("hidden")
  else if (state === "results") {
    statsContainer.classList.remove("hidden")
    resultsContent.classList.remove("hidden")
  }
}

const methodBtns = document.querySelectorAll(".method-btn")
const methodHints = {
  normal: "Standard summarization method",
  business_insights: "Business summary focused on key metrics, financial data, and strategic insights",
}

methodBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    methodBtns.forEach((b) => b.classList.remove("active"))
    btn.classList.add("active")
    currentMethod = btn.dataset.method
    methodHint.textContent = methodHints[currentMethod]
  })
})

summarizeBtn.addEventListener("click", async () => {
  const text = inputText.value.trim()

  if (!text) {
    showState("error")
    errorMessage.textContent = "Please enter some text to summarize"
    return
  }

  showState("loading")

  try {
    const response = await fetch("/api/summarize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        ratio: summaryRatio.value,
        method: currentMethod,
      }),
    })

    const data = await response.json()

    if (data.success) {
      displayResults(data)
    } else {
      showState("error")
      errorMessage.textContent = data.message || "Error generating summary"
    }
  } catch (error) {
    showState("error")
    errorMessage.textContent = "Failed to connect to server. Please check your connection."
  }
})

function displayResults(data) {
  summaryText.textContent = data.summary
  document.getElementById("statOriginal").textContent = data.original_length
  document.getElementById("statSummary").textContent = data.summary_length
  document.getElementById("statCompression").textContent = data.compression_ratio

  if (data.keywords) {
    const keywordsList = document.getElementById("keywordsList")
    keywordsList.innerHTML = data.keywords.map((keyword) => `<span class="keyword-tag">${keyword}</span>`).join("")
    document.getElementById("metricsContainer").classList.remove("hidden")
  }

  if (data.readability) {
    const readability = data.readability
    const metricsHTML = `
      <div class="metric-item">
        <div class="metric-label">Avg Words/Sent</div>
        <div class="metric-value">${readability.avg_words_per_sentence}</div>
      </div>
      <div class="metric-item">
        <div class="metric-label">Avg Chars/Word</div>
        <div class="metric-value">${readability.avg_chars_per_word}</div>
      </div>
      <div class="metric-item">
        <div class="metric-label">Reading Grade</div>
        <div class="metric-value">${readability.flesch_kincaid_grade}</div>
      </div>
      <div class="metric-item">
        <div class="metric-label">Reading Time</div>
        <div class="metric-value">${readability.reading_time_minutes} min</div>
      </div>
    `
    document.getElementById("readabilityMetrics").innerHTML = metricsHTML
  }

  showState("results")
}

document.getElementById("copyBtn").addEventListener("click", function () {
  const text = summaryText.textContent
  navigator.clipboard.writeText(text).then(() => {
    const btnText = this.querySelector(".btn-text")
    const btnFeedback = this.querySelector(".btn-feedback")

    btnText.classList.add("hide")
    btnFeedback.classList.add("show")

    setTimeout(() => {
      btnText.classList.remove("hide")
      btnFeedback.classList.remove("show")
    }, 2000)
  })
})

document.getElementById("downloadBtn").addEventListener("click", () => {
  const text = summaryText.textContent
  const element = document.createElement("a")
  element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(text))
  element.setAttribute("download", `summary-${new Date().toISOString().slice(0, 10)}.txt`)
  element.style.display = "none"
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
})

document.getElementById("clearBtn").addEventListener("click", () => {
  inputText.value = ""
  updateStats()
  showState("empty")
})

analyticsBtn.addEventListener("click", () => {
  loadAnalytics()
  analyticsModal.classList.remove("hidden")
})

closeAnalyticsBtn.addEventListener("click", () => {
  analyticsModal.classList.add("hidden")
})

analyticsModal.addEventListener("click", (e) => {
  if (e.target === analyticsModal) {
    analyticsModal.classList.add("hidden")
  }
})

async function loadAnalytics() {
  try {
    const response = await fetch("/api/analytics")
    const data = await response.json()

    if (data.success) {
      const stats = data.stats
      document.getElementById("analyticsTotalSummaries").textContent = stats.total_summaries
      document.getElementById("analyticsTotalTexts").textContent = stats.total_texts_processed
      document.getElementById("analyticsTotalGenerated").textContent = stats.total_words_generated
      document.getElementById("analyticsCompression").textContent = stats.average_compression_ratio + "%"

      // Display methods breakdown
      const methodLabels = {
        normal: "Normal",
        business_insights: "Business Insights",
        // Legacy method names (for backward compatibility - will be migrated on server)
        frequency: "Frequency",
        tfidf: "TF-IDF",
        hybrid: "Hybrid"
      }
      
      // Filter out methods with 0 counts and sort by count (descending)
      const methodsHTML = Object.entries(stats.methods_used)
        .filter(([method, count]) => count > 0) // Only show methods that have been used
        .sort((a, b) => b[1] - a[1]) // Sort by count descending
        .map(
          ([method, count]) => `
          <div class="breakdown-item">
            <div class="breakdown-label">${methodLabels[method] || method.toUpperCase().replace('_', ' ')}</div>
            <div class="breakdown-count">${count}</div>
          </div>
        `,
        )
        .join("")
      
      // If no methods have been used yet, show a message
      if (!methodsHTML) {
        document.getElementById("methodsUsed").innerHTML = '<div class="breakdown-item"><div class="breakdown-label">No methods used yet</div></div>'
      } else {
        document.getElementById("methodsUsed").innerHTML = methodsHTML
      }


    }
  } catch (error) {
    console.error("Error loading analytics:", error)
  }
}

updateStats()
showState("empty")
