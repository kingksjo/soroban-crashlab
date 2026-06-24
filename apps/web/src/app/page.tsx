"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { FuzzingRun } from "./types";

function DashboardContent() {
  const [runs, setRuns] = useState<FuzzingRun[]>([]);
  const [dataState, setDataState] = useState<"loading" | "error" | "success">("loading");

  useEffect(() => {
    let cancelled = false;
    const ctrl = new AbortController();
    const load = async () => {
      setDataState("loading");
      try {
        const res = await fetch("/api/runs", { signal: ctrl.signal });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) {
          setRuns(data.runs ?? []);
          setDataState("success");
        }
      } catch {
        if (!cancelled) setDataState("error");
      }
    };
    void load();
    return () => {
      cancelled = true;
      ctrl.abort();
    };
  }, [fetchAttempt, demoLoading]);

  // Re-fetch data when the page becomes visible again (e.g., after navigating back).
  useEffect(() => {
    let mounted = true;
    const handleVisibility = () => {
      if (document.visibilityState === "visible" && mounted) {
        setFetchAttempt(prev => prev + 1);
      }
    };
    const handleFocus = () => {
      if (mounted) setFetchAttempt(prev => prev + 1);
    };
    document.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("focus", handleFocus);
    return () => {
      mounted = false;
      document.removeEventListener("visibilitychange", handleVisibility);
      window.removeEventListener("focus", handleFocus);
    };
  }, []);

  useEffect(() => {
    if (selectedRunId && !selectedRun) {
      setQueryState({ run: null });
    }
  }, [selectedRun, selectedRunId, setQueryState]);

  useEffect(() => {
    if (currentPage !== clampedPage) {
      setQueryState({ page: clampedPage === 1 ? null : String(clampedPage) });
    }
  }, [clampedPage, currentPage, setQueryState]);

  useEffect(() => {
    if (reportRunId && !reportRun) {
      const run = runs.find(r => r.id === reportRunId);
      if (run) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setReportRun(run);
      } else if (dataState === "success") {
        // Clear param if run not found after data loaded
        setQueryState({ report: null });
      }
    }
  }, [reportRun, reportRunId, runs, dataState, setQueryState]);

  const handleOpenRunDrawer = useCallback(
    (runId: string) => setQueryState({ run: runId, report: null }),
    [setQueryState],
  );

  const handleCloseRunDrawer = useCallback(
    () => setQueryState({ run: null }),
    [setQueryState],
  );

  const handleOpenReport = useCallback(
    (run: FuzzingRun) => {
      setReportRun(run);
      setQueryState({ report: run.id, run: null });
    },
    [setQueryState],
  );

  const handleCloseReport = useCallback(
    () => {
      setReportRun(null);
      setQueryState({ report: null });
    },
    [setQueryState],
  );

  const handleReplayComplete = useCallback(
    (data: FuzzingRun | { id: string; status: "running" }) => {
      let newRun: FuzzingRun;
      if ("area" in data) {
        newRun = data;
      } else {
        newRun = {
          id: data.id,
          status: "running",
          area: "state",
          severity: "medium",
          duration: 0,
          seedCount: 0,
          crashDetail: null,
          cpuInstructions: 0,
          memoryBytes: 0,
          minResourceFee: 0,
        };
      }
      setRuns((prev) => [newRun, ...prev]);
    },
    [],
  );

  const handlePageChange = useCallback(
    (page: number) => {
      setQueryState({ page: page <= 1 ? null : String(page) });
      cardsContainerRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    },
    [setQueryState],
  );

  const handleLaunchCampaign = useCallback((config: CampaignConfig) => {
    console.log("Launching campaign with config:", config);
    setShowCampaignConfig(false);
    // Simulate campaign launch by adding a new running run
    const newRun: FuzzingRun = {
      id: `run-${Date.now().toString().slice(-4)}`,
      status: "running",
      area: "state",
      severity: "medium",
      duration: 0,
      seedCount: 0,
      crashDetail: null,
      cpuInstructions: 0,
      memoryBytes: 0,
      minResourceFee: 0,
    };
    setRuns((prev) => [newRun, ...prev]);
  }, []);

  const handleCopyPermalink = useCallback(async () => {
    try {
      const stableQuery = toStableQueryString(
        new URLSearchParams(searchParams.toString()),
      );
      const permalink = `${window.location.origin}${pathname}${stableQuery ? `?${stableQuery}` : ""}`;
      await navigator.clipboard.writeText(permalink);
      setCopyState("copied");
    } catch {
      setCopyState("failed");
    }
  }, [pathname, searchParams]);

  const handleDashboardFiltersChange = useCallback((filters: DashboardFilters) => {
    setDashboardFilters(filters);
    setQueryState({ page: null });
  }, [setQueryState]);

  const handleDashboardFiltersReset = useCallback(() => {
    setDashboardFilters({
      status: [],
      area: [],
      severity: [],
      dateRange: { start: '', end: '' },
      durationRange: { min: 0, max: 0 },
      resourceFeeRange: { min: 0, max: 0 },
      hasCrash: null,
      searchTerm: '',
    });
    setQueryState({ page: null });
  }, [setQueryState]);

  useEffect(() => {
    if (copyState === "idle") return;
    const timer = window.setTimeout(() => setCopyState("idle"), 1800);
    return () => window.clearTimeout(timer);
  }, [copyState]);

  const cards = [
    {
      title: "Intelligent Mutation",
      description:
        "Automatically mutate transaction envelopes and inputs to explore complex state transitions specific to Soroban.",
      icon: "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z",
      color: "blue",
      details:
        "Our intelligent mutation engine uses advanced algorithms to systematically explore the state space of your Soroban contracts. It generates meaningful test cases by mutating transaction parameters, account states, and contract inputs in ways that are likely to expose edge cases and vulnerabilities.",
    },
    {
      title: "Invariant Testing",
      description:
        "Define robust invariants and property assertions. We run permutations to ensure they hold up under stress.",
      icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
      color: "purple",
      details:
        "Property-based testing for Soroban contracts. Define invariants that should always hold true, and our fuzzer will attempt to break them through millions of randomized test cases. When an invariant is violated, we provide a minimal reproducible example.",
    },
    {
      title: "Actionable Reports",
      description:
        "Get actionable, detailed execution traces when our fuzzer detects a crash, panic, or invariant breach.",
      icon: "M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
      color: "green",
      details:
        "When issues are found, CrashLab generates comprehensive reports including full execution traces, contract state at the time of failure, and suggested fixes. Reports are formatted for easy integration into your CI/CD pipeline.",
    },
  ];

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const runDrawerOpen = Boolean(searchParams.get("run"));
      if (runDrawerOpen && e.key === "Escape") {
        e.preventDefault();
        handleCloseRunDrawer();
        return;
      }
      if (showDetailView && e.key !== "Escape") return;

      switch (e.key) {
        case "ArrowDown":
        case "ArrowRight":
          e.preventDefault();
          setSelectedCardIndex((prev) => (prev + 1) % cards.length);
          break;
        case "ArrowUp":
        case "ArrowLeft":
          e.preventDefault();
          setSelectedCardIndex(
            (prev) => (prev - 1 + cards.length) % cards.length,
          );
          break;
        case "Enter":
          e.preventDefault();
          setShowDetailView(true);
          break;
        case "Escape":
          e.preventDefault();
          if (showDetailView) {
            setShowDetailView(false);
          }
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [showDetailView, cards.length, searchParams, handleCloseRunDrawer]);

  const handleCardClick = (index: number) => {
    setSelectedCardIndex(index);
    setShowDetailView(true);
  };

  const handleOpenOnboardingChecklist = useCallback(() => {
    setShowOnboardingChecklist(true);
    try {
      localStorage.setItem(ONBOARDING_SEEN_STORAGE_KEY, "true");
      localStorage.setItem(ONBOARDING_DISMISSED_STORAGE_KEY, "false");
    } catch {
      // ignore storage write errors
    }
  }, []);

  const handleCloseOnboardingChecklist = useCallback(() => {
    setShowOnboardingChecklist(false);
    try {
      localStorage.setItem(ONBOARDING_DISMISSED_STORAGE_KEY, "true");
    } catch {
      // ignore storage write errors
    }
  }, []);

  return (
    <div className="container-full page-padding fade-in">
      <div className="flex items-center justify-between mb-4 sm:mb-6">
        <div>
          <h1 className="heading-page">Dashboard</h1>
          <p className="text-meta mt-0.5 sm:mt-1">Fuzzing campaign overview</p>
        </div>
        <Link href="/runs" className="btn-primary text-xs sm:text-sm px-3 sm:px-6 h-9 sm:h-10">
          <span className="hidden sm:inline">View All Runs</span>
          <span className="sm:hidden">Runs</span>
          <span className="text-sm">→</span>
        </Link>
      </div>

      {dataState === "error" && (
        <div className="card card-padding mb-4 sm:mb-6" style={{ borderLeft: '4px solid #CC1016' }}>
          <div className="flex items-center gap-3">
            <span className="text-lg">⚠</span>
            <div>
              <p className="font-semibold" style={{ color: '#CC1016' }}>Connection Error</p>
              <p className="text-meta">Could not reach the backend API.</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-5 gap-2 sm:gap-4 mb-6 sm:mb-8">
        {[
          { label: 'Total Runs', value: dataState === "loading" ? '...' : totalRuns, color: 'var(--text-primary)' },
          { label: 'Running', value: dataState === "loading" ? '...' : runningRuns, color: '#0A66C2' },
          { label: 'Completed', value: dataState === "loading" ? '...' : completedRuns, color: '#057642' },
          { label: 'Failed', value: dataState === "loading" ? '...' : failedRuns, color: '#CC1016' },
          { label: 'Critical', value: dataState === "loading" ? '...' : criticalRuns, color: '#C37D16' },
        ].map((stat) => (
          <div key={stat.label} className="card card-padding stat-card" style={{ padding: '12px 8px' }}>
            <div className="stat-value" style={{ color: stat.color, fontSize: 'clamp(18px, 4vw, 24px)' }}>{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>

      {dataState === "loading" && (
        <div className="card card-padding flex items-center justify-center py-8 sm:py-12">
          <div className="flex items-center gap-3">
          <div className="w-5 h-5 rounded-full border-2 border-t-transparent animate-spin" style={{ borderColor: '#0A66C2', borderTopColor: 'transparent' }} />
          <span className="text-meta">Loading data...</span>
          </div>
        </div>
      )}

      {dataState === "success" && (
        <>
          <div className="section">
            <div className="flex items-center justify-between mb-3 sm:mb-4">
              <h2 className="heading-section">Recent Runs</h2>
              <Link href="/runs" className="link text-xs sm:text-sm">View all</Link>
            </div>
            <div className="card table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Area</th>
                    <th className="hidden sm:table-cell">Severity</th>
                    <th className="hidden sm:table-cell">Duration</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {recentRuns.map((run) => (
                    <tr key={run.id}>
                      <td className="code-text text-meta">{run.id}</td>
                      <td><span className={`badge badge-${run.status}`}>{run.status}</span></td>
                      <td>{run.area}</td>
                      <td className="hidden sm:table-cell" style={{ color: run.severity === 'critical' ? '#C37D16' : 'var(--text-primary)' }}>{run.severity}</td>
                      <td className="hidden sm:table-cell text-meta">{run.duration.toLocaleString()}ms</td>
                      <td><Link href={`/runs/${run.id}`} className="link text-xs sm:text-sm">View</Link></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4 section">
            <div className="card card-padding">
              <h3 className="font-semibold text-xs sm:text-sm mb-3 sm:mb-4" style={{ color: 'var(--text-secondary)' }}>Quick Actions</h3>
              <div className="flex flex-col gap-1 sm:gap-2">
                {[
                  { href: '/runs', label: 'Browse all runs' },
                  { href: '/analytics', label: 'View analytics and charts' },
                  { href: '/triage', label: 'Failure triage board' },
                  { href: '/integrations', label: 'Manage integrations' },
                ].map((action) => (
                  <Link key={action.href} href={action.href} className="btn-ghost justify-between text-xs sm:text-sm rounded-lg" style={{ height: 'auto', padding: '8px 10px sm:10px 12px' }}>
                    <span>{action.label}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>→</span>
                  </Link>
                ))}
              </div>
            </div>
            <div className="card card-padding">
              <h3 className="font-semibold text-xs sm:text-sm mb-3 sm:mb-4" style={{ color: 'var(--text-secondary)' }}>System Status</h3>
              <div className="space-y-2 sm:space-y-3">
                {[
                  { label: 'Backend Status', value: dataState === "success" ? 'Online' : 'Offline', color: dataState === "success" ? '#057642' : '#CC1016' },
                  { label: 'Data Source', value: process.env.NEXT_PUBLIC_API_URL ? 'Remote API' : 'Mock Data' },
                  { label: 'Environment', value: process.env.NEXT_PUBLIC_VERCEL_ENV || 'Development' },
                  { label: 'Smart Contract', value: 'Compiled to WASM (7.4KB)' },
                ].map((info) => (
                  <div key={info.label} className="flex justify-between items-center py-0.5 sm:py-1">
                    <span className="text-meta">{info.label}</span>
                    <span className="text-xs sm:text-sm font-medium" style={{ color: info.color || 'var(--text-primary)' }}>{info.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default function Home() {
  return (
    <Suspense fallback={
      <div className="container-full page-padding flex items-center justify-center min-h-[50vh]">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 rounded-full border-2 border-t-transparent animate-spin" style={{ borderColor: '#0A66C2', borderTopColor: 'transparent' }} />
          <span className="text-meta">Loading...</span>
        </div>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
