
import { useState, useEffect } from "react";

import {
  LayoutDashboard,
  FolderKanban,
  Play,
  History,
  Settings,
  Search,
  Bell,
  Plus,
  CheckCircle2,
  XCircle,
  Clock,
  Activity,
  ArrowUpRight,
  Terminal,
  ChevronRight,
  Code2,
  Sparkles,
  Menu
} from "lucide-react";

import {
  getProjects,
  registerProject,
  executeTests,
  submitApproval
} from "./api";

import "./App.css";

function App() {
  // NAVIGATION
  const [activePage, setActivePage] = useState("Overview");

  // PROJECT STATES
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [projectPath, setProjectPath] = useState("");
  const [search, setSearch] = useState("");
  const [saving, setSaving] = useState(false);

  // EXECUTION STATES
  const [selectedProject, setSelectedProject] = useState("");
  const [running, setRunning] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [executionError, setExecutionError] = useState("");

  // APPROVAL STATES
  const [approving, setApproving] = useState(false);
  const [approvalMessage, setApprovalMessage] = useState("");

  // FETCH PROJECTS FROM BACKEND
  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getProjects();

      setProjects(
        data.map((project) => ({
          ...project,
          language: project.default_language || "Python",
          status: "Registered"
        }))
      );

    } catch (err) {
      console.error("Project fetching error:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to load projects. Check backend connection."
      );

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // REGISTER PROJECT
  const addProject = async (e) => {
    e.preventDefault();

    if (!projectName.trim() || !projectPath.trim()) {
      return;
    }

    try {
      setSaving(true);
      setError("");

      await registerProject({
        name: projectName.trim(),
        path: projectPath.trim(),
        default_language: "python"
      });

      setProjectName("");
      setProjectPath("");
      setShowForm(false);

      await fetchProjects();

    } catch (err) {
      console.error("Project registration error:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to register project."
      );

    } finally {
      setSaving(false);
    }
  };

  // RUN TESTS
  const runTests = async () => {
    if (!selectedProject) {
      setExecutionError("Please select a project first.");
      return;
    }

    try {
      setRunning(true);
      setExecutionError("");
      setExecutionResult(null);
      setApprovalMessage("");

      const result = await executeTests(
        Number(selectedProject),
        "python"
      );

      console.log("Execution response:", result);

      setExecutionResult(result);

    } catch (err) {
      console.error("Execution error:", err);

      setExecutionError(
        err.response?.data?.detail ||
        "Test execution failed. Check the backend terminal."
      );

    } finally {
      setRunning(false);
    }
  };

  // APPROVE OR REJECT AI FIX
  const handleApproval = async (approved) => {
    const threadId = executionResult?.thread_id;

    if (!threadId) {
      setApprovalMessage("Execution thread ID is missing.");
      return;
    }

    try {
      setApproving(true);
      setApprovalMessage("");

      const result = await submitApproval(
        threadId,
        Number(selectedProject),
        approved
      );

      setExecutionResult((previous) => ({
        ...previous,
        ...result
      }));

      setApprovalMessage(
        approved
          ? "Approval submitted successfully."
          : "Fix rejection submitted successfully."
      );

    } catch (err) {
      console.error("Approval error:", err);

      setApprovalMessage(
        err.response?.data?.detail ||
        "Unable to submit approval decision."
      );

    } finally {
      setApproving(false);
    }
  };

  // NAVIGATION ITEMS
  const navigation = [
    { label: "Overview", icon: LayoutDashboard },
    { label: "Projects", icon: FolderKanban },
    { label: "Run Tests", icon: Play },
    { label: "History", icon: History },
    { label: "Settings", icon: Settings },
  ];

  // DASHBOARD STATISTICS
  const stats = [
    {
      label: "Total Projects",
      value: projects.length,
      icon: FolderKanban,
      color: "purple",
      note: "Registered projects"
    },
    {
      label: "Total Executions",
      value: "—",
      icon: Activity,
      color: "blue",
      note: "History integration pending"
    },
    {
      label: "Tests Passed",
      value: "—",
      icon: CheckCircle2,
      color: "green",
      note: "History integration pending"
    },
    {
      label: "Tests Failed",
      value: "—",
      icon: XCircle,
      color: "red",
      note: "History integration pending"
    },
  ];

  // FILTER PROJECTS
  const filteredProjects = projects.filter((project) =>
    project.name.toLowerCase().includes(search.toLowerCase())
  );

  // EXECUTION STATUS
  const approvalRequired =
    executionResult?.status === "APPROVAL_REQUIRED";

  const executionFinished =
    executionResult?.status === "COMPLETED" ||
    executionResult?.status === "FIX_VERIFIED" ||
    executionResult?.status === "FIX_REJECTED" ||
    executionResult?.final_status === "FIX_VERIFIED" ||
    executionResult?.final_status === "FIX_REJECTED";

  return (
    <div className="app-shell">

      {/* SIDEBAR */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">
            <Code2 size={24} />
          </div>

          <div>
            <h2>TestPilot<span> AI</span></h2>
            <p>INTELLIGENT TEST AUTOMATION</p>
          </div>
        </div>

        <div className="workspace">
          <span className="online-dot"></span>
          WORKSPACE ONLINE
        </div>

        <p className="nav-heading">WORKSPACE</p>

        <nav>
          {navigation.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-link ${
                activePage === label ? "active" : ""
              }`}
              onClick={() => setActivePage(label)}
            >
              <Icon size={19} />
              <span>{label}</span>

              {activePage === label && (
                <ChevronRight size={16} />
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">

          <div className="ai-card">
            <Sparkles size={20} />

            <h4>AI Repair Engine</h4>

            <p>
              Intelligent failure analysis and automated code repair.
            </p>

            <span><i></i> Engine ready</span>
          </div>

          <div className="profile">
            <div className="avatar">TP</div>

            <div>
              <strong>TestPilot Admin</strong>
              <small>Developer workspace</small>
            </div>
          </div>

        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">

        {/* TOPBAR */}
        <header className="topbar">

          <div className="breadcrumb">
            <Menu className="mobile-menu" size={21} />
            Workspace
            <span>/</span>
            <strong>{activePage}</strong>
          </div>

          <div className="top-actions">

            <div className="api-status">
              <i></i> Backend connected
            </div>

            <button className="icon-button">
              <Bell size={19} />
            </button>

          </div>
        </header>

        <div className="page-content">

          {/* WELCOME */}
          <section className="welcome">

            <div>
              <div className="eyebrow">
                <Sparkles size={14} />
                AI-POWERED TEST AUTOMATION
              </div>

              <h1>
                {activePage === "Overview"
                  ? "Testing, made intelligent."
                  : activePage}
              </h1>

              <p>
                Monitor your projects, execute tests and repair failures with AI.
              </p>
            </div>

            <button
              className="primary-button"
              onClick={() => setActivePage("Run Tests")}
            >
              <Play size={17} fill="currentColor" />
              Run new tests
            </button>

          </section>

          {/* GLOBAL ERROR */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* OVERVIEW */}
          {activePage === "Overview" && (
            <>

              <section className="stats-grid">

                {stats.map(({ label, value, icon: Icon, color, note }) => (
                  <article className="stat-card" key={label}>

                    <div className={`stat-icon ${color}`}>
                      <Icon size={21} />
                    </div>

                    <p>{label}</p>
                    <h2>{value}</h2>
                    <small>{note}</small>

                  </article>
                ))}

              </section>

              <section className="content-grid">

                {/* PROJECTS */}
                <article className="panel project-panel">

                  <div className="panel-header">

                    <div>
                      <h3>Recent Projects</h3>
                      <p>Your registered test projects</p>
                    </div>

                    <button
                      className="text-button"
                      onClick={() => setActivePage("Projects")}
                    >
                      View all <ArrowUpRight size={15} />
                    </button>

                  </div>

                  {loading ? (
                    <p className="empty-message">Loading projects...</p>
                  ) : projects.length === 0 ? (
                    <p className="empty-message">No projects registered yet.</p>
                  ) : (
                    projects.slice(0, 4).map((project) => (

                      <div className="project-row" key={project.id}>

                        <div className="project-symbol">
                          <Code2 size={20} />
                        </div>

                        <div className="project-info">
                          <strong>{project.name}</strong>
                          <small>
                            {project.language} · {project.path}
                          </small>
                        </div>

                        <span className="status-pill">
                          <i></i>
                          {project.status}
                        </span>

                      </div>

                    ))
                  )}

                </article>

                {/* SYSTEM STATUS */}
                <article className="panel activity-panel">

                  <div className="panel-header">
                    <div>
                      <h3>System Status</h3>
                      <p>Platform health overview</p>
                    </div>

                    <Activity size={19} className="muted-icon" />
                  </div>

                  <div className="system-item">
                    <span>FastAPI Backend</span>
                    <strong className="healthy">Online</strong>
                  </div>

                  <div className="system-item">
                    <span>PostgreSQL</span>
                    <strong className="healthy">Connected</strong>
                  </div>

                  <div className="system-item">
                    <span>AI Repair Engine</span>
                    <strong className="healthy">Ready</strong>
                  </div>

                  <div className="system-item">
                    <span>Test Runner</span>
                    <strong className="healthy">Available</strong>
                  </div>

                  <div className="system-footer">
                    <CheckCircle2 size={16} />
                    Core services configured
                  </div>

                </article>

              </section>

              {/* RECENT EXECUTIONS */}
              <section className="panel execution-panel">

                <div className="panel-header">

                  <div>
                    <h3>Recent Executions</h3>
                    <p>Latest test activity across your workspace</p>
                  </div>

                  <button
                    className="text-button"
                    onClick={() => setActivePage("History")}
                  >
                    View history <ArrowUpRight size={15} />
                  </button>

                </div>

                <div className="empty-state">

                  <div>
                    <Terminal size={25} />
                  </div>

                  <strong>Ready for your next test run</strong>

                  <p>Your execution history will appear here.</p>

                  <button
                    className="secondary-button"
                    onClick={() => setActivePage("Run Tests")}
                  >
                    Start testing
                  </button>

                </div>

              </section>

            </>
          )}

          {/* PROJECTS PAGE */}
          {activePage === "Projects" && (

            <section className="panel">

              <div className="panel-header">

                <div>
                  <h3>Project Management</h3>
                  <p>Manage your registered codebases</p>
                </div>

                <button
                  className="primary-button"
                  onClick={() => setShowForm(!showForm)}
                >
                  <Plus size={17} />
                  Add project
                </button>

              </div>

              {showForm && (

                <form className="project-form" onSubmit={addProject}>

                  <label>
                    Project name

                    <input
                      value={projectName}
                      onChange={(e) => setProjectName(e.target.value)}
                      placeholder="Enter project name"
                      required
                    />
                  </label>

                  <label>
                    Project path

                    <input
                      value={projectPath}
                      onChange={(e) => setProjectPath(e.target.value)}
                      placeholder="/home/kashvi/automation/my_project"
                      required
                    />
                  </label>

                  <button
                    className="primary-button"
                    type="submit"
                    disabled={saving}
                  >
                    {saving ? "Registering..." : "Add project"}
                  </button>

                </form>

              )}

              <div className="search-box">
                <Search size={18} />

                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search projects..."
                />
              </div>

              {loading ? (
                <p className="empty-message">Loading projects...</p>
              ) : filteredProjects.length === 0 ? (
                <p className="empty-message">No projects found.</p>
              ) : (
                filteredProjects.map((project) => (

                  <div className="project-row" key={project.id}>

                    <div className="project-symbol">
                      <Code2 size={20} />
                    </div>

                    <div className="project-info">
                      <strong>{project.name}</strong>
                      <small>{project.path}</small>
                    </div>

                    <span className="status-pill">
                      <i></i>
                      {project.status}
                    </span>

                  </div>

                ))
              )}

            </section>

          )}

          {/* RUN TESTS PAGE */}
          {activePage === "Run Tests" && (

            <section className="panel run-panel">

              <div className="panel-header">

                <div>
                  <h3>Test Execution</h3>
                  <p>Select a project and launch automated tests</p>
                </div>

                <Play size={22} className="muted-icon" />

              </div>

              <div className="project-form">

                <label>
                  Select Project

                  <select
                    value={selectedProject}
                    onChange={(e) => {
                      setSelectedProject(e.target.value);
                      setExecutionResult(null);
                      setExecutionError("");
                      setApprovalMessage("");
                    }}
                  >
                    <option value="">Choose a registered project</option>

                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.name}
                      </option>
                    ))}

                  </select>
                </label>

                <label>
                  Language
                  <input value="Python" disabled />
                </label>

                <button
                  className="primary-button"
                  onClick={runTests}
                  disabled={running || loading || !selectedProject}
                >
                  <Play size={16} />

                  {running ? "Running tests..." : "Run Tests"}
                </button>

              </div>

              {executionError && (
                <div className="error-message">
                  {executionError}
                </div>
              )}

              {executionResult && (

                <div className="execution-results">

                  <div className="panel-header">
                    <div>
                      <h3>Execution Results</h3>
                      <p>{executionResult.message || "Test execution response"}</p>
                    </div>
                  </div>

                  <p>
                    Status: <strong>
                      {executionResult.status ||
                       executionResult.final_status ||
                       "Unknown"}
                    </strong>
                  </p>

                  <div className="stats-grid">

                    <article className="stat-card">
                      <div className="stat-icon green">
                        <CheckCircle2 size={20} />
                      </div>
                      <p>Passed</p>
                      <h2>{executionResult.passed ?? 0}</h2>
                    </article>

                    <article className="stat-card">
                      <div className="stat-icon red">
                        <XCircle size={20} />
                      </div>
                      <p>Failed</p>
                      <h2>{executionResult.failed ?? 0}</h2>
                    </article>

                    <article className="stat-card">
                      <div className="stat-icon blue">
                        <Clock size={20} />
                      </div>
                      <p>Skipped</p>
                      <h2>{executionResult.skipped ?? 0}</h2>
                    </article>

                  </div>

                  {executionResult.duration != null && (
                    <p>
                      Duration: {Number(executionResult.duration).toFixed(2)} seconds
                    </p>
                  )}

                  {executionResult.thread_id && (
                    <p>
                      Execution ID: {executionResult.thread_id}
                    </p>
                  )}

                  {approvalRequired && (

                    <div className="panel approval-panel">

                      <h3>AI Fix Requires Approval</h3>

                      <p>
                        The AI has investigated the failure and is waiting
                        for your decision before applying its proposed fix.
                      </p>

                      {executionResult.proposed_fix && (
                        <pre>
                          {JSON.stringify(
                            executionResult.proposed_fix,
                            null,
                            2
                          )}
                        </pre>
                      )}

                      <div className="approval-actions">

                        <button
                          className="primary-button"
                          onClick={() => handleApproval(true)}
                          disabled={approving}
                        >
                          {approving ? "Submitting..." : "Approve Fix"}
                        </button>

                        <button
                          className="secondary-button"
                          onClick={() => handleApproval(false)}
                          disabled={approving}
                        >
                          Reject Fix
                        </button>

                      </div>

                      {approvalMessage && (
                        <p>{approvalMessage}</p>
                      )}

                    </div>

                  )}

                  {executionFinished && (
                    <div className="system-footer">
                      <CheckCircle2 size={17} />
                      Execution workflow finished.
                    </div>
                  )}

                </div>

              )}

            </section>

          )}

          {/* HISTORY PAGE */}
          {activePage === "History" && (

            <section className="panel">

              <div className="panel-header">
                <div>
                  <h3>Execution History</h3>
                  <p>Review previous test runs and outcomes</p>
                </div>

                <History size={21} className="muted-icon" />
              </div>

              <div className="empty-state">

                <div>
                  <Clock size={25} />
                </div>

                <strong>History integration pending</strong>

                <p>
                  We'll connect this page to your PostgreSQL history API next.
                </p>

              </div>

            </section>

          )}

          {/* SETTINGS PAGE */}
          {activePage === "Settings" && (

            <section className="panel">

              <h3>Settings</h3>

              <p className="muted-text">
                Backend: http://localhost:8000
              </p>

              <p className="muted-text">
                Frontend: http://localhost:5173
              </p>

            </section>

          )}

        </div>

      </main>

    </div>
  );
}

export default App;
