function ShieldIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="feature-icon-svg"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
    >
      <path d="M12 3L19 6V11C19 16 15.7 19.4 12 21C8.3 19.4 5 16 5 11V6L12 3Z" />

      <path d="M9 12L11 14L15 10" />
    </svg>
  );
}

function ChartIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="feature-icon-svg"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M5 19V12" />
      <path d="M10 19V8" />
      <path d="M15 19V5" />
      <path d="M20 19V10" />
    </svg>
  );
}

function RiskDashboardIllustration() {
  return (
    <div className="risk-illustration">
      <div className="illustration-glow" />

      <div className="illustration-orbit">
        <span className="orbit-dot orbit-dot-one" />
        <span className="orbit-dot orbit-dot-two" />
        <span className="orbit-dot orbit-dot-three" />
      </div>

      <div className="dashboard-window">
        <div className="dashboard-top">
          <div className="dashboard-dots">
            <span />
            <span />
            <span />
          </div>

          <div className="dashboard-title-line" />
        </div>

        <div className="dashboard-content">
          <div className="chart-area">
            <div className="chart-line" />

            <div className="chart-bars">
              <span className="bar bar-one" />
              <span className="bar bar-two" />
              <span className="bar bar-three" />
              <span className="bar bar-four" />
              <span className="bar bar-five" />
            </div>
          </div>

          <div className="donut-chart">
            <div className="donut-inner" />
          </div>
        </div>
      </div>

      <div className="dashboard-layer" />

      <div className="illustration-shield">
        <svg viewBox="0 0 100 120" fill="none">
          <path
            d="M50 5L91 21V54C91 82 72 103 50 115C28 103 9 82 9 54V21L50 5Z"
            fill="url(#shieldGradient)"
            stroke="#d9d0ff"
            strokeWidth="2"
          />

          <path
            d="M31 59L43 71L70 43"
            stroke="white"
            strokeWidth="7"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          <defs>
            <linearGradient
              id="shieldGradient"
              x1="20"
              y1="20"
              x2="80"
              y2="100"
            >
              <stop offset="0%" stopColor="#a895ff" />
              <stop offset="100%" stopColor="#5d3bea" />
            </linearGradient>
          </defs>
        </svg>
      </div>
    </div>
  );
}

function Feature({
  icon,
  title,
  description,
}: {
  icon: "shield" | "chart";
  title: string;
  description: string;
}) {
  return (
    <div className="risk-feature">
      <div className="risk-feature-icon">
        {icon === "shield" ? <ShieldIcon /> : <ChartIcon />}
      </div>
      <div>
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function RiskEnginePanel() {
  return (
    <section className="risk-panel">
      <div className="risk-background-circle circle-one" />
      <div className="risk-background-circle circle-two" />
      <div className="risk-background-curve" />
      <div className="risk-panel-content">
        <div className="risk-eyebrow">AI-POWERED AML & KYC</div>
        <h2>Risk Scoring Engine</h2>
        <p className="risk-description">
          Smarter risk detection. Better decisions.
          <br />A safer tomorrow.
        </p>
        <div className="risk-features">
          <Feature
            icon="shield"
            title="Detect Suspicious Activity"
            description={
              "Identify high-risk customers with AI-driven analytics."
            }
          />
          <Feature
            icon="chart"
            title="Automate Compliance"
            description={"Reduce manual effort with intelligent workflows."}
          />
          <Feature
            icon="shield"
            title="Enhance Fraud Detection"
            description={"Protect your business with real-time risk scoring."}
          />
        </div>
      </div>
      <RiskDashboardIllustration />
    </section>
  );
}
