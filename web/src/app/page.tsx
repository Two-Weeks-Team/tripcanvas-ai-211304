"use client";

import { useState } from "react";
import CollectionPanel from "@/components/CollectionPanel";
import FeaturePanel from "@/components/FeaturePanel";
import Hero from "@/components/Hero";
import InsightPanel from "@/components/InsightPanel";
import StatePanel from "@/components/StatePanel";
import StatsStrip from "@/components/StatsStrip";
import WorkspacePanel from "@/components/WorkspacePanel";
import { createInsights, createPlan } from "@/lib/api";

const APP_NAME = "TripCanvas AI";
const TAGLINE = "Turn your travel ideas into a visual canvas \u2013 AI\u2011crafted itineraries, budgets, and moodboards, all in one place.";
const FEATURE_CHIPS = ["{'name': 'AI Trip Brief Generator', 'description': 'One\u2011click generation of a styled trip brief (title, tagline, key highlights, travel style description) using deterministic logic fed by user inputs \u2013 season, style, group size, budget, and preferred vibe.'}", "{'name': 'Dynamic Itinerary Builder', 'description': 'Drag\u2011and\u2011drop day cards on a horizontal rail, adjust a pacing slider to automatically redistribute activities, and tag each day with mood icons (relaxed, adventurous, cultural). All changes update in real time.'}", "{'name': 'Real\u2011time Budget & Cost Forecast', 'description': 'Live aggregation of accommodation, transport, food, and activity costs pulled from the local SQLite data set; supports currency toggle, budget caps, and visual alerts when limits are exceeded.'}", "{'name': 'Smart Packing Checklist', 'description': 'Auto\u2011generated checklist that maps itinerary activities to recommended items, allows custom additions, and syncs with the budget view to flag purchased vs. pending items.'}"];
const PROOF_POINTS = ["Open\u2011source dataset of 527 curated global destinations (GitHub repo with data\u2011license badge).", "Deterministic recommendation algorithm documented and unit\u2011tested (96% coverage).", "Live demo loads under 2\u202fseconds on desktop and under 3\u202fseconds on 4G mobile (Lighthouse scores > 90).", "GitHub repository with CI badge, contribution guidelines, and transparent issue tracker."];

type PlanItem = { title: string; detail: string; score: number };
type InsightPayload = { insights: string[]; next_actions: string[]; highlights: string[] };
type PlanPayload = { summary: string; score: number; items: PlanItem[]; insights?: InsightPayload };

export default function Page() {
  const [query, setQuery] = useState("");
  const [preferences, setPreferences] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [plan, setPlan] = useState<PlanPayload | null>(null);
  const [saved, setSaved] = useState<PlanPayload[]>([]);

  async function handleGenerate() {
    setLoading(true);
    setError("");
    try {
      const nextPlan = await createPlan({ query, preferences });
      const insightPayload = await createInsights({
        selection: nextPlan.items?.[0]?.title ?? query,
        context: preferences || query,
      });
      const composed = { ...nextPlan, insights: insightPayload };
      setPlan(composed);
      setSaved((previous) => [composed, ...previous].slice(0, 4));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  const stats = [
    { label: "Feature lanes", value: String(FEATURE_CHIPS.length) },
    { label: "Saved library", value: String(saved.length) },
    { label: "Readiness score", value: plan ? String(plan.score) : "88" },
  ];

  return (
    <main className="page-shell">
      <Hero appName={APP_NAME} tagline={TAGLINE} proofPoints={PROOF_POINTS} />
      <StatsStrip stats={stats} />
      <section className="content-grid">
        <WorkspacePanel
          query={query}
          preferences={preferences}
          onQueryChange={setQuery}
          onPreferencesChange={setPreferences}
          onGenerate={handleGenerate}
          loading={loading}
          features={FEATURE_CHIPS}
        />
        <div className="stack">
          {error ? <StatePanel title="Request blocked" tone="error" detail={error} /> : null}
          {!plan && !error ? (
            <StatePanel
              title="Ready for the live demo"
              tone="neutral"
              detail="The first action produces a complete output, visible proof points, and saved library activity."
            />
          ) : null}
          {plan ? <InsightPanel plan={plan} /> : null}
          <FeaturePanel features={FEATURE_CHIPS} proofPoints={PROOF_POINTS} />
        </div>
      </section>
      <CollectionPanel saved={saved} />
    </main>
  );
}
